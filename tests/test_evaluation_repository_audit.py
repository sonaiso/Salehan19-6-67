"""Tests for RepositoryAudit."""
from mcd.evaluation.repository_audit import RepositoryAudit, RepositoryAuditResult


def test_repository_audit_runs():
    audit = RepositoryAudit()
    result = audit.run()
    assert isinstance(result, RepositoryAuditResult)


def test_repository_audit_detects_src_files():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.src_file_count > 0


def test_repository_audit_detects_test_files():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.test_file_count > 0


def test_repository_audit_cli_detected():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.cli_detected is True


def test_repository_audit_readme_detected():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.readme_detected is True


def test_repository_audit_pyproject_detected():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.pyproject_detected is True


def test_repository_audit_packages_detected():
    audit = RepositoryAudit()
    result = audit.run()
    assert len(result.packages_detected) > 0


def test_repository_audit_has_findings():
    audit = RepositoryAudit()
    result = audit.run()
    assert isinstance(result.findings, list)


def test_repository_audit_status_is_valid():
    audit = RepositoryAudit()
    result = audit.run()
    assert result.status in ("pass", "warning", "fail")


def test_repository_audit_expected_layers_present():
    audit = RepositoryAudit()
    result = audit.run()
    expected = {"core", "engines", "knowledge", "nabhani", "classification"}
    detected = set(result.packages_detected)
    missing = expected - detected
    assert not missing, f"Missing packages: {missing}"
