import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import (
    blank_to_null, clean_id_text, map_values, parse_yymmdd, to_number,
)


class TransTransformer(BaseTransformer):
    source_table = "trans"
    target_table = "trans"
    target_columns = ["trans_id", "account_id", "trans_date", "trans_type",
                      "operation", "amount", "balance", "k_symbol", "bank", "account"]

    TYPE = {"PRIJEM": "CREDIT", "VYDAJ": "DEBIT", "VYBER": "WITHDRAWAL"}
    OPERATION = {
        "VKLAD": "CASH_DEPOSIT",
        "PREVOD Z UCTU": "TRANSFER_IN",
        "VYBER": "CASH_WITHDRAWAL",
        "PREVOD NA UCET": "TRANSFER_OUT",
        "VYBER KARTOU": "CARD_WITHDRAWAL",
    }
    K_SYMBOL = {
        "POJISTNE": "INSURANCE",
        "SLUZBY": "STATEMENT_FEE",
        "UROK": "INTEREST_CREDITED",
        "SANKC. UROK": "PENALTY_INTEREST",
        "DUCHOD": "PENSION",
        "UVER": "LOAN_PAYMENT",
        "SIPO": "HOUSEHOLD",
    }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df["trans_id"] = to_number(df["trans_id"], "trans.trans_id").astype("Int64")
        df["account_id"] = to_number(df["account_id"], "trans.account_id").astype("Int64")
        df["trans_date"] = parse_yymmdd(df["date"], "trans.trans_date")
        df["trans_type"] = map_values(df["type"], self.TYPE, "trans.type")
        df["operation"] = map_values(df["operation"], self.OPERATION, "trans.operation")
        df["amount"] = to_number(df["amount"], "trans.amount")
        df["balance"] = to_number(df["balance"], "trans.balance")
        df["k_symbol"] = map_values(df["k_symbol"], self.K_SYMBOL, "trans.k_symbol")
        df["bank"] = blank_to_null(df["bank"])
        df["account"] = clean_id_text(df["account"])
        return df