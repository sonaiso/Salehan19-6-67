"""Residual model for coding copilot governance gaps."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ResidualType = Literal[
    "ambiguous_issue_scope",
    "missing_repo_context",
    "missing_test_context",
    "missing_expected_tests",
    "unlinked_patch_file",
    "unexplained_patch_scope",
    "failing_tests",
    "static_check_failure",
    "architecture_violation",
    "no_reverse_trace",
    "summary_as_proof",
    "copilot_output_as_evidence",
    "ci_pending",
    "insufficient_evidence",
]

ResidualSeverity = Literal["info", "warning", "blocking", "fatal"]


@dataclass
class CodingResidual:
    residual_type: ResidualType
    severity: ResidualSeverity = "warning"
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "residual_type": self.residual_type,
            "severity": self.severity,
            "message": self.message,
        }
