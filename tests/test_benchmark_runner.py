from __future__ import annotations

from mcd.evaluation.benchmark_runner import (
    REQUIRED_BENCHMARK_METRICS,
    run_empirical_benchmarks,
)


def test_benchmark_runner_emits_required_metrics():
    report = run_empirical_benchmarks()
    assert report.total_cases > 0
    assert set(REQUIRED_BENCHMARK_METRICS).issubset(report.metrics.keys())


def test_benchmark_runner_metric_ranges():
    report = run_empirical_benchmarks()
    for metric_name in REQUIRED_BENCHMARK_METRICS:
        value = report.metrics[metric_name]
        assert 0.0 <= value <= 1.0, metric_name


def test_benchmark_runner_includes_case_rows():
    report = run_empirical_benchmarks()
    assert len(report.cases) == report.total_cases
    first = report.cases[0]
    assert "case_id" in first
    assert "public_judgment" in first
