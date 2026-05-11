"""Audit real PR fixtures with AFJG coding governance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.coding_copilot.checks_governance import ChecksGovernance
from mcd.coding_copilot.merge_governance import MergeGovernanceInput, evaluate_merge_governance
from mcd.coding_copilot.pr_certification import PRCertification

BLOCKING_RESIDUAL_TYPES = {
    "ci_pending",
    "failing_checks",
    "missing_check_evidence",
    "architecture_violation",
    "merge_with_pending_checks",
    "merge_without_required_checks",
    "merge_without_pr_certification",
    "branch_protection_not_configured",
}


@dataclass
class PRAuditInput:
    pr_number: int
    title: str
    merged: bool
    checks_total: int
    checks_passed: int
    checks_failed: int
    checks_pending: int
    files_changed_count: int
    commits_count: int
    claims: list[dict[str, Any]] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    residuals: list[dict[str, Any] | str] = field(default_factory=list)
    reverse_trace_complete: bool = False
    required_checks_configured: bool = True
    branch_protection_configured: bool = True
    pr_certification_present: bool = True


@dataclass
class PRAuditResult:
    pr_number: int
    final_judgment: str
    residuals: list[str]
    certificate_allowed: bool
    reason: str
    public_report: str


def _normalize_residual_types(residuals: list[dict[str, Any] | str]) -> list[str]:
    normalized: list[str] = []
    for item in residuals:
        if isinstance(item, str):
            residual_type = item.strip()
        else:
            residual_type = str(item.get("residual_type", "")).strip()
        if residual_type and residual_type not in normalized:
            normalized.append(residual_type)
    return normalized


def _append_unique(items: list[str], seen: set[str], value: str) -> None:
    normalized = (value or "").strip()
    if normalized and normalized not in seen:
        items.append(normalized)
        seen.add(normalized)


def _claims_have_matching_evidence(claims: list[dict[str, Any]], evidence: dict[str, Any]) -> bool:
    if not claims:
        return False
    evidence_ids: set[str] = set()
    extra = evidence.get("evidence_ids")
    if isinstance(extra, list):
        evidence_ids.update(str(i) for i in extra if i)

    test_evidence = evidence.get("test_evidence") or {}
    test_command = test_evidence.get("test_command")
    if test_command:
        evidence_ids.add(f"test::{test_command}")

    static_evidence = evidence.get("static_evidence") or {}
    tool_name = static_evidence.get("tool_name")
    if tool_name:
        evidence_ids.add(f"static::{tool_name}")

    architecture_evidence = evidence.get("architecture_evidence") or {}
    if architecture_evidence:
        evidence_ids.add("architecture::governance")

    for claim in claims:
        required = claim.get("required_evidence") or []
        if any(req not in evidence_ids for req in required):
            return False
    return True


def _build_result(
    pr_input: PRAuditInput,
    *,
    judgment: str,
    residuals: list[str],
    reason: str,
) -> PRAuditResult:
    certification = PRCertification(
        pr_number=pr_input.pr_number,
        certified_by="audit_pr_fixture",
        judgment=judgment,
        checks_summary={
            "checks_total": pr_input.checks_total,
            "checks_passed": pr_input.checks_passed,
            "checks_failed": pr_input.checks_failed,
            "checks_pending": pr_input.checks_pending,
        },
        residuals=residuals,
        reverse_trace_complete=pr_input.reverse_trace_complete,
    )
    merged_note = "merged" if pr_input.merged else "not_merged"
    report = (
        f"pr={pr_input.pr_number}; judgment={judgment}; reason={reason}; "
        f"{merged_note}; certificate_allowed={certification.certificate_allowed}"
    )
    return PRAuditResult(
        pr_number=pr_input.pr_number,
        final_judgment=judgment,
        residuals=residuals,
        certificate_allowed=certification.certificate_allowed,
        reason=reason,
        public_report=report,
    )


def audit_pr_fixture(pr_input: PRAuditInput) -> PRAuditResult:
    checks = ChecksGovernance(
        checks_total=pr_input.checks_total,
        checks_passed=pr_input.checks_passed,
        checks_failed=pr_input.checks_failed,
        checks_pending=pr_input.checks_pending,
    )
    residual_types = _normalize_residual_types(pr_input.residuals)
    residual_seen = set(residual_types)
    for residual in checks.residuals():
        _append_unique(residual_types, residual_seen, residual.residual_type)

    merge_governance = evaluate_merge_governance(
        MergeGovernanceInput(
            pr_number=pr_input.pr_number,
            merged=pr_input.merged,
            checks_total=pr_input.checks_total,
            checks_passed=pr_input.checks_passed,
            checks_failed=pr_input.checks_failed,
            checks_pending=pr_input.checks_pending,
            required_checks_configured=pr_input.required_checks_configured,
            branch_protection_configured=pr_input.branch_protection_configured,
            pr_certification_present=pr_input.pr_certification_present,
            reverse_trace_complete=pr_input.reverse_trace_complete,
        )
    )

    for residual in merge_governance.residuals:
        _append_unique(residual_types, residual_seen, residual)

    if merge_governance.final_judgment != "CERTIFICATE":
        return _build_result(
            pr_input,
            judgment=merge_governance.final_judgment,
            residuals=residual_types,
            reason=merge_governance.reason,
        )

    if not pr_input.reverse_trace_complete:
        _append_unique(residual_types, residual_seen, "insufficient_evidence")
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="reverse_trace_incomplete",
        )

    if not _claims_have_matching_evidence(pr_input.claims, pr_input.evidence):
        _append_unique(residual_types, residual_seen, "insufficient_evidence")
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="claims_evidence_mismatch",
        )

    if any(item in BLOCKING_RESIDUAL_TYPES for item in residual_types):
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="blocking_residual_present",
        )

    return _build_result(
        pr_input,
        judgment="CERTIFICATE",
        residuals=residual_types,
        reason="all_certificate_gates_passed",
    )
