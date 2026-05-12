"""Governed linking transition contract."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.forbidden_transitions import ForbiddenTransition, validate_transition
from mcd.core.linking_type import LinkingType, certificate_eligible, parse_linking_type
from mcd.core.rank_calculus import (
    FINAL_JUDGMENTS,
    RankCalculationError,
    downgrade_judgment_for_residuals,
    enforce_judgment_rank,
    enforce_linking_rank,
)


class LinkingContractError(ValueError):
    """Raised when a linking transition violates the governance contract."""


@dataclass
class LinkingContract:
    source: str
    target: str
    linking_type: LinkingType | str
    evidence_rank: str
    residuals: list[str] = field(default_factory=list)
    governance_passed: bool = False
    proof_object_ref: str = ""
    trace_graph_ref: str = ""
    reverse_trace_ref: str = ""

    def __post_init__(self) -> None:
        self.source = (self.source or "").strip().upper()
        self.target = (self.target or "").strip().upper()
        self.linking_type = parse_linking_type(self.linking_type)

    def validate_transition(self) -> None:
        if not self.source or not self.target:
            raise LinkingContractError("source and target are required")

        try:
            validate_transition(self.source, self.target)
        except ForbiddenTransition as exc:
            raise LinkingContractError(str(exc)) from exc

        if self.linking_type is LinkingType.INTERPRETIVE and self.target == "CERTIFICATE":
            raise LinkingContractError("forbidden transition: INTERPRETATION -> CERTIFICATE")

        if self.linking_type is LinkingType.SEMANTIC and self.target in ("FINAL_JUDGMENT", *FINAL_JUDGMENTS):
            raise LinkingContractError("forbidden transition: SEMANTIC_LINK -> FINAL_JUDGMENT")

        if self.source == "ZERO" and self.target == "CERTIFICATE":
            raise LinkingContractError("forbidden transition: ZERO -> CERTIFICATE")

        try:
            enforce_linking_rank(self.linking_type, self.evidence_rank)
        except RankCalculationError as exc:
            raise LinkingContractError(str(exc)) from exc

        if self.target in FINAL_JUDGMENTS:
            try:
                enforce_judgment_rank(self.evidence_rank, self.target)
            except RankCalculationError as exc:
                raise LinkingContractError(str(exc)) from exc

        if self.target == "CERTIFICATE":
            if not certificate_eligible(self.linking_type):
                raise LinkingContractError("certificate requires GOVERNED_CERTIFICATION linking type")
            if not self.governance_passed:
                raise LinkingContractError("certificate requires governance gate pass")
            if not self.proof_object_ref:
                raise LinkingContractError("certificate requires proof object reference")
            if not self.trace_graph_ref:
                raise LinkingContractError("certificate requires trace graph reference")
            if not self.reverse_trace_ref:
                raise LinkingContractError("certificate requires reverse trace reference")

    def apply(self) -> dict[str, object]:
        self.validate_transition()
        effective_target = downgrade_judgment_for_residuals(self.target, self.residuals)
        propagated_residuals = list(self.residuals)
        return {
            "source": self.source,
            "target": self.target,
            "effective_target": effective_target,
            "linking_type": self.linking_type.name,
            "evidence_rank": self.evidence_rank,
            "residuals": propagated_residuals,
            "proof_object": {
                "ref": self.proof_object_ref,
                "residuals": propagated_residuals,
            },
            "trace_graph": {
                "ref": self.trace_graph_ref,
                "residuals": propagated_residuals,
            },
            "reverse_trace": {
                "ref": self.reverse_trace_ref,
                "residuals": propagated_residuals,
            },
        }
