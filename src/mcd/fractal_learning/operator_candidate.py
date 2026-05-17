from __future__ import annotations

from dataclasses import dataclass, field

from mcd.fractal_learning.operator_contract import OperatorContract


@dataclass
class TypedOperatorCandidate:
    contract: OperatorContract
    transition: tuple[str, str] | None = None
    evidence: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.transition is None:
            self.transition = (self.contract.layer_from, self.contract.layer_to)

    def validate(self) -> list[str]:
        residuals = list(self.residuals)
        residuals.extend(self.contract.validate())

        if not isinstance(self.transition, tuple) or len(self.transition) != 2:
            residuals.append("operator_multi_transition_forbidden")
        elif self.transition != (self.contract.layer_from, self.contract.layer_to):
            residuals.append("operator_multi_transition_forbidden")

        return list(dict.fromkeys(residuals))
