import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import blank_to_null, to_number


class DistrictTransformer(BaseTransformer):
    source_table = "district"
    target_table = "district"

    RENAME = {
        "A1": "district_id", "A2": "district_name", "A3": "region",
        "A4": "inhabitants",
        "A5": "municipalities_lt_499", "A6": "municipalities_500_1999",
        "A7": "municipalities_2000_9999", "A8": "municipalities_gt_10000",
        "A9": "n_cities", "A10": "urban_ratio", "A11": "avg_salary",
        "A12": "unemployment_95", "A13": "unemployment_96",
        "A14": "entrepreneurs_per_1000", "A15": "crimes_95", "A16": "crimes_96",
    }
    INT_COLS = [
        "district_id", "inhabitants", "municipalities_lt_499",
        "municipalities_500_1999", "municipalities_2000_9999",
        "municipalities_gt_10000", "n_cities", "avg_salary",
        "entrepreneurs_per_1000", "crimes_95", "crimes_96",
    ]
    DEC_COLS = ["urban_ratio", "unemployment_95", "unemployment_96"]
    TEXT_COLS = ["district_name", "region"]

    target_columns = list(RENAME.values())

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=self.RENAME)
        for c in self.TEXT_COLS:
            df[c] = blank_to_null(df[c])
        for c in self.INT_COLS:
            df[c] = to_number(df[c], f"district.{c}").astype("Int64")
        for c in self.DEC_COLS:
            df[c] = to_number(df[c], f"district.{c}")
        return df