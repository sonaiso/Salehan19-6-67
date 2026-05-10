from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

PROOF_STATUSES = {"certificate", "hypothesis", "zero"}


@dataclass
class ProofObject:
    proof_id: str
    claim_id: str
    proof_status: str = "zero"
    evidence_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    relation_refs: list[str] = field(default_factory=list)
    certainty_score: float = 0.0
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reverse_trace_id: Optional[str] = None

    def __post_init__(self):
        if self.proof_status not in PROOF_STATUSES:
            raise ValueError(f"Invalid proof_status: {self.proof_status}")
        if self.proof_status == "certificate":
            if not self.evidence_refs:
                raise ValueError("Certificate ProofObject requires evidence_refs")
            if self.blockers:
                raise ValueError("Certificate ProofObject cannot have blockers")
            if self.reverse_trace_id is None:
                raise ValueError("Certificate ProofObject requires reverse_trace_id")

    @staticmethod
    def make_id() -> str:
        return f"PROOF-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "proof_id": self.proof_id,
            "claim_id": self.claim_id,
            "proof_status": self.proof_status,
            "evidence_refs": self.evidence_refs,
            "trace_refs": self.trace_refs,
            "relation_refs": self.relation_refs,
            "certainty_score": self.certainty_score,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "reverse_trace_id": self.reverse_trace_id,
        }
