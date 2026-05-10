"""VectorTrace — links a composed vector to its source traces."""
from __future__ import annotations

from dataclasses import dataclass, field

VECTOR_TYPES = ["feature", "role", "domain", "evidence", "certainty", "graph"]


@dataclass
class VectorTrace:
    vector_id: str
    vector_type: str
    source_trace_ids: list[str]
    vector: dict[str, float]
    contribution_weights: dict[str, float]
    normalization_applied: bool
    explanation: str

    def __post_init__(self) -> None:
        if self.vector_type not in VECTOR_TYPES:
            raise ValueError(f"Invalid vector_type '{self.vector_type}'")
        for k, v in self.vector.items():
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"Vector dimension '{k}' = {v} out of [0,1]")

    def to_dict(self) -> dict:
        return {
            "vector_id": self.vector_id,
            "vector_type": self.vector_type,
            "source_trace_ids": self.source_trace_ids,
            "vector": self.vector,
            "contribution_weights": self.contribution_weights,
            "normalization_applied": self.normalization_applied,
            "explanation": self.explanation,
        }
