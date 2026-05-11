import json
from pathlib import Path

from mcd.coding_copilot.merge_governance import MergeGovernanceInput, evaluate_merge_governance
from mcd.coding_copilot.pr_audit import PRAuditInput, audit_pr_fixture


def _base_input(**kwargs) -> MergeGovernanceInput:
    data = {
        "pr_number": 60,
        "merged": False,
        "checks_total": 4,
        "checks_passed": 4,
        "checks_failed": 0,
        "checks_pending": 0,
        "required_checks_configured": True,
        "branch_protection_configured": True,
        "pr_certification_present": True,
        "reverse_trace_complete": True,
    }
    data.update(kwargs)
    return MergeGovernanceInput(**data)


def test_pending_checks_block_epistemic_merge():
    result = evaluate_merge_governance(_base_input(checks_passed=3, checks_pending=1))
    assert result.merge_allowed_epistemically is False
    assert "merge_with_pending_checks" in result.residuals


def test_merge_with_pending_checks_is_hypothesis():
    result = evaluate_merge_governance(_base_input(merged=True, checks_passed=3, checks_pending=1))
    assert result.final_judgment == "HYPOTHESIS"


def test_failed_checks_zero():
    result = evaluate_merge_governance(_base_input(checks_passed=3, checks_failed=1))
    assert result.final_judgment == "ZERO"
    assert result.merge_allowed_epistemically is False


def test_missing_branch_protection_blocks_certificate():
    result = evaluate_merge_governance(_base_input(branch_protection_configured=False))
    assert result.final_judgment == "HYPOTHESIS"
    assert "branch_protection_not_configured" in result.residuals


def test_missing_required_checks_blocks_certificate():
    result = evaluate_merge_governance(_base_input(required_checks_configured=False))
    assert result.final_judgment == "HYPOTHESIS"
    assert "merge_without_required_checks" in result.residuals


def test_missing_pr_certification_blocks_certificate():
    result = evaluate_merge_governance(_base_input(pr_certification_present=False))
    assert result.final_judgment == "HYPOTHESIS"
    assert "merge_without_pr_certification" in result.residuals


def test_certificate_requires_all_merge_gates():
    result = evaluate_merge_governance(_base_input())
    assert result.final_judgment == "CERTIFICATE"
    assert result.merge_allowed_epistemically is True


def test_pr59_fixture_is_hypothesis_due_pending_checks():
    path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "coding_copilot"
        / "real_prs"
        / "pr_59_dogfood_pr_audit.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = audit_pr_fixture(
        PRAuditInput(
            pr_number=payload["pr_number"],
            title=payload["title"],
            merged=payload["merged"],
            checks_total=payload["checks_total"],
            checks_passed=payload["checks_passed"],
            checks_failed=payload["checks_failed"],
            checks_pending=payload["checks_pending"],
            files_changed_count=payload["files_changed_count"],
            commits_count=payload["commits_count"],
            claims=payload["claims"],
            evidence=payload["evidence"],
            residuals=payload.get("residuals", []),
            reverse_trace_complete=all((payload.get("reverse_trace") or {}).values()),
            required_checks_configured=payload.get("required_checks_configured", True),
            branch_protection_configured=payload.get("branch_protection_configured", True),
            pr_certification_present=payload.get("pr_certification_present", True),
        )
    )
    assert result.final_judgment == "HYPOTHESIS"
    assert "ci_pending" in result.residuals
    assert "merge_with_pending_checks" in result.residuals


def test_merged_state_never_upgrades_judgment():
    result = evaluate_merge_governance(_base_input(merged=True, checks_passed=3, checks_pending=1))
    assert result.final_judgment == "HYPOTHESIS"
