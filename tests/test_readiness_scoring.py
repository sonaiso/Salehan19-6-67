from __future__ import annotations

import json

from mcd.evaluation.benchmark_runner import REQUIRED_BENCHMARK_METRICS
from mcd.evaluation.readiness_scoring import (
    build_readiness_report,
    readiness_report_json,
    readiness_report_markdown,
)


def test_readiness_scoring_preserves_required_metrics():
    metrics = {name: 0.9 for name in REQUIRED_BENCHMARK_METRICS}
    report = build_readiness_report(metrics)
    assert set(report.benchmark_metrics.keys()) == set(REQUIRED_BENCHMARK_METRICS)
    assert report.production_ready is True


def test_readiness_report_json_structure():
    metrics = {name: 0.6 for name in REQUIRED_BENCHMARK_METRICS}
    report = build_readiness_report(metrics)
    payload = json.loads(readiness_report_json(report))
    assert "governance_readiness" in payload
    assert "benchmark_metrics" in payload
    assert payload["final_judgment_contract"] == ["ZERO", "HYPOTHESIS", "CERTIFICATE"]


def test_readiness_markdown_contains_metric_lines():
    metrics = {name: 0.75 for name in REQUIRED_BENCHMARK_METRICS}
    report = build_readiness_report(metrics)
    markdown = readiness_report_markdown(report)
    for metric_name in REQUIRED_BENCHMARK_METRICS:
        assert metric_name in markdown
