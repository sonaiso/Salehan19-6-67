from __future__ import annotations

from dataclasses import dataclass

from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit
from mcd.math_governance.governance_gate import MathematicalGovernanceGate
from mcd.math_governance.level_morphism_registry import LevelMorphismRegistry
from mcd.math_governance.text_ascent_chain import validate_text_ascent_chain


@dataclass
class InvariantResult:
    name: str
    passed: bool
    details: list[str]

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "details": self.details}


class MathematicalInvariantSuite:
    def __init__(self) -> None:
        self._registry = LevelMorphismRegistry()
        self._gate = MathematicalGovernanceGate()

    def every_level_transition_has_morphism(self, units: list[GovernedFractalUnit]) -> InvariantResult:
        details = []
        passed = True
        for i in range(len(units) - 1):
            ok, msg = self._registry.validate_transition(units[i].level_id, units[i + 1].level_id)
            if not ok:
                passed = False
                details.extend(msg)
        return InvariantResult("every level transition has morphism", passed, details)

    def final_judgment_has_reverse_path(self, units: list[GovernedFractalUnit]) -> InvariantResult:
        if not units:
            return InvariantResult("final judgment reverse path", False, ["empty chain"])
        report = validate_text_ascent_chain(units)
        return InvariantResult("final judgment has unicode-to-fulltext reverse path", report.passed, report.violations)

    def run(self, units: list[GovernedFractalUnit]) -> list[InvariantResult]:
        return [
            self.every_level_transition_has_morphism(units),
            self.final_judgment_has_reverse_path(units),
        ]
