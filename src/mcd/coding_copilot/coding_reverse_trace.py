"""Reverse trace model for governed coding decisions."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodingReverseTrace:
    trace_id: str
    issue_id: str
    repo_snapshot_id: str
    claim_ids: list[str] = field(default_factory=list)
    patch_id: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    test_commands: list[str] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    commit_sha: str = ""
    pr_number: str = ""
    complete: bool = False
    gaps: list[str] = field(default_factory=list)

    def assess_completeness(self) -> None:
        self.gaps = []
        if not self.claim_ids:
            self.gaps.append("missing_claim_ids")
        if not self.patch_id:
            self.gaps.append("missing_patch_id")
        if not self.evidence_ids:
            self.gaps.append("missing_evidence_ids")
        if not self.changed_files:
            self.gaps.append("missing_changed_files")
        if not self.commit_sha:
            self.gaps.append("missing_commit_sha")
        if not self.pr_number:
            self.gaps.append("missing_pr_number")
        self.complete = len(self.gaps) == 0

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "issue_id": self.issue_id,
            "repo_snapshot_id": self.repo_snapshot_id,
            "claim_ids": self.claim_ids,
            "patch_id": self.patch_id,
            "evidence_ids": self.evidence_ids,
            "test_commands": self.test_commands,
            "changed_files": self.changed_files,
            "commit_sha": self.commit_sha,
            "pr_number": self.pr_number,
            "complete": self.complete,
            "gaps": self.gaps,
        }
