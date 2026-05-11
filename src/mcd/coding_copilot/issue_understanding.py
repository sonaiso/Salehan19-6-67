"""Issue understanding model for governed coding tasks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from mcd.coding_copilot.coding_residual import CodingResidual

TaskType = Literal[
    "bugfix",
    "feature",
    "refactor",
    "docs",
    "test",
    "architecture",
    "unknown",
]


@dataclass
class IssueUnderstanding:
    issue_id: str
    raw_text: str
    task_type: TaskType = "unknown"
    requested_behavior: str = ""
    observed_behavior: str = ""
    constraints: list[str] = field(default_factory=list)
    affected_layers: list[str] = field(default_factory=list)
    ambiguity_residuals: list[CodingResidual] = field(default_factory=list)

    def ensure_consistency(self) -> None:
        if self.task_type == "unknown" and not any(r.residual_type == "ambiguous_issue_scope" for r in self.ambiguity_residuals):
            self.ambiguity_residuals.append(
                CodingResidual(
                    residual_type="ambiguous_issue_scope",
                    severity="warning",
                    message="Issue task type is unknown; certificate is blocked.",
                )
            )

    def to_dict(self) -> dict:
        return {
            "issue_id": self.issue_id,
            "raw_text": self.raw_text,
            "task_type": self.task_type,
            "requested_behavior": self.requested_behavior,
            "observed_behavior": self.observed_behavior,
            "constraints": self.constraints,
            "affected_layers": self.affected_layers,
            "ambiguity_residuals": [r.to_dict() for r in self.ambiguity_residuals],
        }
