from datetime import datetime

from mcd.coding_copilot.pr_certification import PRCertification


def _base_cert(**kwargs) -> PRCertification:
    data = {
        "pr_number": 60,
        "certified_by": "afjg-pr-certification",
        "judgment": "CERTIFICATE",
        "checks_summary": {"checks_total": 4, "checks_passed": 4, "checks_failed": 0, "checks_pending": 0},
        "residuals": [],
        "reverse_trace_complete": True,
        "certificate_allowed": True,
    }
    data.update(kwargs)
    return PRCertification(**data)


def test_hypothesis_is_not_merge_certificate():
    cert = _base_cert(judgment="HYPOTHESIS", reverse_trace_complete=True)
    assert cert.reverse_trace_complete is True
    assert cert.certificate_allowed is False


def test_certificate_with_no_blocking_residual_is_allowed():
    cert = _base_cert()
    assert cert.certificate_allowed is True


def test_ci_pending_blocks_certificate():
    cert = _base_cert(residuals=["ci_pending"])
    assert cert.certificate_allowed is False


def test_merge_with_pending_checks_blocks_certificate():
    cert = _base_cert(residuals=["merge_with_pending_checks"])
    assert cert.certificate_allowed is False


def test_created_at_is_populated_and_ordered():
    first = _base_cert()
    second = _base_cert()
    first_ts = datetime.fromisoformat(first.created_at)
    second_ts = datetime.fromisoformat(second.created_at)
    assert second_ts >= first_ts
