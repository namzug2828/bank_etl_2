import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import map_values, to_number


class DispTransformer(BaseTransformer):
    source_table = "disp"
    target_table = "disp"
    target_columns = ["disp_id", "client_id", "account_id", "disp_type"]

    DISP_TYPE = {"OWNER": "OWNER", "DISPONENT": "DISPONENT"}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for c in ["disp_id", "client_id", "account_id"]:
            df[c] = to_number(df[c], f"disp.{c}").astype("Int64")
        df["disp_type"] = map_values(df["type"], self.DISP_TYPE, "disp.type")
        return df
    