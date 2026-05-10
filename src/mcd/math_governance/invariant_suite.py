from __future__ import annotations

from dataclasses import dataclass

from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit
from mcd.math_governance.governance_gate import MathematicalGovernanceGate
from mcd.math_governance.level_morphism_registry import LevelMorphismRegistry


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

    def final_answer_has_reverse_path(self, units: list[GovernedFractalUnit]) -> InvariantResult:
        if not units:
            return InvariantResult("final answer reverse path", False, ["empty chain"])
        tail = units[-1]
        passed = bool(tail.trace_refs) and tail.level_id == "final_answer"
        details = [] if passed else ["final answer missing reverse trace to earlier levels"]
        return InvariantResult("final answer has reverse path", passed, details)

    def run(self, units: list[GovernedFractalUnit]) -> list[InvariantResult]:
        return [
            self.every_level_transition_has_morphism(units),
            self.final_answer_has_reverse_path(units),
        ]
