from mcd.coding_copilot.pr_audit import PRAuditInput, audit_pr_fixture


def _base_input() -> PRAuditInput:
    return PRAuditInput(
        pr_number=100,
        title="Sample PR",
        merged=True,
        checks_total=4,
        checks_passed=4,
        checks_failed=0,
        checks_pending=0,
        files_changed_count=3,
        commits_count=1,
        claims=[
            {
                "claim_id": "C-1",
                "required_evidence": [
                    "test::PYTHONPATH=src python -m pytest tests/test_coding_pr_audit.py -q",
                    "architecture::governance",
                ],
            }
        ],
        evidence={
            "test_evidence": {
                "test_command": "PYTHONPATH=src python -m pytest tests/test_coding_pr_audit.py -q",
                "passed": True,
                "failures": [],
            },
            "static_evidence": {"tool_name": "ruff", "passed": True, "findings": []},
            "architecture_evidence": {"checked_rules": ["r1"], "violations": [], "passed": True},
        },
        residuals=[],
        reverse_trace_complete=True,
    )


def test_merged_is_not_certificate():
    payload = _base_input()
    payload.checks_pending = 1
    payload.checks_passed = 3
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "HYPOTHESIS"


def test_pending_checks_force_hypothesis():
    payload = _base_input()
    payload.checks_pending = 1
    payload.checks_passed = 3
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "HYPOTHESIS"
    assert "ci_pending" in result.residuals


def test_three_of_four_checks_is_hypothesis():
    payload = _base_input()
    payload.checks_total = 4
    payload.checks_passed = 3
    payload.checks_pending = 1
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "HYPOTHESIS"


def test_failed_required_check_blocks_certificate():
    payload = _base_input()
    payload.checks_passed = 3
    payload.checks_failed = 1
    payload.evidence["failed_required_checks"] = ["build"]
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "ZERO"
    assert result.certificate_allowed is False


def test_all_green_alone_not_certificate():
    payload = _base_input()
    payload.claims = []
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "HYPOTHESIS"
    assert result.certificate_allowed is False


def test_certificate_requires_reverse_trace():
    payload = _base_input()
    payload.reverse_trace_complete = False
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "HYPOTHESIS"


def test_certificate_requires_all_gates():
    payload = _base_input()
    result = audit_pr_fixture(payload)
    assert result.final_judgment == "CERTIFICATE"
