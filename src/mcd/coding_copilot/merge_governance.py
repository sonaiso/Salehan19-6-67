"""Hard merge-governance rules for coding copilot PR certification."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MergeGovernanceInput:
    pr_number: int
    merged: bool
    checks_total: int
    checks_passed: int
    checks_failed: int
    checks_pending: int
    required_checks_configured: bool
    branch_protection_configured: bool
    pr_certification_present: bool
    reverse_trace_complete: bool


@dataclass
class MergeGovernanceResult:
    merge_allowed_epistemically: bool
    final_judgment: str
    residuals: list[str] = field(default_factory=list)
    reason: str = ""
    required_actions: list[str] = field(default_factory=list)


_CERTIFICATE_GATES = (
    "checks_pending == 0",
    "checks_failed == 0",
    "checks_passed == checks_total",
    "checks_total > 0",
    "branch_protection_configured == true",
    "required_checks_configured == true",
    "pr_certification_present == true",
    "reverse_trace_complete == true",
)


def evaluate_merge_governance(governance_input: MergeGovernanceInput) -> MergeGovernanceResult:
    if governance_input.checks_pending > 0:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="HYPOTHESIS",
            residuals=["merge_with_pending_checks"],
            reason="pending_checks",
            required_actions=["Wait for all required checks to complete before merge."],
        )

    if governance_input.checks_failed > 0:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="ZERO",
            residuals=["failing_checks"],
            reason="failing_checks",
            required_actions=["Fix failing required checks before merge."],
        )

    if governance_input.checks_total == 0:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="HYPOTHESIS",
            residuals=["missing_check_evidence"],
            reason="missing_check_evidence",
            required_actions=["Configure and run required checks for the PR."],
        )

    if not governance_input.branch_protection_configured:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="HYPOTHESIS",
            residuals=["branch_protection_not_configured"],
            reason="branch_protection_not_configured",
            required_actions=["Enable branch protection/ruleset on the target branch."],
        )

    if not governance_input.required_checks_configured:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="HYPOTHESIS",
            residuals=["merge_without_required_checks"],
            reason="required_checks_not_configured",
            required_actions=["Mark AFJG checks as required in branch protection."],
        )

    if not governance_input.pr_certification_present:
        return MergeGovernanceResult(
            merge_allowed_epistemically=False,
            final_judgment="HYPOTHESIS",
            residuals=["merge_without_pr_certification"],
            reason="pr_certification_missing",
            required_actions=["Require PR certification status check before merge."],
        )

    certificate_ready = (
        governance_input.checks_pending == 0
        and governance_input.checks_failed == 0
        and governance_input.checks_total > 0
        and governance_input.checks_passed == governance_input.checks_total
        and governance_input.branch_protection_configured
        and governance_input.required_checks_configured
        and governance_input.pr_certification_present
        and governance_input.reverse_trace_complete
    )
    if certificate_ready:
        return MergeGovernanceResult(
            merge_allowed_epistemically=True,
            final_judgment="CERTIFICATE",
            residuals=[],
            reason="all_merge_gates_passed",
            required_actions=[],
        )

    return MergeGovernanceResult(
        merge_allowed_epistemically=False,
        final_judgment="HYPOTHESIS",
        residuals=["insufficient_evidence"],
        reason="merge_gates_incomplete",
        required_actions=[f"Satisfy certificate gates: {', '.join(_CERTIFICATE_GATES)}"],
    )
