import io
import logging

import pandas as pd

from bank_etl.db import DatabaseConnection

logger = logging.getLogger(__name__)


class RawLoader:
    """Carga DataFrames al esquema raw (tablas TEXT, reemplazo completo)."""

    SCHEMA = "raw"

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def load(self, table: str, df: pd.DataFrame) -> int:
        # 1) Crea la tabla vacía con columnas TEXT (reemplaza si existe)
        df.head(0).to_sql(
            table, self.db.engine, schema=self.SCHEMA,
            if_exists="replace", index=False,
        )

        # 2) Carga masiva con COPY
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        conn = self.db.engine.raw_connection()
        try:
            with conn.cursor() as cur:
                cur.copy_expert(
                    f'COPY {self.SCHEMA}."{table}" FROM STDIN WITH (FORMAT csv)',
                    buffer,
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        logger.info("Cargado raw.%s: %s filas", table, len(df))
        return len(df)