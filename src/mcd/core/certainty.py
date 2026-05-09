"""Certainty dataclass, levels, and scoring."""
from __future__ import annotations

from dataclasses import dataclass

CERTAINTY_LEVELS = {
    "weak_or_unverified":   (0.0,  0.40),
    "hypothesis":           (0.40, 0.60),
    "probable_knowledge":   (0.60, 0.75),
    "strong_knowledge":     (0.75, 0.90),
    "near_certainty":       (0.90, 1.01),
}


def _level_from_score(score: float) -> str:
    for level, (lo, hi) in CERTAINTY_LEVELS.items():
        if lo <= score < hi:
            return level
    return "near_certainty"


@dataclass
class Certainty:
    score: float
    level: str
    evidence_type: str
    explanation: str = ""

    @classmethod
    def from_score(cls, score: float, evidence_type: str = "unknown", explanation: str = "") -> "Certainty":
        level = _level_from_score(score)
        return cls(score=score, level=level, evidence_type=evidence_type, explanation=explanation)
