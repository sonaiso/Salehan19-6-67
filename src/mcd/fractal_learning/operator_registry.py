from __future__ import annotations

from dataclasses import dataclass, field

from mcd.fractal_learning.operator_candidate import TypedOperatorCandidate
from mcd.fractal_learning.operator_contract import OperatorContract


@dataclass(frozen=True)
class RegistrationResult:
    accepted: bool
    residuals: list[str] = field(default_factory=list)


class FractalOperatorRegistry:
    def __init__(self) -> None:
        self._operators: dict[str, OperatorContract] = {}

    def register(self, candidate: TypedOperatorCandidate) -> RegistrationResult:
        residuals = list(candidate.validate())
        operator_id = candidate.contract.operator_id

        if _looks_free_rule(operator_id):
            residuals.append("operator_contract_invalid")

        if not candidate.contract.gates:
            residuals.append("operator_missing_gate")

        if not candidate.contract.residual_policy:
            residuals.append("operator_contract_invalid")

        if not candidate.contract.forbidden_outputs:
            residuals.append("operator_contract_invalid")

        residuals = list(dict.fromkeys(residuals))
        if residuals:
            return RegistrationResult(accepted=False, residuals=residuals)

        self._operators[operator_id] = candidate.contract
        return RegistrationResult(accepted=True, residuals=[])

    def get(self, operator_id: str) -> OperatorContract | None:
        return self._operators.get(operator_id)

    def all(self) -> list[OperatorContract]:
        return list(self._operators.values())


def _looks_free_rule(operator_id: str) -> bool:
    normalized = operator_id.strip().lower()
    return normalized.startswith("solve_") or normalized.endswith("_problem") or "solve" in normalized
