from bank_etl.transform.registry import TRANSFORMERS
from bank_etl.validation.rules import (
    ConditionRule, ForeignKeyRule, NullCountRule, QueryRule,
    RowCountRule, SumChecksumRule, UniqueKeyRule,
)

PRIMARY_KEYS = {
    "district": "district_id", "client": "client_id", "account": "account_id",
    "disp": "disp_id", "card": "card_id", "loan": "loan_id",
    "permanent_order": "order_id", "trans": "trans_id",
}

FOREIGN_KEYS = [
    ("client", "district_id", "district", "district_id"),
    ("account", "district_id", "district", "district_id"),
    ("disp", "client_id", "client", "client_id"),
    ("disp", "account_id", "account", "account_id"),
    ("card", "disp_id", "disp", "disp_id"),
    ("loan", "account_id", "account", "account_id"),
    ("permanent_order", "account_id", "account", "account_id"),
    ("trans", "account_id", "account", "account_id"),
]

# (tabla raw, tabla core, columna)
CHECKSUMS = [
    ("loan", "loan", "amount"),
    ("loan", "loan", "payments"),
    ("order", "permanent_order", "amount"),
    ("trans", "trans", "amount"),
    ("trans", "trans", "balance"),
]


def build_rules() -> list:
    rules = []

    # 1) Conciliación de conteos raw vs core
    rules += [RowCountRule(t.source_table, t.target_table) for t in TRANSFORMERS]

    # 2) Sumas de control
    rules += [SumChecksumRule(r, c, col) for r, c, col in CHECKSUMS]

    # 3) Duplicados de clave
    rules += [UniqueKeyRule(t, pk) for t, pk in PRIMARY_KEYS.items()]

    # 4) Integridad referencial
    rules += [ForeignKeyRule(*fk) for fk in FOREIGN_KEYS]

    # 5) Nulos: lo que la transformación debió completar
    rules += [
        NullCountRule("client", "birth_date"),
        NullCountRule("client", "gender"),
        # Hallazgo conocido: 1 distrito trae '?' en las columnas de 1995
        NullCountRule("district", "crimes_95", max_nulls=1),
        NullCountRule("district", "unemployment_95", max_nulls=1),
    ]

    # 6) Rangos y reglas de negocio
    rules += [
        ConditionRule("loan", "range:duration", "duration NOT IN (12, 24, 36, 48, 60)"),
        ConditionRule("loan", "range:amount_positive", "amount <= 0"),
        ConditionRule("trans", "range:trans_date",
                      "trans_date NOT BETWEEN DATE '1993-01-01' AND DATE '1998-12-31'"),
        ConditionRule("client", "range:birth_date",
                      "birth_date NOT BETWEEN DATE '1900-01-01' AND DATE '1995-12-31'"),
        QueryRule(
            "loan", "business:loan_after_account_creation",
            "SELECT COUNT(*) FROM core.loan l JOIN core.account a USING (account_id) "
            "WHERE l.loan_date < a.created_date",
        ),
        QueryRule(
            "disp", "business:one_owner_per_account",
            "SELECT COUNT(*) FROM (SELECT account_id FROM core.disp "
            "GROUP BY account_id HAVING COUNT(*) FILTER (WHERE disp_type = 'OWNER') <> 1) d",
            checked_sql="SELECT COUNT(*) FROM core.account",
        ),
    ]
    return rules