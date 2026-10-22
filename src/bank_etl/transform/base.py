import logging
from abc import ABC, abstractmethod

import pandas as pd


class BaseTransformer(ABC):
    """Contrato común: cada tabla hereda y solo implementa transform()."""

    source_table: str          # tabla en el esquema raw
    target_table: str          # tabla en el esquema core
    target_columns: list[str]  # columnas y orden exactos del DDL de core

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia, tipa y renombra. Recibe todo en texto, devuelve tipos finales."""

    def run(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        out = self.transform(raw_df.copy())

        missing = set(self.target_columns) - set(out.columns)
        if missing:
            raise ValueError(f"{self.target_table}: faltan columnas {sorted(missing)}")

        out = out[self.target_columns]
        if len(out) != len(raw_df):
            self.logger.warning(
                "%s: filas entrada=%s, salida=%s", self.target_table, len(raw_df), len(out)
            )
        self.logger.info("Transformado %s -> %s: %s filas",
                         self.source_table, self.target_table, len(out))
        return out