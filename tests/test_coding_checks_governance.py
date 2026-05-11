from mcd.coding_copilot.checks_governance import ChecksGovernance


def test_pending_checks_emit_ci_pending():
    governance = ChecksGovernance(checks_total=4, checks_passed=3, checks_failed=0, checks_pending=1)
    residual_types = {item.residual_type for item in governance.residuals()}
    assert "ci_pending" in residual_types
    assert governance.has_pending() is True
    assert governance.all_green() is False


def test_failed_checks_emit_failing_checks():
    governance = ChecksGovernance(checks_total=4, checks_passed=3, checks_failed=1, checks_pending=0)
    residual_types = {item.residual_type for item in governance.residuals()}
    assert "failing_checks" in residual_types
    assert governance.has_failures() is True
    assert governance.all_green() is False


def test_no_checks_emit_missing_check_evidence():
    governance = ChecksGovernance(checks_total=0, checks_passed=0, checks_failed=0, checks_pending=0)
    residual_types = {item.residual_type for item in governance.residuals()}
    assert "missing_check_evidence" in residual_types
    assert governance.all_green() is False
