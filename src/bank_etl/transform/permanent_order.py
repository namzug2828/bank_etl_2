import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import (
    blank_to_null, clean_id_text, map_values, to_number,
)


class PermanentOrderTransformer(BaseTransformer):
    source_table = "order"                 # palabra reservada en SQL
    target_table = "permanent_order"
    target_columns = ["order_id", "account_id", "bank_to", "account_to",
                      "amount", "k_symbol"]

    K_SYMBOL = {
        "SIPO": "HOUSEHOLD",
        "UVER": "LOAN_PAYMENT",
        "POJISTNE": "INSURANCE",
        "LEASING": "LEASING",
    }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for c in ["order_id", "account_id"]:
            df[c] = to_number(df[c], f"order.{c}").astype("Int64")
        df["bank_to"] = blank_to_null(df["bank_to"])
        df["account_to"] = clean_id_text(df["account_to"])
        df["amount"] = to_number(df["amount"], "order.amount")
        df["k_symbol"] = map_values(df["k_symbol"], self.K_SYMBOL, "order.k_symbol")
        return df