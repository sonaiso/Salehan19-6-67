"""Audit real PR fixtures with AFJG coding governance."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.coding_copilot.checks_governance import ChecksGovernance

BLOCKING_RESIDUAL_TYPES = {"ci_pending", "failing_checks", "missing_check_evidence", "architecture_violation"}


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


def _has_fatal_failure(evidence: dict[str, Any], residuals: list[str]) -> bool:
    if "required_check_failed" in residuals:
        return True
    if "fatal_check_failure" in residuals:
        return True
    failed_required = evidence.get("failed_required_checks")
    if isinstance(failed_required, list) and len(failed_required) > 0:
        return True
    return bool(evidence.get("fatal_failure", False))


def _build_result(
    pr_input: PRAuditInput,
    *,
    judgment: str,
    residuals: list[str],
    reason: str,
) -> PRAuditResult:
    merged_note = "merged" if pr_input.merged else "not_merged"
    report = (
        f"pr={pr_input.pr_number}; judgment={judgment}; reason={reason}; "
        f"{merged_note}; certificate_allowed={judgment == 'CERTIFICATE'}"
    )
    return PRAuditResult(
        pr_number=pr_input.pr_number,
        final_judgment=judgment,
        residuals=residuals,
        certificate_allowed=judgment == "CERTIFICATE",
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
    for residual in checks.residuals():
        if residual.residual_type not in residual_types:
            residual_types.append(residual.residual_type)

    if checks.has_pending():
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="ci_pending",
        )

    if checks.has_failures():
        fatal_failure = _has_fatal_failure(pr_input.evidence, residual_types)
        return _build_result(
            pr_input,
            judgment="ZERO" if fatal_failure else "HYPOTHESIS",
            residuals=residual_types,
            reason="failing_checks_required" if fatal_failure else "failing_checks_nonfatal",
        )

    if pr_input.checks_total == 0:
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="missing_check_evidence",
        )

    if not checks.all_green():
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="checks_not_all_green",
        )

    if not pr_input.reverse_trace_complete:
        if "insufficient_evidence" not in residual_types:
            residual_types.append("insufficient_evidence")
        return _build_result(
            pr_input,
            judgment="HYPOTHESIS",
            residuals=residual_types,
            reason="reverse_trace_incomplete",
        )

    if not _claims_have_matching_evidence(pr_input.claims, pr_input.evidence):
        if "insufficient_evidence" not in residual_types:
            residual_types.append("insufficient_evidence")
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
