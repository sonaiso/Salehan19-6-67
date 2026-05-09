"""Tests for pilot_readiness.py."""
from __future__ import annotations

import pytest
from mcd.industrial.pilot_readiness import (
    PilotReadinessGate,
    PilotReadinessCriteria,
    PilotReadinessResult,
)


def test_evaluate_from_runner_returns_result():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert isinstance(result, PilotReadinessResult)


def test_ready_for_pilot_is_bool():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert isinstance(result.ready_for_pilot, bool)


def test_score_is_float_between_0_and_1():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert isinstance(result.score, float)
    assert 0.0 <= result.score <= 1.0


def test_blockers_is_list():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert isinstance(result.blockers, list)


def test_rest_api_not_implemented_in_blockers():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=True,
        industrial_test_pass_rate=0.9,
        false_certainty_rate=0.0,
        source_required_detection=0.95,
        injection_detection=0.95,
        json_schema_stability=1.0,
        readiness_report_exists=True,
        api_contract_defined=True,
        rest_api_implemented=False,
    )
    result = gate.evaluate(criteria)
    assert any("REST API" in b for b in result.blockers)


def test_passed_and_failed_criteria_cover_all():
    gate = PilotReadinessGate()
    result = gate.evaluate_from_runner()
    assert len(result.passed_criteria) + len(result.failed_criteria) > 0


def test_evaluate_with_good_criteria():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=True,
        industrial_test_pass_rate=0.95,
        false_certainty_rate=0.01,
        source_required_detection=0.95,
        injection_detection=0.95,
        json_schema_stability=1.0,
        p95_latency_ms=200.0,
        readiness_report_exists=True,
        api_contract_defined=True,
        rest_api_implemented=True,
    )
    result = gate.evaluate(criteria)
    assert result.score > 0.5
    assert "tests_pass" in result.passed_criteria


def test_evaluate_with_failing_criteria():
    gate = PilotReadinessGate()
    criteria = PilotReadinessCriteria(
        tests_pass=False,
        industrial_test_pass_rate=0.2,
        false_certainty_rate=0.8,
        source_required_detection=0.1,
        injection_detection=0.1,
        json_schema_stability=0.0,
        rest_api_implemented=False,
    )
    result = gate.evaluate(criteria)
    assert result.ready_for_pilot is False
    assert len(result.blockers) > 0
