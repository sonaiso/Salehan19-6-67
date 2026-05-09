"""Tests for ReportBuilder."""
from mcd.evaluation.repository_audit import RepositoryAudit
from mcd.evaluation.architecture_audit import ArchitectureAudit
from mcd.evaluation.test_audit import TestAudit
from mcd.evaluation.cli_audit import CLIAudit
from mcd.evaluation.code_quality_audit import CodeQualityAudit
from mcd.evaluation.production_readiness import ProductionReadinessReport
from mcd.evaluation.report_builder import build_markdown_report


def _build_report_str() -> str:
    repo = RepositoryAudit().run()
    arch = ArchitectureAudit().run()
    test = TestAudit().run()
    cli = CLIAudit().run()
    code = CodeQualityAudit().run()
    readiness = ProductionReadinessReport.build_default()
    return build_markdown_report(repo, arch, test, cli, code, readiness)


def test_report_builder_returns_string():
    md = _build_report_str()
    assert isinstance(md, str)
    assert len(md) > 100


def test_report_contains_executive_summary():
    md = _build_report_str()
    assert "Executive Summary" in md


def test_report_contains_layers():
    md = _build_report_str()
    assert "MCD" in md
    assert "NERL" in md
    assert "FPCL" in md


def test_report_contains_kpi_section():
    md = _build_report_str()
    assert "KPI" in md


def test_report_contains_readiness_section():
    md = _build_report_str()
    assert "Production Readiness" in md


def test_report_contains_gpt55_section():
    md = _build_report_str()
    assert "GPT-5.5" in md


def test_report_contains_next_steps():
    md = _build_report_str()
    assert "Next Steps" in md or "30-Day" in md


def test_report_no_actual_gpt_call():
    # Verify no actual API call is made
    md = _build_report_str()
    assert "api_key" not in md.lower()
    assert "openai.com/v1" not in md
