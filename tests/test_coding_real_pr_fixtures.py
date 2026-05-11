import json
from pathlib import Path

from mcd.coding_copilot.pr_audit import PRAuditInput, audit_pr_fixture


def _fixture_to_input(payload: dict) -> PRAuditInput:
    reverse_trace = payload.get("reverse_trace") or {}
    reverse_trace_complete = bool(
        reverse_trace.get("complete")
        if "complete" in reverse_trace
        else all(reverse_trace.values()) if reverse_trace else False
    )
    return PRAuditInput(
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
        reverse_trace_complete=reverse_trace_complete,
    )


def test_pr57_expected_hypothesis_due_pending_check():
    path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "coding_copilot"
        / "real_prs"
        / "pr_57_phase0_constitution.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = audit_pr_fixture(_fixture_to_input(payload))
    assert result.final_judgment == "HYPOTHESIS"
    assert "ci_pending" in result.residuals


def test_pr58_expected_hypothesis_due_three_of_four_checks():
    path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "coding_copilot"
        / "real_prs"
        / "pr_58_coding_copilot_kernel.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = audit_pr_fixture(_fixture_to_input(payload))
    assert result.final_judgment == "HYPOTHESIS"
    assert "ci_pending" in result.residuals


def test_real_pr_fixtures_validate():
    root = Path(__file__).resolve().parents[1] / "examples" / "coding_copilot" / "real_prs"
    files = sorted(root.glob("*.json"))
    assert len(files) == 3
    required = {
        "pr_number",
        "title",
        "merged",
        "checks_total",
        "checks_passed",
        "checks_failed",
        "checks_pending",
        "files_changed_count",
        "commits_count",
        "summary",
        "affected_layers",
        "claims",
        "evidence",
        "residuals",
        "reverse_trace",
        "expected_final_judgment",
    }
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert required.issubset(payload.keys())
        result = audit_pr_fixture(_fixture_to_input(payload))
        assert result.final_judgment == payload["expected_final_judgment"]
