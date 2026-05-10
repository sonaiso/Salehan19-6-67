"""AgreementEngine — checks gender/number/case agreement between words."""
from __future__ import annotations
from mcd.murab.murab_schema import MurabUnit


class AgreementEngine:
    """Checks morphosyntactic agreement between Arabic words."""

    def check_agreement(self, unit1: MurabUnit, unit2: MurabUnit) -> dict:
        """Check agreement between two MurabUnit objects."""
        issues = []

        if unit1.irab_case != unit2.irab_case:
            issues.append({
                "type": "case_mismatch",
                "expected": unit1.irab_case,
                "found": unit2.irab_case,
            })

        return {
            "agree": len(issues) == 0,
            "issues": issues,
            "unit1": unit1.surface,
            "unit2": unit2.surface,
        }

    def check_sequence_agreement(self, units: list) -> list:
        """Check agreement across a sequence of units."""
        results = []
        for i in range(len(units) - 1):
            result = self.check_agreement(units[i], units[i + 1])
            if not result["agree"]:
                results.append(result)
        return results
