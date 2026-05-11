"""Kernel orchestrator for AFJG coding copilot simulation."""
from __future__ import annotations

import uuid

from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.code_claim import CodeClaim
from mcd.coding_copilot.coding_judgment import CodingJudgment, build_coding_judgment
from mcd.coding_copilot.coding_residual import CodingResidual
from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace
from mcd.coding_copilot.issue_understanding import IssueUnderstanding
from mcd.coding_copilot.patch_artifact import PatchArtifact
from mcd.coding_copilot.patch_plan import PatchPlan
from mcd.coding_copilot.repo_context import RepoContextMap
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence


class CodingCopilotKernel:
    """Judgment-only kernel; this phase does not generate code."""

    def understand_issue(self, raw_text: str, issue_id: str | None = None) -> IssueUnderstanding:
        lowered = raw_text.lower()
        task_type = "unknown"
        if any(w in lowered for w in ("bug", "fix", "error", "regression")):
            task_type = "bugfix"
        elif any(w in lowered for w in ("feature", "add", "support")):
            task_type = "feature"
        elif "refactor" in lowered:
            task_type = "refactor"
        elif any(w in lowered for w in ("doc", "readme", "documentation")):
            task_type = "docs"
        elif "test" in lowered:
            task_type = "test"
        elif any(w in lowered for w in ("architecture", "governance")):
            task_type = "architecture"

        issue = IssueUnderstanding(
            issue_id=issue_id or f"ISSUE-{uuid.uuid4().hex[:8]}",
            raw_text=raw_text,
            task_type=task_type,
            requested_behavior=raw_text,
            observed_behavior="",
        )
        issue.ensure_consistency()
        return issue

    def build_repo_context(
        self,
        *,
        repo_snapshot_id: str,
        relevant_files: list[str],
        relevant_tests: list[str] | None = None,
        relevant_docs: list[str] | None = None,
        architecture_rules: list[str] | None = None,
    ) -> RepoContextMap:
        context = RepoContextMap(
            repo_snapshot_id=repo_snapshot_id,
            relevant_files=relevant_files,
            relevant_tests=relevant_tests or [],
            relevant_docs=relevant_docs or [],
            architecture_rules=architecture_rules or [],
        )
        context.ensure_consistency()
        return context

    def create_code_claim(
        self,
        *,
        claim_id: str,
        claim_type: str,
        affected_files: list[str],
        expected_effect: str,
        risk_level: str = "medium",
        required_evidence: list[str] | None = None,
    ) -> CodeClaim:
        return CodeClaim(
            claim_id=claim_id,
            claim_type=claim_type,
            affected_files=affected_files,
            expected_effect=expected_effect,
            risk_level=risk_level,
            required_evidence=required_evidence or [],
        )

    def create_patch_plan(
        self,
        *,
        plan_id: str,
        claims: list[CodeClaim],
        steps: list[str],
        expected_tests: list[str],
        rollback_plan: str,
        forbidden_paths: list[str] | None = None,
        task_type: str = "unknown",
    ) -> PatchPlan:
        plan = PatchPlan(
            plan_id=plan_id,
            claims=claims,
            steps=steps,
            expected_tests=expected_tests,
            rollback_plan=rollback_plan,
            forbidden_paths=forbidden_paths or [],
        )
        plan.ensure_consistency(task_type=task_type)
        return plan

    def evaluate_patch(
        self,
        *,
        patch_id: str,
        changed_files: list[str],
        additions: int,
        deletions: int,
        touched_layers: list[str],
        declared_reason: str,
        linked_claims: dict[str, list[str]],
        test_evidence: TestEvidence | None,
        static_evidence: StaticEvidence | None,
        architecture_evidence: ArchitectureEvidence | None,
    ) -> tuple[PatchArtifact, list[CodingResidual]]:
        patch = PatchArtifact(
            patch_id=patch_id,
            changed_files=changed_files,
            additions=additions,
            deletions=deletions,
            touched_layers=touched_layers,
            declared_reason=declared_reason,
            linked_claims=linked_claims,
        )
        patch.ensure_consistency()
        residuals = list(patch.residuals)

        if test_evidence and not test_evidence.passed:
            residuals.append(CodingResidual("failing_tests", "fatal", "Test evidence failed."))
        if static_evidence and not static_evidence.passed:
            residuals.append(CodingResidual("static_check_failure", "warning", "Static tool findings present."))
        if architecture_evidence and (not architecture_evidence.passed or architecture_evidence.violations):
            residuals.append(CodingResidual("architecture_violation", "fatal", "Architecture violations found."))

        return patch, residuals

    def decide(
        self,
        *,
        issue: IssueUnderstanding,
        repo_context: RepoContextMap,
        claims: list[CodeClaim],
        patch_plan: PatchPlan,
        patch_artifact: PatchArtifact,
        test_evidence: TestEvidence | None,
        static_evidence: StaticEvidence | None,
        architecture_evidence: ArchitectureEvidence | None,
        reverse_trace: CodingReverseTrace | None,
        residuals: list[CodingResidual] | None = None,
        allow_local_certificate_candidate: bool = False,
    ) -> CodingJudgment:
        return build_coding_judgment(
            issue=issue,
            repo_context=repo_context,
            claims=claims,
            patch_plan=patch_plan,
            patch_artifact=patch_artifact,
            test_evidence=test_evidence,
            static_evidence=static_evidence,
            architecture_evidence=architecture_evidence,
            reverse_trace=reverse_trace,
            residuals=residuals or [],
            allow_local_certificate_candidate=allow_local_certificate_candidate,
        )

    def produce_report(self, judgment: CodingJudgment) -> dict:
        return judgment.to_dict()
