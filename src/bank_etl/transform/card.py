import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import map_values, parse_yymmdd, to_number


class CardTransformer(BaseTransformer):
    source_table = "card"
    target_table = "card"
    target_columns = ["card_id", "disp_id", "card_type", "issued_date"]

    CARD_TYPE = {"classic": "CLASSIC", "junior": "JUNIOR", "gold": "GOLD"}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for c in ["card_id", "disp_id"]:
            df[c] = to_number(df[c], f"card.{c}").astype("Int64")
        df["card_type"] = map_values(df["type"], self.CARD_TYPE, "card.type")
        df["issued_date"] = parse_yymmdd(df["issued"], "card.issued_date")  # '931107 00:00:00'
        return df