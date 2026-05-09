"""CognitiveGraph dataclass — a graph of nodes and edges."""
from __future__ import annotations

from dataclasses import dataclass, field
import json

from .cognitive_node import CognitiveNode
from .cognitive_edge import CognitiveEdge

EVIDENCE_STATUSES: list[str] = [
    "sufficient", "insufficient", "missing", "conflicting",
    "contaminated", "stale",
]

CERTAINTY_POLICIES: list[str] = [
    "certain_knowledge", "probable_knowledge", "possible_knowledge",
    "insufficient_evidence", "near_certainty", "suspend_judgment",
]


@dataclass
class CognitiveGraph:
    graph_id: str
    nodes: list[CognitiveNode] = field(default_factory=list)
    edges: list[CognitiveEdge] = field(default_factory=list)
    root_vector: dict[str, float] = field(default_factory=dict)
    domain_summary: dict[str, float] = field(default_factory=dict)
    evidence_status: str = "missing"
    certainty_policy: str = "probable_knowledge"
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(f"Invalid evidence_status '{self.evidence_status}'")
        if self.certainty_policy not in CERTAINTY_POLICIES:
            raise ValueError(f"Invalid certainty_policy '{self.certainty_policy}'")

    def node_ids(self) -> set[str]:
        return {n.node_id for n in self.nodes}

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "root_vector": self.root_vector,
            "domain_summary": self.domain_summary,
            "evidence_status": self.evidence_status,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }

    def is_json_serializable(self) -> bool:
        try:
            json.dumps(self.to_dict(), ensure_ascii=False)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def from_dict(cls, d: dict) -> "CognitiveGraph":
        return cls(
            graph_id=d["graph_id"],
            nodes=[CognitiveNode.from_dict(n) for n in d.get("nodes", [])],
            edges=[CognitiveEdge.from_dict(e) for e in d.get("edges", [])],
            root_vector=d.get("root_vector", {}),
            domain_summary=d.get("domain_summary", {}),
            evidence_status=d.get("evidence_status", "missing"),
            certainty_policy=d.get("certainty_policy", "probable_knowledge"),
            warnings=d.get("warnings", []),
            metadata=d.get("metadata", {}),
        )
