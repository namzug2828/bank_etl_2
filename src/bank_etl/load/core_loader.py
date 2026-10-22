import io
import logging

import pandas as pd

from bank_etl.db import DatabaseConnection

logger = logging.getLogger(__name__)


class CoreLoader:
    """Carga un DataFrame ya tipado a core (reemplazo completo, atómico)."""

    SCHEMA = "core"

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def load(self, table: str, df: pd.DataFrame) -> int:
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False, na_rep="", date_format="%Y-%m-%d")
        buffer.seek(0)

        columns = ", ".join(df.columns)
        conn = self.db.engine.raw_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"TRUNCATE {self.SCHEMA}.{table} CASCADE")
                cur.copy_expert(
                    f"COPY {self.SCHEMA}.{table} ({columns}) FROM STDIN WITH (FORMAT csv)",
                    buffer,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        logger.info("Cargado core.%s: %s filas", table, len(df))
        return len(df)