"""Tests for staging_simulator.py."""
from __future__ import annotations

import pytest
from mcd.industrial.staging_simulator import StagingSimulator, StagingSimulationReport
from mcd.industrial.industrial_test_case import get_default_test_cases


def test_staging_simulator_returns_report():
    sim = StagingSimulator()
    report = sim.run(get_default_test_cases()[:5])
    assert isinstance(report, StagingSimulationReport)


def test_pass_rate_is_float_between_0_and_1():
    sim = StagingSimulator()
    report = sim.run(get_default_test_cases()[:5])
    assert isinstance(report.pass_rate, float)
    assert 0.0 <= report.pass_rate <= 1.0


def test_total_cases_equals_passed_plus_failed():
    sim = StagingSimulator()
    report = sim.run(get_default_test_cases()[:10])
    assert report.total_cases == report.passed + report.failed


def test_results_list_length_matches_total():
    sim = StagingSimulator()
    cases = get_default_test_cases()[:7]
    report = sim.run(cases)
    assert len(report.results) == report.total_cases


def test_warnings_is_list():
    sim = StagingSimulator()
    report = sim.run(get_default_test_cases()[:3])
    assert isinstance(report.warnings, list)


def test_staging_simulator_with_default_cases():
    sim = StagingSimulator()
    report = sim.run()
    assert report.total_cases == len(get_default_test_cases())
