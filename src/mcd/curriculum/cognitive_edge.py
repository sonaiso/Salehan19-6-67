"""CognitiveEdge dataclass — a directed edge in a CognitiveGraph."""
from __future__ import annotations

from dataclasses import dataclass, field

VALID_RELATIONS: list[str] = [
    "has_property", "agent_of", "patient_of", "instrument_of",
    "time_of", "place_of", "causes", "caused_by", "supports",
    "contradicts", "qualifies", "restricts", "entails",
    "requires_evidence", "has_certainty_policy", "belongs_to_domain",
    "uses_tool", "sourced_from", "not_equivalent_to",
]


@dataclass
class CognitiveEdge:
    edge_id: str
    source: str
    relation: str
    target: str
    qualifier: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    certainty: float = 0.5
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.relation not in VALID_RELATIONS:
            raise ValueError(f"Invalid relation '{self.relation}'. Must be one of {VALID_RELATIONS}")
        if not (0.0 <= self.certainty <= 1.0):
            raise ValueError(f"certainty must be between 0 and 1, got {self.certainty}")

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "qualifier": self.qualifier,
            "evidence_refs": self.evidence_refs,
            "certainty": self.certainty,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CognitiveEdge":
        return cls(
            edge_id=d["edge_id"],
            source=d["source"],
            relation=d["relation"],
            target=d["target"],
            qualifier=d.get("qualifier"),
            evidence_refs=d.get("evidence_refs", []),
            certainty=d.get("certainty", 0.5),
            metadata=d.get("metadata", {}),
        )
