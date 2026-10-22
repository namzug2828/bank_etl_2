from bank_etl.transform.account import AccountTransformer
from bank_etl.transform.client import ClientTransformer
from bank_etl.transform.district import DistrictTransformer

# Orden de carga = orden de dependencias (FK)
TRANSFORMERS = [
    DistrictTransformer,
    ClientTransformer,
    AccountTransformer,
]