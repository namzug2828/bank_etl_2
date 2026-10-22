import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import map_values, parse_yymmdd, to_number


class AccountTransformer(BaseTransformer):
    source_table = "account"
    target_table = "account"
    target_columns = ["account_id", "district_id", "frequency", "created_date"]

    FREQUENCY = {
        "POPLATEK MESICNE": "MONTHLY",
        "POPLATEK TYDNE": "WEEKLY",
        "POPLATEK PO OBRATU": "AFTER_TRANSACTION",
    }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df["account_id"] = to_number(df["account_id"], "account.account_id").astype("Int64")
        df["district_id"] = to_number(df["district_id"], "account.district_id").astype("Int64")
        df["frequency"] = map_values(df["frequency"], self.FREQUENCY, "account.frequency")
        df["created_date"] = parse_yymmdd(df["date"], "account.created_date")
        return df