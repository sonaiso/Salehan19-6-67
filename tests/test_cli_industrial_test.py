"""CLI integration tests for industrial commands."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

PYTHON = sys.executable
PYTHONPATH = "src"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": PYTHONPATH},
    )


def test_industrial_test_quick_json():
    result = run_cli("industrial-test", "--profile", "quick", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "summary" in data
    assert "results" in data


def test_industrial_test_full_markdown():
    result = run_cli("industrial-test", "--profile", "full", "--output", "markdown")
    assert result.returncode == 0
    assert "Industrial Testing Report" in result.stdout


def test_source_api_smoke_ok_with_relevant_docs():
    result = run_cli("source-api-smoke", "--scenario", "ok_with_relevant_docs", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert len(data["documents"]) > 0


def test_source_api_smoke_timeout():
    result = run_cli("source-api-smoke", "--scenario", "timeout", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "timeout"


def test_source_api_smoke_injection():
    result = run_cli("source-api-smoke", "--scenario", "injection_contaminated_doc", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"


def test_pilot_readiness_json():
    result = run_cli("pilot-readiness", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "ready_for_pilot" in data
    assert "score" in data
    assert "blockers" in data


def test_latency_benchmark_json():
    result = run_cli("latency-benchmark", "--cases", "5", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "avg_latency_ms" in data
    assert data["total_cases"] > 0


def test_existing_command_classify_still_works():
    result = run_cli("classify", "ما هو الإسلام؟", "--output", "json")
    assert result.returncode == 0


def test_existing_command_nabhani_still_works():
    result = run_cli("nabhani", "ما حكم الصلاة؟", "--output", "json")
    assert result.returncode == 0
