"""Patch artifact model for diff-level governance."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.coding_copilot.coding_residual import CodingResidual


@dataclass
class PatchArtifact:
    patch_id: str
    changed_files: list[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    touched_layers: list[str] = field(default_factory=list)
    declared_reason: str = ""
    linked_claims: dict[str, list[str]] = field(default_factory=dict)
    residuals: list[CodingResidual] = field(default_factory=list)

    def ensure_consistency(self) -> None:
        if not self.changed_files:
            self.residuals.append(
                CodingResidual(
                    residual_type="unexplained_patch_scope",
                    severity="blocking",
                    message="Patch artifact has no changed files.",
                )
            )
            return

        for file_path in self.changed_files:
            if not self.linked_claims.get(file_path):
                self.residuals.append(
                    CodingResidual(
                        residual_type="unlinked_patch_file",
                        severity="fatal",
                        message=f"Changed file '{file_path}' is not linked to any claim.",
                    )
                )

        if (self.additions + self.deletions) > 500 and not self.declared_reason:
            self.residuals.append(
                CodingResidual(
                    residual_type="unexplained_patch_scope",
                    severity="warning",
                    message="Large patch without declared reason.",
                )
            )

    def to_dict(self) -> dict:
        return {
            "patch_id": self.patch_id,
            "changed_files": self.changed_files,
            "additions": self.additions,
            "deletions": self.deletions,
            "touched_layers": self.touched_layers,
            "declared_reason": self.declared_reason,
            "linked_claims": self.linked_claims,
            "residuals": [r.to_dict() for r in self.residuals],
        }
