"""CertaintyTrace — tracks certainty policy derivation."""
from __future__ import annotations

from dataclasses import dataclass, field

CERTAINTY_POLICIES = [
    "suspend",
    "hypothesis",
    "probable_knowledge",
    "strong_knowledge",
    "near_certainty",
]


@dataclass
class CertaintyTrace:
    certainty_id: str
    policy: str
    score: float
    source_evidence_ids: list[str]
    source_token_ids: list[str]
    reason: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.policy not in CERTAINTY_POLICIES:
            raise ValueError(f"Invalid certainty policy '{self.policy}'")
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"score must be in [0,1], got {self.score}")

    def to_dict(self) -> dict:
        return {
            "certainty_id": self.certainty_id,
            "policy": self.policy,
            "score": self.score,
            "source_evidence_ids": self.source_evidence_ids,
            "source_token_ids": self.source_token_ids,
            "reason": self.reason,
            "metadata": self.metadata,
        }
