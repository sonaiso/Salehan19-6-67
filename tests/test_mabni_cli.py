"""Tests for mabni CLI commands."""
from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", **__import__("os").environ},
    )
    return result


def test_mabni_analyze_json():
    result = _run_cli("mabni-analyze", "--text", "ما جاء زيد", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "text" in data
    assert data["text"] == "ما جاء زيد"


def test_mabni_analyze_summary():
    result = _run_cli("mabni-analyze", "--text", "إن جاء زيد فأكرمه", "--output", "summary")
    assert result.returncode == 0
    assert "زيد" in result.stdout or "إن" in result.stdout or "شرط" in result.stdout


def test_mabni_registry_table():
    result = _run_cli("mabni-registry", "--output", "table")
    assert result.returncode == 0
    assert "Total" in result.stdout


def test_mabni_registry_json():
    result = _run_cli("mabni-registry", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0


def test_mabni_certainty_summary():
    result = _run_cli("mabni-certainty", "--text", "ما جاء زيد", "--output", "summary")
    assert result.returncode == 0


def test_mabni_graph_json():
    result = _run_cli("mabni-graph", "--text", "ما جاء زيد", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "nodes" in data
    assert "edges" in data


def test_mabni_trace_summary():
    result = _run_cli("mabni-trace", "--text", "ما جاء", "--output", "summary")
    assert result.returncode == 0
