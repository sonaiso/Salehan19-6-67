"""NodeTraceLink — links a CognitiveNode to its Unicode/token origins."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NodeTraceLink:
    node_id: str
    token_ids: list[str]
    unicode_trace_ids: list[str]
    role_vector_contribution: dict[str, float]
    domain_vector_contribution: dict[str, float]
    explanation: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "token_ids": self.token_ids,
            "unicode_trace_ids": self.unicode_trace_ids,
            "role_vector_contribution": self.role_vector_contribution,
            "domain_vector_contribution": self.domain_vector_contribution,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }

    @property
    def is_generated(self) -> bool:
        return bool(self.metadata.get("generated_node"))
