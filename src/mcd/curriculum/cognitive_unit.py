"""CognitiveUnit dataclass — a single curriculum training example."""
from __future__ import annotations

from dataclasses import dataclass, field

from .reality_frame import RealityFrame


@dataclass
class CognitiveUnit:
    unit_id: str
    input_text: str
    level: int
    target_layer: str
    expected_frame: RealityFrame
    expected_warnings: list[str] = field(default_factory=list)
    forbidden_confusions: list[str] = field(default_factory=list)
    evidence_need: list[str] = field(default_factory=list)
    certainty_policy: str = "probable_knowledge"
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "input_text": self.input_text,
            "level": self.level,
            "target_layer": self.target_layer,
            "expected_frame": self.expected_frame.to_dict(),
            "expected_warnings": self.expected_warnings,
            "forbidden_confusions": self.forbidden_confusions,
            "evidence_need": self.evidence_need,
            "certainty_policy": self.certainty_policy,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "metadata": self.metadata,
        }
