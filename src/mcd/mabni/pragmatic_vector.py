"""MabniPragmaticVector — float feature vector for a Mabni operator."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction


@dataclass
class MabniPragmaticVector:
    reference: float = 0.0
    scope: float = 0.0
    condition: float = 0.0
    negation: float = 0.0
    answer: float = 0.0
    speech_act: float = 0.0
    emphasis: float = 0.0
    restriction: float = 0.0
    exception: float = 0.0
    qasr: float = 0.0
    interrogation: float = 0.0
    command: float = 0.0
    prohibition: float = 0.0
    uncertainty: float = 0.0
    suspension: float = 0.0
    # evidence_creation MUST be 0.0 — mabni never creates evidence
    evidence_creation: float = 0.0
    evidence_requirement: float = 0.0
    certainty_increase: float = 0.0
    certainty_decrease: float = 0.0

    def __post_init__(self) -> None:
        if self.evidence_creation > 0.0:
            raise ValueError(
                "MabniPragmaticVector.evidence_creation must be <= 0.0 unless external evidence exists. "
                "Mabni operators do not create evidence."
            )

    def to_dict(self) -> dict:
        return {
            "reference": round(self.reference, 4),
            "scope": round(self.scope, 4),
            "condition": round(self.condition, 4),
            "negation": round(self.negation, 4),
            "answer": round(self.answer, 4),
            "speech_act": round(self.speech_act, 4),
            "emphasis": round(self.emphasis, 4),
            "restriction": round(self.restriction, 4),
            "exception": round(self.exception, 4),
            "qasr": round(self.qasr, 4),
            "interrogation": round(self.interrogation, 4),
            "command": round(self.command, 4),
            "prohibition": round(self.prohibition, 4),
            "uncertainty": round(self.uncertainty, 4),
            "suspension": round(self.suspension, 4),
            "evidence_creation": round(self.evidence_creation, 4),
            "evidence_requirement": round(self.evidence_requirement, 4),
            "certainty_increase": round(self.certainty_increase, 4),
            "certainty_decrease": round(self.certainty_decrease, 4),
        }

    @classmethod
    def from_operator(cls, operator: MabniOperator) -> "MabniPragmaticVector":
        """Build a pragmatic vector from a MabniOperator."""
        v: dict[str, float] = {}

        lf = operator.logical_function
        pf = operator.pragmatic_function
        ce = operator.certainty_effect
        mt = operator.mabni_type

        v["reference"] = 1.0 if lf == LogicalFunction.reference else 0.0
        v["scope"] = 1.0 if lf in (LogicalFunction.scope, LogicalFunction.restriction, LogicalFunction.exception) else 0.0
        v["condition"] = 1.0 if lf == LogicalFunction.condition else 0.0
        v["negation"] = 1.0 if lf == LogicalFunction.negation else 0.0
        v["answer"] = 1.0 if lf == LogicalFunction.answer else 0.0
        v["speech_act"] = 1.0 if lf == LogicalFunction.speech_act else 0.0
        v["emphasis"] = 1.0 if lf == LogicalFunction.emphasis else 0.0
        v["restriction"] = 1.0 if lf in (LogicalFunction.restriction, LogicalFunction.qasr) else 0.0
        v["exception"] = 1.0 if lf == LogicalFunction.exception else 0.0
        v["qasr"] = 1.0 if lf == LogicalFunction.qasr else 0.0
        v["interrogation"] = 1.0 if pf == PragmaticFunction.question or mt == MabniType.interrogative else 0.0
        v["command"] = 1.0 if pf == PragmaticFunction.command or mt == MabniType.imperative_marker else 0.0
        v["prohibition"] = 1.0 if pf == PragmaticFunction.prohibition or mt == MabniType.prohibition_marker else 0.0
        v["uncertainty"] = 1.0 if ce in (CertaintyEffect.suspend, CertaintyEffect.lower) else 0.0
        v["suspension"] = 1.0 if lf == LogicalFunction.suspension or ce == CertaintyEffect.suspend else 0.0
        # evidence_creation is always 0.0
        v["evidence_creation"] = 0.0
        v["evidence_requirement"] = 1.0 if operator.affects_evidence else 0.0
        v["certainty_increase"] = 0.0  # mabni never increases certainty on its own
        v["certainty_decrease"] = 1.0 if ce in (CertaintyEffect.lower, CertaintyEffect.scope_limit) else 0.0

        return cls(**v)
