"""Tests for failure_injection.py."""
from __future__ import annotations

import pytest
from mcd.industrial.failure_injection import FailureInjector, FailureInjectionResult, SCENARIO_TO_MOCK


def test_run_all_returns_list():
    injector = FailureInjector()
    results = injector.run_all()
    assert isinstance(results, list)
    assert len(results) == len(SCENARIO_TO_MOCK)


def test_each_result_has_passed_attribute():
    injector = FailureInjector()
    results = injector.run_all()
    for r in results:
        assert isinstance(r, FailureInjectionResult)
        assert hasattr(r, "passed")
        assert isinstance(r.passed, bool)


def test_source_timeout_scenario():
    injector = FailureInjector()
    result = injector.run_scenario("source_timeout")
    assert result.scenario == "source_timeout"
    assert result.certainty_lowered is True
    assert result.suspended is True


def test_source_empty_scenario():
    injector = FailureInjector()
    result = injector.run_scenario("source_empty")
    assert result.certainty_lowered is True
    assert result.has_warnings is True


def test_prompt_injection_in_source_scenario():
    injector = FailureInjector()
    result = injector.run_scenario("prompt_injection_in_source")
    assert result.certainty_lowered is True
    assert result.has_warnings is True


def test_source_conflict_scenario():
    injector = FailureInjector()
    result = injector.run_scenario("source_conflict")
    assert result.has_warnings is True


def test_all_results_have_details():
    injector = FailureInjector()
    results = injector.run_all()
    for r in results:
        assert isinstance(r.details, str)
        assert len(r.details) > 0


def test_no_fabricated_answer_when_no_source():
    injector = FailureInjector()
    result = injector.run_scenario("missing_evidence")
    assert result.no_fabricated_answer is True
