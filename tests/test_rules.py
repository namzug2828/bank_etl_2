from bank_etl.validation.base import BaseRule
from bank_etl.validation.rules import NullCountRule, RowCountRule
from bank_etl.validation.validator import Validator


class FakeDB:
    def __init__(self, values):
        self._values = iter(values)

    def scalar(self, sql, params=None):
        return next(self._values)


class BoomRule(BaseRule):
    table_name = "x"
    rule_name = "boom"

    def evaluate(self, db):
        raise RuntimeError("falló")


def test_null_rule_allows_known_nulls():
    # primero viola=1, luego checked=77
    result = NullCountRule("district", "crimes_95", max_nulls=1).evaluate(FakeDB([1, 77]))
    assert result.passed and result.rows_failed == 1


def test_null_rule_fails_when_exceeding_limit():
    result = NullCountRule("client", "gender").evaluate(FakeDB([3, 5369]))
    assert not result.passed and result.rows_failed == 3


def test_row_count_detects_mismatch():
    result = RowCountRule("trans", "trans").evaluate(FakeDB([100, 99]))
    assert not result.passed and result.rows_failed == 1


def test_validator_survives_a_broken_rule():
    results = Validator(FakeDB([]), [BoomRule()]).run()
    assert len(results) == 1
    assert not results[0].passed
    assert "falló" in results[0].details