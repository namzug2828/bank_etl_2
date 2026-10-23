import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from bank_etl.config import Settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Encapsula la conexión a PostgreSQL."""

    def __init__(self, settings: Settings):
        self._engine: Engine = create_engine(settings.db_url)

    @property
    def engine(self) -> Engine:
        return self._engine

    def execute(self, sql: str, params: dict | None = None) -> None:
        with self._engine.begin() as conn:
            conn.execute(text(sql), params or {})

    def check(self) -> bool:
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexión a PostgreSQL OK")
        return True

    def scalar(self, sql: str, params: dict | None = None):
        """Ejecuta una consulta y devuelve la primera columna de la primera fila."""
        with self._engine.begin() as conn:
            return conn.execute(text(sql), params or {}).scalar()