"""EdgeTraceLink — links a CognitiveEdge to its Unicode/token origins."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EdgeTraceLink:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation: str
    supporting_unicode_trace_ids: list[str]
    supporting_token_ids: list[str]
    confidence: float
    explanation: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0,1], got {self.confidence}")

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relation": self.relation,
            "supporting_unicode_trace_ids": self.supporting_unicode_trace_ids,
            "supporting_token_ids": self.supporting_token_ids,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }

    @property
    def is_inferred(self) -> bool:
        return bool(self.metadata.get("inferred"))
