import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import map_values, parse_yymmdd, to_number


class LoanTransformer(BaseTransformer):
    source_table = "loan"
    target_table = "loan"
    target_columns = ["loan_id", "account_id", "loan_date", "amount",
                      "duration", "payments", "status"]

    # A: terminado sin problemas, B: terminado sin pagar,
    # C: en curso sin problemas, D: en curso con deuda
    STATUS = {"A": "A", "B": "B", "C": "C", "D": "D"}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for c in ["loan_id", "account_id", "duration"]:
            df[c] = to_number(df[c], f"loan.{c}").astype("Int64")
        for c in ["amount", "payments"]:
            df[c] = to_number(df[c], f"loan.{c}")
        df["loan_date"] = parse_yymmdd(df["date"], "loan.loan_date")
        df["status"] = map_values(df["status"], self.STATUS, "loan.status")
        return df