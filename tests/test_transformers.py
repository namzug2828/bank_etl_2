import pandas as pd
import pytest

from bank_etl.transform.account import AccountTransformer
from bank_etl.transform.client import ClientTransformer


def test_client_decodes_birth_number():
    raw = pd.DataFrame({
        "client_id": ["1", "2", "3"],
        "birth_number": ["706213", "450204", "406009"],
        "district_id": ["18", "1", "1"],
    })
    out = ClientTransformer().run(raw)
    assert out["gender"].tolist() == ["F", "M", "F"]
    assert out.loc[0, "birth_date"].date().isoformat() == "1970-12-13"
    assert out.loc[1, "birth_date"].date().isoformat() == "1945-02-04"


def test_account_rejects_unknown_frequency():
    raw = pd.DataFrame({
        "account_id": ["1"], "district_id": ["1"],
        "frequency": ["ALGO RARO"], "date": ["930101"],
    })
    with pytest.raises(ValueError):
        AccountTransformer().run(raw)