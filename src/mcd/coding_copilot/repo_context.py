"""Repository context map required before patch governance."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.coding_copilot.coding_residual import CodingResidual


@dataclass
class RepoContextMap:
    repo_snapshot_id: str
    relevant_files: list[str] = field(default_factory=list)
    relevant_tests: list[str] = field(default_factory=list)
    relevant_docs: list[str] = field(default_factory=list)
    architecture_rules: list[str] = field(default_factory=list)
    dependency_edges: list[dict[str, str]] = field(default_factory=list)
    missing_context: list[str] = field(default_factory=list)
    residuals: list[CodingResidual] = field(default_factory=list)

    def ensure_consistency(self) -> None:
        if not self.relevant_files and not any(r.residual_type == "missing_repo_context" for r in self.residuals):
            self.residuals.append(
                CodingResidual(
                    residual_type="missing_repo_context",
                    severity="blocking",
                    message="No relevant files were identified for this issue.",
                )
            )
        if not self.relevant_tests and not any(r.residual_type == "missing_test_context" for r in self.residuals):
            self.residuals.append(
                CodingResidual(
                    residual_type="missing_test_context",
                    severity="warning",
                    message="No relevant tests were mapped for this issue.",
                )
            )

    def to_dict(self) -> dict:
        return {
            "repo_snapshot_id": self.repo_snapshot_id,
            "relevant_files": self.relevant_files,
            "relevant_tests": self.relevant_tests,
            "relevant_docs": self.relevant_docs,
            "architecture_rules": self.architecture_rules,
            "dependency_edges": self.dependency_edges,
            "missing_context": self.missing_context,
            "residuals": [r.to_dict() for r in self.residuals],
        }
