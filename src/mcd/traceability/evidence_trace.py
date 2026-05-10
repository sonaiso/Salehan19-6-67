"""EvidenceTrace — tracks evidence status in the trace chain."""
from __future__ import annotations

from dataclasses import dataclass, field

EVIDENCE_STATUSES = [
    "present",
    "missing",
    "partial",
    "fake",
    "unverified",
    "source_required",
]


@dataclass
class EvidenceTrace:
    evidence_id: str
    status: str
    source_trace_ids: list[str]
    token_ids: list[str]
    description: str
    evidence_type: str = "unclassified"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in EVIDENCE_STATUSES:
            raise ValueError(f"Invalid evidence status '{self.status}'")

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "status": self.status,
            "source_trace_ids": self.source_trace_ids,
            "token_ids": self.token_ids,
            "description": self.description,
            "evidence_type": self.evidence_type,
            "metadata": self.metadata,
        }
