import logging
import sys

from bank_etl.config import Settings
from bank_etl.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> int:
    ok = Pipeline(Settings.from_env()).run()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())