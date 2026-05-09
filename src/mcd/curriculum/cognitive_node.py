"""CognitiveNode dataclass — a single node in a CognitiveGraph."""
from __future__ import annotations

from dataclasses import dataclass, field

NODE_TYPES: list[str] = [
    "thing", "property", "action", "relation", "cause", "effect",
    "instrument", "time", "place", "evidence", "claim", "judgment",
    "source", "tool", "domain",
]

GROUNDING_STATUSES: list[str] = [
    "ungrounded", "partially_grounded", "grounded", "verified",
]


@dataclass
class CognitiveNode:
    node_id: str
    surface: str
    normalized: str
    node_type: str
    grounding_status: str = "ungrounded"
    role_vector: dict[str, float] = field(default_factory=dict)
    domain_vector: dict[str, float] = field(default_factory=dict)
    evidence_refs: list[str] = field(default_factory=list)
    certainty: float = 0.5
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.node_type not in NODE_TYPES:
            raise ValueError(f"Invalid node_type '{self.node_type}'. Must be one of {NODE_TYPES}")
        if self.grounding_status not in GROUNDING_STATUSES:
            raise ValueError(f"Invalid grounding_status '{self.grounding_status}'.")
        if not (0.0 <= self.certainty <= 1.0):
            raise ValueError(f"certainty must be between 0 and 1, got {self.certainty}")

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "surface": self.surface,
            "normalized": self.normalized,
            "node_type": self.node_type,
            "grounding_status": self.grounding_status,
            "role_vector": self.role_vector,
            "domain_vector": self.domain_vector,
            "evidence_refs": self.evidence_refs,
            "certainty": self.certainty,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CognitiveNode":
        return cls(
            node_id=d["node_id"],
            surface=d["surface"],
            normalized=d["normalized"],
            node_type=d["node_type"],
            grounding_status=d.get("grounding_status", "ungrounded"),
            role_vector=d.get("role_vector", {}),
            domain_vector=d.get("domain_vector", {}),
            evidence_refs=d.get("evidence_refs", []),
            certainty=d.get("certainty", 0.5),
            metadata=d.get("metadata", {}),
        )
