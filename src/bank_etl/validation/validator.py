import logging

from bank_etl.validation.base import BaseRule, RuleResult

logger = logging.getLogger(__name__)


class Validator:
    """Ejecuta un conjunto de reglas. Una regla que falla o se rompe no detiene a las demás."""

    def __init__(self, db, rules: list[BaseRule]):
        self.db = db
        self.rules = rules

    def run(self) -> list[RuleResult]:
        results: list[RuleResult] = []
        for rule in self.rules:
            try:
                result = rule.evaluate(self.db)
            except Exception as exc:  # una regla rota cuenta como fallida
                logger.exception("Error evaluando %s.%s", rule.table_name, rule.rule_name)
                result = RuleResult(rule.table_name, rule.rule_name, False,
                                    details=f"ERROR: {exc}"[:500])
            level = logging.INFO if result.passed else logging.WARNING
            logger.log(level, "%s %s.%s %s",
                       "PASS" if result.passed else "FAIL",
                       result.table_name, result.rule_name, result.details or "")
            results.append(result)

        failed = sum(not r.passed for r in results)
        logger.info("Validación terminada: %s reglas, %s fallidas", len(results), failed)
        return results