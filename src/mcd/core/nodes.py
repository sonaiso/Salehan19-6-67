"""KnowledgeNode dataclass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

NODE_LEVELS = [
    "unicode", "letter", "diacritic", "syllable", "root",
    "pattern", "word", "phrase", "sentence", "thing",
    "property", "concept", "claim", "measure",
]


@dataclass
class KnowledgeNode:
    node_id: str
    level: str
    surface: str
    features: dict[str, Any] = field(default_factory=dict)
    role_vector: dict[str, float] = field(default_factory=dict)
    relations: list[str] = field(default_factory=list)
    evidence: list = field(default_factory=list)
    certainty: "Certainty | None" = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "level": self.level,
            "surface": self.surface,
            "features": self.features,
            "role_vector": self.role_vector,
            "relations": self.relations,
            "certainty": {
                "score": self.certainty.score,
                "level": self.certainty.level,
                "evidence_type": self.certainty.evidence_type,
                "explanation": self.certainty.explanation,
            } if self.certainty else None,
        }
