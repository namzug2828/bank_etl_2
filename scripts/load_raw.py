import logging

from bank_etl.config import Settings
from bank_etl.db import DatabaseConnection
from bank_etl.extract.csv_extractor import CsvExtractor
from bank_etl.load.raw_loader import RawLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    settings = Settings.from_env()
    db = DatabaseConnection(settings)
    db.check()

    extractor = CsvExtractor(settings.raw_data_dir)
    loader = RawLoader(db)

    for table in extractor.list_tables():
        df = extractor.extract(table)
        loader.load(table, df)


if __name__ == "__main__":
    main()