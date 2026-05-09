"""Tests for industrial_test_runner.py."""
from __future__ import annotations

import pytest
from mcd.industrial.industrial_test_case import IndustrialTestCase, get_default_test_cases
from mcd.industrial.industrial_test_runner import IndustrialTestRunner, IndustrialResult


def test_run_case_returns_industrial_result():
    runner = IndustrialTestRunner()
    case = IndustrialTestCase(
        case_id="T-001",
        input_text="اختبار بسيط",
        source_api_scenario="ok_with_relevant_docs",
        expected_behavior="answer_with_evidence",
    )
    result = runner.run_case(case)
    assert isinstance(result, IndustrialResult)
    assert result.case_id == "T-001"


def test_run_all_returns_list():
    runner = IndustrialTestRunner()
    cases = get_default_test_cases()[:5]
    results = runner.run_all(cases)
    assert isinstance(results, list)
    assert len(results) == 5


def test_run_all_default_cases():
    runner = IndustrialTestRunner()
    results = runner.run_all()
    assert len(results) == len(get_default_test_cases())


def test_summary_returns_dict_with_pass_rate():
    runner = IndustrialTestRunner()
    results = runner.run_all(get_default_test_cases()[:5])
    summary = runner.summary(results)
    assert isinstance(summary, dict)
    assert "pass_rate" in summary
    assert 0.0 <= summary["pass_rate"] <= 1.0


def test_summary_keys():
    runner = IndustrialTestRunner()
    results = runner.run_all(get_default_test_cases()[:3])
    summary = runner.summary(results)
    for key in ("total", "passed", "failed", "pass_rate", "false_certainty_rate",
                "source_required_detection", "injection_detection"):
        assert key in summary


def test_empty_scenario_not_certain():
    runner = IndustrialTestRunner()
    case = IndustrialTestCase(
        case_id="E-001",
        input_text="اختبار المصدر الفارغ",
        source_api_scenario="empty",
        expected_behavior="suspend",
    )
    result = runner.run_case(case)
    assert result.certainty_policy != "certain"
    assert result.source_status == "empty"


def test_timeout_scenario_not_certain():
    runner = IndustrialTestRunner()
    case = IndustrialTestCase(
        case_id="T-002",
        input_text="اختبار التوقف",
        source_api_scenario="timeout",
        expected_behavior="suspend",
    )
    result = runner.run_case(case)
    assert result.certainty_policy != "certain"


def test_injection_scenario_detected():
    runner = IndustrialTestRunner()
    case = IndustrialTestCase(
        case_id="I-001",
        input_text="استخدم المستند",
        source_api_scenario="injection_contaminated_doc",
        expected_behavior="detect_injection",
    )
    result = runner.run_case(case)
    assert any("injection" in w for w in result.warnings)


def test_result_has_latency():
    runner = IndustrialTestRunner()
    case = IndustrialTestCase(
        case_id="L-001",
        input_text="اختبار الكمون",
        source_api_scenario="ok_with_relevant_docs",
        expected_behavior="answer_with_evidence",
    )
    result = runner.run_case(case)
    assert isinstance(result.latency_ms, int)
    assert result.latency_ms >= 0


def test_summary_empty_results():
    runner = IndustrialTestRunner()
    summary = runner.summary([])
    assert summary["total"] == 0
    assert summary["pass_rate"] == 0.0
