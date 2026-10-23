from dataclasses import asdict

from sqlalchemy import text

from bank_etl.db import DatabaseConnection
from bank_etl.validation.base import RuleResult


class AuditLog:
    """Escribe en audit.etl_run y audit.validation_result."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def start_run(self, pipeline_name: str) -> int:
        return self.db.scalar(
            "INSERT INTO audit.etl_run (pipeline_name) VALUES (:n) RETURNING run_id",
            {"n": pipeline_name},
        )

    def finish_run(self, run_id: int, status: str, error_message: str | None = None) -> None:
        self.db.execute(
            "UPDATE audit.etl_run SET finished_at = now(), status = :s, "
            "error_message = :e WHERE run_id = :r",
            {"s": status, "e": error_message, "r": run_id},
        )

    def save_results(self, run_id: int, results: list[RuleResult]) -> None:
        if not results:
            return
        rows = [{"run_id": run_id, **asdict(r)} for r in results]
        with self.db.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO audit.validation_result "
                    "(run_id, table_name, rule_name, passed, rows_checked, rows_failed, details) "
                    "VALUES (:run_id, :table_name, :rule_name, :passed, "
                    ":rows_checked, :rows_failed, :details)"
                ),
                rows,
            )