import logging

from bank_etl.config import Settings
from bank_etl.db import DatabaseConnection
from bank_etl.extract.raw_reader import RawReader
from bank_etl.load.core_loader import CoreLoader
from bank_etl.transform.registry import TRANSFORMERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    db = DatabaseConnection(Settings.from_env())
    db.check()

    reader = RawReader(db)
    loader = CoreLoader(db)

    for transformer_cls in TRANSFORMERS:
        transformer = transformer_cls()
        raw_df = reader.read(transformer.source_table)
        core_df = transformer.run(raw_df)
        loader.load(transformer.target_table, core_df)


if __name__ == "__main__":
    main()