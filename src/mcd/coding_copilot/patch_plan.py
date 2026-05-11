"""Patch planning contract for governed coding changes."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.coding_copilot.coding_residual import CodingResidual
from mcd.coding_copilot.code_claim import CodeClaim


@dataclass
class PatchPlan:
    plan_id: str
    claims: list[CodeClaim]
    steps: list[str] = field(default_factory=list)
    forbidden_paths: list[str] = field(default_factory=list)
    expected_tests: list[str] = field(default_factory=list)
    rollback_plan: str = ""
    residuals: list[CodingResidual] = field(default_factory=list)

    def ensure_consistency(self, *, task_type: str = "unknown") -> None:
        if not self.rollback_plan:
            self.residuals.append(
                CodingResidual(
                    residual_type="insufficient_evidence",
                    severity="warning",
                    message="Patch plan has no rollback plan.",
                )
            )
        if task_type != "docs" and not self.expected_tests and not any(r.residual_type == "missing_expected_tests" for r in self.residuals):
            self.residuals.append(
                CodingResidual(
                    residual_type="missing_expected_tests",
                    severity="warning",
                    message="No expected tests declared for non-docs task.",
                )
            )

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "claims": [c.to_dict() for c in self.claims],
            "steps": self.steps,
            "forbidden_paths": self.forbidden_paths,
            "expected_tests": self.expected_tests,
            "rollback_plan": self.rollback_plan,
            "residuals": [r.to_dict() for r in self.residuals],
        }
