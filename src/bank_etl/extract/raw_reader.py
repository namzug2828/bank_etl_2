import logging

import pandas as pd

from bank_etl.db import DatabaseConnection

logger = logging.getLogger(__name__)


class RawReader:
    """Lee tablas del esquema raw de Postgres."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def read(self, table: str) -> pd.DataFrame:
        df = pd.read_sql(f'SELECT * FROM raw."{table}"', self.db.engine)
        logger.info("Leído raw.%s: %s filas", table, len(df))
        return df