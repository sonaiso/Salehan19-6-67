"""Tests for Phase 5.2 — Pre-API Qualification Gate."""
from __future__ import annotations

import json

import pytest

from mcd.industrial.pre_api_qualification import (
    PreAPIQualificationGate,
    PreAPIQualificationReport,
    PreAPIQualificationDimension,
    render_markdown,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gate_with_all_passing(tests_pass: bool = True) -> PreAPIQualificationReport:
    """Return a report built with best-case inputs so all non-API dims pass."""
    gate = PreAPIQualificationGate()
    # Provide a calibration result with very low false_certainty_rate
    calibration_result = {
        "false_certainty_rate": 0.01,
        "suspension_precision": 0.95,
        "certainty_policy_accuracy": 0.97,
    }
    # Industrial result with high pass rate
    industrial_result = {
        "pass_rate": 0.95,
        "false_certainty_rate": 0.01,
        "injection_detection": 0.95,
        "source_required_detection": 0.95,
    }
    trust_result = {
        "injection_detection": 0.95,
        "source_required_detection": 0.95,
    }
    coverage_report = {"coverage_score": 0.93}
    # Pre-computed dataset metrics: no duplicates, no field violations
    dataset_metrics = {
        "total_examples": 546,
        "duplicate_count": 0,
        "field_violations": 0,
    }
    return gate.evaluate(
        tests_pass=tests_pass,
        readiness_report_exists=True,
        calibration_result=calibration_result,
        industrial_result=industrial_result,
        trust_result=trust_result,
        coverage_report=coverage_report,
        dataset_metrics=dataset_metrics,
        schema_stability=0.99,
        latency_target_ms=1000.0,
    )


# ---------------------------------------------------------------------------
# Required tests
# ---------------------------------------------------------------------------


def test_pre_api_blocks_if_non_api_dimension_below_45():
    """If any non-API dimension is below 4.5, status must be blocked_before_api."""
    gate = PreAPIQualificationGate()
    # tests_pass=None → test_score capped at 4.3 (below 4.5)
    report = gate.evaluate(tests_pass=None)
    assert report.status == "blocked_before_api"
    assert not report.non_api_passed

    # Verify that test_score dimension is in the failed set
    test_dim = next(d for d in report.dimensions if d.name == "test_score")
    assert not test_dim.passed
    assert test_dim.score < 4.5


def test_pre_api_allows_api_score_below_45():
    """api_score below 4.5 must NOT cause blocked_before_api status."""
    gate = PreAPIQualificationGate()
    report = _gate_with_all_passing(tests_pass=True)

    api_dim = next(d for d in report.dimensions if d.name == "api_score")
    assert api_dim.score < 4.5  # API is 0.0 — not yet implemented

    # The gate must not block qualification because of api_score
    # (It may still be blocked for other reasons, but api_score is not the cause)
    # Check that api_score is excluded from non_api_passed logic
    non_api_names = PreAPIQualificationGate.NON_API_DIMENSIONS
    assert "api_score" not in non_api_names


def test_pre_api_requires_tests_pass_for_test_score_45():
    """test_score must not reach 4.5 unless tests_pass=True is explicitly provided."""
    gate = PreAPIQualificationGate()

    # Without tests_pass
    report_no_flag = gate.evaluate(tests_pass=None)
    test_dim_no_flag = next(d for d in report_no_flag.dimensions if d.name == "test_score")
    assert test_dim_no_flag.score < 4.5, "test_score must be capped below 4.5 when tests_pass is not confirmed"

    # With tests_pass=False
    report_false = gate.evaluate(tests_pass=False)
    test_dim_false = next(d for d in report_false.dimensions if d.name == "test_score")
    assert test_dim_false.score < 4.5

    # With tests_pass=True
    report_true = gate.evaluate(tests_pass=True)
    test_dim_true = next(d for d in report_true.dimensions if d.name == "test_score")
    assert test_dim_true.score >= 4.5


def test_pre_api_caps_latency_without_target():
    """latency_score must not exceed 4.4 when latency_target_ms is not provided."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate(latency_target_ms=None)
    latency_dim = next(d for d in report.dimensions if d.name == "latency_score")
    assert latency_dim.score <= 4.4, (
        f"latency_score={latency_dim.score} should be ≤ 4.4 when target is absent"
    )
    assert not latency_dim.passed


def test_pre_api_caps_dataset_without_coverage():
    """dataset_score must not exceed 4.4 when no coverage_report is provided."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate(coverage_report=None)
    dataset_dim = next(d for d in report.dimensions if d.name == "dataset_score")
    assert dataset_dim.score <= 4.4, (
        f"dataset_score={dataset_dim.score} should be ≤ 4.4 without coverage proof"
    )
    assert not dataset_dim.passed


def test_pre_api_qualified_when_all_non_api_above_45():
    """When all non-API dimensions score ≥ 4.5, status must be qualified_for_api_phase."""
    report = _gate_with_all_passing(tests_pass=True)

    # Verify every non-API dimension passed
    for dim in report.dimensions:
        if dim.name == "api_score":
            continue
        assert dim.passed, (
            f"{dim.name} scored {dim.score:.2f} — expected ≥ 4.5 with best-case inputs"
        )

    assert report.non_api_passed
    assert report.status == "qualified_for_api_phase"
    assert report.average_non_api_score >= 4.5


def test_pre_api_markdown_contains_go_no_go():
    """Markdown output must contain a Go / No-Go section."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate(tests_pass=None)  # Some dims will fail
    md = render_markdown(report)

    assert "## 9. Go / No-Go" in md
    assert "## 10. Next Phase Recommendation" in md
    assert "Pre-API Qualification Report" in md

    # Qualified case
    report_ok = _gate_with_all_passing(tests_pass=True)
    md_ok = render_markdown(report_ok)
    assert "GO" in md_ok or "QUALIFIED" in md_ok


def test_pre_api_json_serializable():
    """The report must be fully JSON-serializable."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate(tests_pass=True)

    report_dict = report.to_dict()
    serialized = json.dumps(report_dict, ensure_ascii=False)
    deserialized = json.loads(serialized)

    assert deserialized["status"] in {"blocked_before_api", "qualified_for_api_phase"}
    assert isinstance(deserialized["dimensions"], list)
    assert isinstance(deserialized["average_non_api_score"], float)
    assert isinstance(deserialized["api_score"], float)
    assert isinstance(deserialized["non_api_passed"], bool)
    assert isinstance(deserialized["blockers"], list)
    assert isinstance(deserialized["required_fixes_before_api"], list)
    assert isinstance(deserialized["summary"], str)

    # Each dimension must have the right keys
    for dim in deserialized["dimensions"]:
        assert "name" in dim
        assert "score" in dim
        assert "threshold" in dim
        assert "passed" in dim
        assert "evidence" in dim
        assert "blockers" in dim
        assert "next_actions" in dim


# ---------------------------------------------------------------------------
# Additional correctness tests
# ---------------------------------------------------------------------------


def test_api_score_always_zero_or_one():
    """api_score must be 0.0 (REST API not implemented)."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate()
    assert report.api_score == 0.0


def test_status_values_are_valid():
    """status must be one of the two valid values."""
    gate = PreAPIQualificationGate()
    for flag in [None, True, False]:
        report = gate.evaluate(tests_pass=flag)
        assert report.status in {"blocked_before_api", "qualified_for_api_phase"}


def test_dimensions_count():
    """Report must contain exactly 11 dimensions."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate()
    assert len(report.dimensions) == 11


def test_non_api_dimensions_list_excludes_api():
    """NON_API_DIMENSIONS must not include api_score."""
    assert "api_score" not in PreAPIQualificationGate.NON_API_DIMENSIONS
    assert len(PreAPIQualificationGate.NON_API_DIMENSIONS) == 10


def test_dimension_to_dict_has_all_keys():
    """PreAPIQualificationDimension.to_dict() must include all required keys."""
    dim = PreAPIQualificationDimension(
        name="test",
        score=4.5,
        passed=True,
        evidence=["ev1"],
        blockers=[],
        next_actions=["act1"],
    )
    d = dim.to_dict()
    for key in ("name", "score", "threshold", "passed", "evidence", "blockers", "next_actions"):
        assert key in d


def test_markdown_sections_present():
    """All 10 required markdown sections must appear in output."""
    gate = PreAPIQualificationGate()
    report = gate.evaluate(tests_pass=True)
    md = render_markdown(report)

    required_sections = [
        "## 1. Executive Summary",
        "## 2. Final Decision",
        "## 3. Dimension Scores",
        "## 4. Non-API Gates",
        "## 5. API Exception",
        "## 6. Blockers Before API",
        "## 7. Required Fixes",
        "## 8. Evidence Commands",
        "## 9. Go / No-Go",
        "## 10. Next Phase Recommendation",
    ]
    for section in required_sections:
        assert section in md, f"Missing section: {section}"
