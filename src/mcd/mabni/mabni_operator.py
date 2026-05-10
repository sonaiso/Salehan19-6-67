"""MabniOperator — dataclass representing a single Mabni particle/operator."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.mabni.mabni_schema import (
    CertaintyEffect,
    LogicalFunction,
    MabniType,
    PragmaticFunction,
)


@dataclass
class MabniOperator:
    operator_id: str
    surface: str
    normalized: str
    mabni_type: MabniType
    logical_function: LogicalFunction
    pragmatic_function: PragmaticFunction
    affects_evidence: bool
    affects_certainty: bool
    certainty_effect: CertaintyEffect
    trace_ids: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    # ALWAYS False by default — mabni doesn't create evidence
    creates_evidence: bool = False

    def __post_init__(self) -> None:
        # Enforce the invariant: mabni operators never create evidence
        if self.creates_evidence:
            raise ValueError(
                f"MabniOperator '{self.operator_id}': creates_evidence must be False. "
                "Mabni operators modify scope/certainty but never create evidence."
            )
        # Coerce enum fields if string values were passed (e.g. from JSON)
        if isinstance(self.mabni_type, str):
            self.mabni_type = MabniType(self.mabni_type)
        if isinstance(self.logical_function, str):
            self.logical_function = LogicalFunction(self.logical_function)
        if isinstance(self.pragmatic_function, str):
            self.pragmatic_function = PragmaticFunction(self.pragmatic_function)
        if isinstance(self.certainty_effect, str):
            self.certainty_effect = CertaintyEffect(self.certainty_effect)

    def to_dict(self) -> dict:
        return {
            "operator_id": self.operator_id,
            "surface": self.surface,
            "normalized": self.normalized,
            "mabni_type": self.mabni_type.value,
            "logical_function": self.logical_function.value,
            "pragmatic_function": self.pragmatic_function.value,
            "affects_evidence": self.affects_evidence,
            "affects_certainty": self.affects_certainty,
            "creates_evidence": self.creates_evidence,
            "certainty_effect": self.certainty_effect.value,
            "trace_ids": self.trace_ids,
            "examples": self.examples,
        }
