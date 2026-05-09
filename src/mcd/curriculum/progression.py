"""ProgressionTracker — tracks learning progression across levels."""
from __future__ import annotations

from dataclasses import dataclass, field

from .cognitive_unit import CognitiveUnit


@dataclass
class ProgressionStep:
    level: int
    completed: int
    total: int
    score: float

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "completed": self.completed,
            "total": self.total,
            "score": round(self.score, 4),
            "completion_ratio": round(self.completed / self.total, 4) if self.total else 0.0,
        }


@dataclass
class ProgressionReport:
    steps: list[ProgressionStep] = field(default_factory=list)
    overall_completion: float = 0.0
    next_recommended_level: int | None = None

    def to_dict(self) -> dict:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "overall_completion": round(self.overall_completion, 4),
            "next_recommended_level": self.next_recommended_level,
        }


class ProgressionTracker:
    """Tracks progression through curriculum levels."""

    _PASSING_SCORE = 0.7

    def compute(self, units: list[CognitiveUnit], scores: dict[str, float]) -> ProgressionReport:
        by_level: dict[int, list[CognitiveUnit]] = {}
        for u in units:
            by_level.setdefault(u.level, []).append(u)

        report = ProgressionReport()
        for level in sorted(by_level):
            level_units = by_level[level]
            total = len(level_units)
            level_scores = [scores.get(u.unit_id, 0.0) for u in level_units]
            avg_score = sum(level_scores) / total if total else 0.0
            completed = sum(1 for s in level_scores if s >= self._PASSING_SCORE)
            report.steps.append(ProgressionStep(level, completed, total, avg_score))

        if report.steps:
            report.overall_completion = sum(s.completed / s.total for s in report.steps if s.total) / len(report.steps)
            for step in report.steps:
                if step.score < self._PASSING_SCORE:
                    report.next_recommended_level = step.level
                    break

        return report
