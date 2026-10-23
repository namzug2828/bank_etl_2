import logging

from bank_etl.audit import AuditLog
from bank_etl.config import Settings
from bank_etl.db import DatabaseConnection
from bank_etl.extract.csv_extractor import CsvExtractor
from bank_etl.extract.raw_reader import RawReader
from bank_etl.load.core_loader import CoreLoader
from bank_etl.load.raw_loader import RawLoader
from bank_etl.transform.registry import TRANSFORMERS
from bank_etl.validation.registry import build_rules
from bank_etl.validation.validator import Validator

logger = logging.getLogger(__name__)


class Pipeline:
    """CSV -> raw -> core -> validación, con registro de cada ejecución."""

    def __init__(self, settings: Settings, name: str = "berka_full_load"):
        self.settings = settings
        self.name = name
        self.db = DatabaseConnection(settings)
        self.audit = AuditLog(self.db)

    def _load_raw(self) -> None:
        extractor = CsvExtractor(self.settings.raw_data_dir)
        loader = RawLoader(self.db)
        for table in extractor.list_tables():
            loader.load(table, extractor.extract(table))

    def _load_core(self) -> None:
        reader = RawReader(self.db)
        loader = CoreLoader(self.db)
        for transformer_cls in TRANSFORMERS:
            transformer = transformer_cls()
            raw_df = reader.read(transformer.source_table)
            loader.load(transformer.target_table, transformer.run(raw_df))

    def run(self) -> bool:
        """Devuelve True si el flujo y todas las validaciones pasaron."""
        self.db.check()
        run_id = self.audit.start_run(self.name)
        logger.info("Inicia ejecución run_id=%s", run_id)
        try:
            self._load_raw()
            self._load_core()
            results = Validator(self.db, build_rules()).run()
            self.audit.save_results(run_id, results)

            failed = [r for r in results if not r.passed]
            if failed:
                names = ", ".join(f"{r.table_name}.{r.rule_name}" for r in failed)
                self.audit.finish_run(run_id, "FAILED",
                                      f"{len(failed)} reglas fallidas: {names}"[:1000])
                logger.error("Ejecución %s FAILED: %s reglas fallidas", run_id, len(failed))
                return False

            self.audit.finish_run(run_id, "SUCCESS")
            logger.info("Ejecución %s SUCCESS", run_id)
            return True
        except Exception as exc:
            logger.exception("Ejecución %s abortó", run_id)
            self.audit.finish_run(run_id, "FAILED", str(exc)[:1000])
            raise