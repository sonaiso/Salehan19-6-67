"""Tests for ArchitectureAudit."""
from mcd.evaluation.architecture_audit import ArchitectureAudit, ArchitectureAuditResult


def test_architecture_audit_runs():
    audit = ArchitectureAudit()
    result = audit.run()
    assert isinstance(result, ArchitectureAuditResult)


def test_architecture_scores_in_range():
    audit = ArchitectureAudit()
    result = audit.run()
    for score in [
        result.layer_separation_score,
        result.modularity_score,
        result.dependency_risk_score,
        result.deterministic_core_score,
        result.integration_score,
        result.overall_score,
    ]:
        assert 0.0 <= score <= 1.0, f"Score out of range: {score}"


def test_architecture_overall_score_acceptable():
    audit = ArchitectureAudit()
    result = audit.run()
    assert result.overall_score >= 0.40, f"Architecture score too low: {result.overall_score}"


def test_architecture_maturity_label():
    audit = ArchitectureAudit()
    result = audit.run()
    label = result.maturity_label()
    assert label in ("strong", "acceptable prototype", "research prototype", "weak")


def test_architecture_no_llm_in_classifiers():
    audit = ArchitectureAudit()
    result = audit.run()
    assert result.deterministic_core_score >= 0.9, "LLM dependency detected in classifiers"


def test_architecture_findings_list():
    audit = ArchitectureAudit()
    result = audit.run()
    assert isinstance(result.findings, list)
    assert isinstance(result.risks, list)
    assert isinstance(result.recommendations, list)
