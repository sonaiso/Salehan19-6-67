"""Final judgment contract and decision law for coding copilot simulation."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.code_claim import CodeClaim
from mcd.coding_copilot.coding_residual import CodingResidual
from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace
from mcd.coding_copilot.coding_status import CodingStatus, collapse_to_public_status
from mcd.coding_copilot.issue_understanding import IssueUnderstanding
from mcd.coding_copilot.patch_artifact import PatchArtifact
from mcd.coding_copilot.patch_plan import PatchPlan
from mcd.coding_copilot.repo_context import RepoContextMap
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence


@dataclass
class CodingJudgment:
    judgment_id: str
    issue: IssueUnderstanding
    repo_context: RepoContextMap
    claims: list[CodeClaim]
    patch_plan: PatchPlan
    patch_artifact: PatchArtifact
    test_evidence: TestEvidence | None = None
    static_evidence: StaticEvidence | None = None
    architecture_evidence: ArchitectureEvidence | None = None
    residuals: list[CodingResidual] = field(default_factory=list)
    reverse_trace: CodingReverseTrace | None = None
    final_judgment: str = CodingStatus.HYPOTHESIS.value
    public_report: str = ""

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "issue": self.issue.to_dict(),
            "repo_context": self.repo_context.to_dict(),
            "claims": [c.to_dict() for c in self.claims],
            "patch_plan": self.patch_plan.to_dict(),
            "patch_artifact": self.patch_artifact.to_dict(),
            "test_evidence": self.test_evidence.to_dict() if self.test_evidence else None,
            "static_evidence": self.static_evidence.to_dict() if self.static_evidence else None,
            "architecture_evidence": self.architecture_evidence.to_dict() if self.architecture_evidence else None,
            "residuals": [r.to_dict() for r in self.residuals],
            "reverse_trace": self.reverse_trace.to_dict() if self.reverse_trace else None,
            "final_judgment": self.final_judgment,
            "public_report": self.public_report,
        }


def decide_final_judgment(
    *,
    issue: IssueUnderstanding,
    claims: list[CodeClaim],
    patch_artifact: PatchArtifact,
    test_evidence: TestEvidence | None,
    static_evidence: StaticEvidence | None,
    architecture_evidence: ArchitectureEvidence | None,
    reverse_trace: CodingReverseTrace | None,
    residuals: list[CodingResidual],
    allow_local_certificate_candidate: bool = False,
) -> str:
    """Apply AFJG coding law to collapse decision into ZERO/HYPOTHESIS/CERTIFICATE."""
    fatal_exists = any(r.severity == "fatal" for r in residuals)
    if fatal_exists:
        return CodingStatus.ZERO.value
    blocking_types = {r.residual_type for r in residuals if r.severity == "blocking"}
    if blocking_types:
        if blocking_types.issubset({"ci_pending", "insufficient_evidence", "missing_expected_tests", "missing_test_context"}):
            return CodingStatus.HYPOTHESIS.value
        return CodingStatus.ZERO.value

    if issue.task_type == "unknown":
        return CodingStatus.HYPOTHESIS.value

    if not claims:
        return CodingStatus.ZERO.value

    if any(r.residual_type == "unlinked_patch_file" for r in residuals):
        return CodingStatus.ZERO.value

    if any(r.residual_type == "summary_as_proof" for r in residuals):
        return CodingStatus.ZERO.value

    if architecture_evidence and (not architecture_evidence.passed or architecture_evidence.violations):
        return CodingStatus.ZERO.value

    if test_evidence is None:
        return CodingStatus.HYPOTHESIS.value

    if not test_evidence.passed or test_evidence.failures:
        return CodingStatus.ZERO.value

    if static_evidence is not None and not static_evidence.passed:
        return CodingStatus.HYPOTHESIS.value

    if reverse_trace is None:
        return CodingStatus.ZERO.value

    reverse_trace.assess_completeness()
    if not reverse_trace.complete:
        if allow_local_certificate_candidate:
            if reverse_trace.gaps and set(reverse_trace.gaps).issubset({"missing_commit_sha", "missing_pr_number"}):
                return CodingStatus.CERTIFICATE.value
        return CodingStatus.HYPOTHESIS.value

    return CodingStatus.CERTIFICATE.value


def build_coding_judgment(
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
    residuals: list[CodingResidual],
    allow_local_certificate_candidate: bool = False,
) -> CodingJudgment:
    issue.ensure_consistency()
    repo_context.ensure_consistency()
    patch_plan.ensure_consistency(task_type=issue.task_type)
    patch_artifact.ensure_consistency()

    all_residuals = list(residuals)
    all_residuals.extend(issue.ambiguity_residuals)
    all_residuals.extend(repo_context.residuals)
    all_residuals.extend(patch_plan.residuals)
    all_residuals.extend(patch_artifact.residuals)

    if reverse_trace is None:
        all_residuals.append(CodingResidual("no_reverse_trace", "fatal", "Patch has no reverse trace."))

    if test_evidence is not None and not test_evidence.passed:
        all_residuals.append(CodingResidual("failing_tests", "fatal", "Tests failed for proposed patch."))

    if static_evidence is not None and not static_evidence.passed:
        all_residuals.append(CodingResidual("static_check_failure", "warning", "Static checks reported findings."))

    if architecture_evidence is not None and (not architecture_evidence.passed or architecture_evidence.violations):
        all_residuals.append(CodingResidual("architecture_violation", "fatal", "Architecture checks reported violations."))

    if test_evidence is None:
        all_residuals.append(CodingResidual("insufficient_evidence", "warning", "No test evidence was supplied."))

    final = decide_final_judgment(
        issue=issue,
        claims=claims,
        patch_artifact=patch_artifact,
        test_evidence=test_evidence,
        static_evidence=static_evidence,
        architecture_evidence=architecture_evidence,
        reverse_trace=reverse_trace,
        residuals=all_residuals,
        allow_local_certificate_candidate=allow_local_certificate_candidate,
    )
    final = collapse_to_public_status(final)

    report = f"coding_judgment={final}; residuals={len(all_residuals)}"

    return CodingJudgment(
        judgment_id=f"CJ-{uuid.uuid4().hex[:12]}",
        issue=issue,
        repo_context=repo_context,
        claims=claims,
        patch_plan=patch_plan,
        patch_artifact=patch_artifact,
        test_evidence=test_evidence,
        static_evidence=static_evidence,
        architecture_evidence=architecture_evidence,
        residuals=all_residuals,
        reverse_trace=reverse_trace,
        final_judgment=final,
        public_report=report,
    )
