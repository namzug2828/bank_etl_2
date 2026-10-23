from decimal import Decimal

from bank_etl.validation.base import BaseRule, RuleResult


class RowCountRule(BaseRule):
    """Conciliación de conteos: raw vs. core."""

    def __init__(self, raw_table: str, core_table: str):
        self.raw_table = raw_table
        self.table_name = core_table
        self.rule_name = "row_count_raw_vs_core"

    def evaluate(self, db) -> RuleResult:
        raw = int(db.scalar(f'SELECT COUNT(*) FROM raw."{self.raw_table}"'))
        core = int(db.scalar(f"SELECT COUNT(*) FROM core.{self.table_name}"))
        return RuleResult(
            self.table_name, self.rule_name, raw == core,
            rows_checked=raw, rows_failed=abs(raw - core),
            details=f"raw={raw}, core={core}",
        )


class SumChecksumRule(BaseRule):
    """Suma de control de una columna numérica: raw vs. core."""

    TOLERANCE = Decimal("0.01")

    def __init__(self, raw_table: str, core_table: str, column: str):
        self.raw_table = raw_table
        self.table_name = core_table
        self.column = column
        self.rule_name = f"checksum:{column}"

    def evaluate(self, db) -> RuleResult:
        raw_sum = db.scalar(f'SELECT SUM("{self.column}"::numeric) FROM raw."{self.raw_table}"')
        core_sum = db.scalar(f"SELECT SUM({self.column}) FROM core.{self.table_name}")
        raw_sum = Decimal(raw_sum or 0)
        core_sum = Decimal(core_sum or 0)
        return RuleResult(
            self.table_name, self.rule_name,
            abs(raw_sum - core_sum) < self.TOLERANCE,
            details=f"raw={raw_sum}, core={core_sum}",
        )


class QueryRule(BaseRule):
    """Cuenta filas que violan una condición. Pasa si violaciones <= max_failures."""

    def __init__(self, table_name: str, rule_name: str, violations_sql: str,
                 checked_sql: str | None = None, max_failures: int = 0):
        self.table_name = table_name
        self.rule_name = rule_name
        self.violations_sql = violations_sql
        self.checked_sql = checked_sql or f"SELECT COUNT(*) FROM core.{table_name}"
        self.max_failures = max_failures

    def evaluate(self, db) -> RuleResult:
        failed = int(db.scalar(self.violations_sql) or 0)
        checked = int(db.scalar(self.checked_sql) or 0)
        return RuleResult(
            self.table_name, self.rule_name, failed <= self.max_failures,
            rows_checked=checked, rows_failed=failed,
            details=f"{failed} violaciones (máximo permitido: {self.max_failures})",
        )


class NullCountRule(QueryRule):
    def __init__(self, table: str, column: str, max_nulls: int = 0):
        super().__init__(
            table, f"nulls:{column}",
            f"SELECT COUNT(*) FROM core.{table} WHERE {column} IS NULL",
            max_failures=max_nulls,
        )


class UniqueKeyRule(QueryRule):
    def __init__(self, table: str, column: str):
        super().__init__(
            table, f"unique:{column}",
            f"SELECT COUNT(*) FROM (SELECT 1 FROM core.{table} "
            f"GROUP BY {column} HAVING COUNT(*) > 1) d",
        )


class ForeignKeyRule(QueryRule):
    def __init__(self, table: str, fk: str, parent: str, pk: str):
        super().__init__(
            table, f"fk:{fk}->{parent}.{pk}",
            f"SELECT COUNT(*) FROM core.{table} c "
            f"LEFT JOIN core.{parent} p ON c.{fk} = p.{pk} "
            f"WHERE c.{fk} IS NOT NULL AND p.{pk} IS NULL",
        )


class ConditionRule(QueryRule):
    """Rango o regla de negocio simple: bad_condition describe lo que NO debe pasar."""

    def __init__(self, table: str, name: str, bad_condition: str):
        super().__init__(
            table, name,
            f"SELECT COUNT(*) FROM core.{table} WHERE {bad_condition}",
        )