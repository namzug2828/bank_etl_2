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


from bank_etl.transform.trans import TransTransformer
from bank_etl.transform.loan import LoanTransformer


def test_trans_blanks_become_null_and_translates():
    raw = pd.DataFrame({
        "trans_id": ["1"], "account_id": ["10"], "date": ["930101"],
        "type": ["PRIJEM"], "operation": ["VKLAD"], "amount": ["700.0"],
        "balance": ["700.0"], "k_symbol": [" "], "bank": [None], "account": [None],
    })
    out = TransTransformer().run(raw)
    assert out.loc[0, "trans_type"] == "CREDIT"
    assert out.loc[0, "operation"] == "CASH_DEPOSIT"
    assert pd.isna(out.loc[0, "k_symbol"])


def test_trans_rejects_unknown_operation():
    raw = pd.DataFrame({
        "trans_id": ["1"], "account_id": ["10"], "date": ["930101"],
        "type": ["PRIJEM"], "operation": ["OTRA COSA"], "amount": ["1"],
        "balance": ["1"], "k_symbol": [None], "bank": [None], "account": [None],
    })
    with pytest.raises(ValueError):
        TransTransformer().run(raw)


def test_loan_rejects_invalid_status():
    raw = pd.DataFrame({
        "loan_id": ["1"], "account_id": ["1"], "date": ["930705"],
        "amount": ["96396"], "duration": ["12"], "payments": ["8033.0"], "status": ["Z"],
    })
    with pytest.raises(ValueError):
        LoanTransformer().run(raw)