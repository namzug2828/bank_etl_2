import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class CsvExtractor:
    """Lee los CSV de Berka como texto, sin interpretar tipos."""

    def __init__(self, directory: Path, sep: str = ";", encoding: str = "latin1"):
        self.directory = Path(directory)
        self.sep = sep
        self.encoding = encoding

    def list_tables(self) -> list[str]:
        return sorted(p.stem for p in self.directory.glob("*.csv"))

    def extract(self, table: str) -> pd.DataFrame:
        path = self.directory / f"{table}.csv"
        if not path.exists():
            raise FileNotFoundError(f"No existe {path}")

        df = pd.read_csv(
            path,
            sep=self.sep,
            encoding=self.encoding,
            dtype=str,          # raw = todo texto
            low_memory=False,
        )
        logger.info("Extraído %s: %s filas, %s columnas", table, len(df), len(df.columns))
        return df