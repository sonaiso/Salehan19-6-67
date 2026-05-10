"""UnfoldPlan — steps to resolve a fold."""
from __future__ import annotations
from dataclasses import dataclass, field

__all__ = ["UnfoldPlan"]


@dataclass
class UnfoldPlan:
    fold_id: str
    steps: list[str] = field(default_factory=list)
    target_improvements: list[str] = field(default_factory=list)
    requires_human_review: bool = False

    def to_dict(self) -> dict:
        return {
            "fold_id": self.fold_id,
            "steps": self.steps,
            "target_improvements": self.target_improvements,
            "requires_human_review": self.requires_human_review,
        }
