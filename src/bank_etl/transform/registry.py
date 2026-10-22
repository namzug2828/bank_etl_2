from bank_etl.transform.account import AccountTransformer
from bank_etl.transform.card import CardTransformer
from bank_etl.transform.client import ClientTransformer
from bank_etl.transform.disp import DispTransformer
from bank_etl.transform.district import DistrictTransformer
from bank_etl.transform.loan import LoanTransformer
from bank_etl.transform.permanent_order import PermanentOrderTransformer
from bank_etl.transform.trans import TransTransformer

# Orden de carga = orden de dependencias (FK)
TRANSFORMERS = [
    DistrictTransformer,
    ClientTransformer,
    AccountTransformer,
    DispTransformer,
    CardTransformer,
    LoanTransformer,
    PermanentOrderTransformer,
    TransTransformer,
]