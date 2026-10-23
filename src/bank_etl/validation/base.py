from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleResult:
    table_name: str
    rule_name: str
    passed: bool
    rows_checked: int | None = None
    rows_failed: int | None = None
    details: str | None = None


class BaseRule(ABC):
    """Contrato común: cada regla sabe evaluarse y devuelve un RuleResult."""

    table_name: str
    rule_name: str

    @abstractmethod
    def evaluate(self, db) -> RuleResult:
        ...