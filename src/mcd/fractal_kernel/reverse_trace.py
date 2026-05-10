from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class ReverseTrace:
    reverse_trace_id: str
    final_claim: str
    proof_id: str
    judgment_units: list[str] = field(default_factory=list)
    concept_units: list[str] = field(default_factory=list)
    sentence_units: list[str] = field(default_factory=list)
    token_units: list[str] = field(default_factory=list)
    unicode_units: list[str] = field(default_factory=list)
    evidence_chain: list[str] = field(default_factory=list)
    certainty_chain: list[str] = field(default_factory=list)
    operator_chain: list[str] = field(default_factory=list)
    relation_chain: list[str] = field(default_factory=list)
    complete: bool = False

    @staticmethod
    def make_id() -> str:
        return f"RTRACE-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "reverse_trace_id": self.reverse_trace_id,
            "final_claim": self.final_claim,
            "proof_id": self.proof_id,
            "judgment_units": self.judgment_units,
            "concept_units": self.concept_units,
            "sentence_units": self.sentence_units,
            "token_units": self.token_units,
            "unicode_units": self.unicode_units,
            "evidence_chain": self.evidence_chain,
            "certainty_chain": self.certainty_chain,
            "operator_chain": self.operator_chain,
            "relation_chain": self.relation_chain,
            "complete": self.complete,
        }
