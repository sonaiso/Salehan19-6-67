"""Tests for latency_benchmark.py."""
from __future__ import annotations

import pytest
from mcd.industrial.latency_benchmark import LatencyBenchmark, LatencyBenchmarkResult
from mcd.industrial.industrial_test_case import get_default_test_cases


def test_latency_benchmark_returns_result():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:3])
    assert isinstance(result, LatencyBenchmarkResult)


def test_total_cases_positive():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:3])
    assert result.total_cases > 0


def test_avg_latency_non_negative():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:3])
    assert result.avg_latency_ms >= 0.0


def test_p95_gte_p50():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:5])
    assert result.p95_latency_ms >= result.p50_latency_ms


def test_max_gte_avg():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:5])
    assert result.max_latency_ms >= result.avg_latency_ms


def test_by_component_is_dict():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:3])
    assert isinstance(result.by_component, dict)
    assert "classification" in result.by_component


def test_warnings_is_list():
    bench = LatencyBenchmark()
    result = bench.run(get_default_test_cases()[:3])
    assert isinstance(result.warnings, list)
