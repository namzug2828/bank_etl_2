import numpy as np
import pandas as pd

from bank_etl.transform.base import BaseTransformer
from bank_etl.transform.helpers import blank_to_null, parse_yymmdd, to_number


class ClientTransformer(BaseTransformer):
    source_table = "client"
    target_table = "client"
    target_columns = ["client_id", "birth_number", "birth_date", "gender", "district_id"]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        bn = blank_to_null(df["birth_number"]).str.zfill(6)   # YYMMDD

        # En las mujeres el mes viene con +50 (ej. 706213 -> mes 12, mujer)
        month = pd.to_numeric(bn.str.slice(2, 4), errors="coerce")
        is_female = (month > 50).fillna(False).astype(bool)
        real_month = month.where(~is_female, month - 50).astype("Int64")
        month_txt = real_month.astype("string").str.zfill(2)

        yymmdd = bn.str.slice(0, 2) + month_txt + bn.str.slice(4, 6)

        df["birth_number"] = bn
        df["birth_date"] = parse_yymmdd(yymmdd, "client.birth_date")
        df["gender"] = pd.Series(
            np.where(is_female, "F", "M"), index=df.index
        ).where(month.notna())
        df["client_id"] = to_number(df["client_id"], "client.client_id").astype("Int64")
        df["district_id"] = to_number(df["district_id"], "client.district_id").astype("Int64")
        return df