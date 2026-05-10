"""Tests for murab CLI commands."""
import subprocess
import json
import sys
import os

PYTHON = sys.executable
ENV = {**os.environ, "PYTHONPATH": "src"}


def run_cli(*args):
    result = subprocess.run(
        [PYTHON, "-m", "mcd.cli"] + list(args),
        capture_output=True, text=True, encoding="utf-8", env=ENV,
    )
    return result


def test_murab_analyze_json():
    result = run_cli("murab-analyze", "--text", "جاء المعلمُ", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) >= 1


def test_murab_analyze_text():
    result = run_cli("murab-analyze", "--text", "كتبَ الطالبُ", "--output", "text")
    assert result.returncode == 0
    assert "Token" in result.stdout or "Case" in result.stdout


def test_irab_resolve_json():
    result = run_cli("irab-resolve", "--token", "الكتابُ", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "irab_case" in data


def test_irab_resolve_with_context():
    result = run_cli(
        "irab-resolve", "--token", "المدرسةِ",
        "--context", "ذهبتُ إلى المدرسةِ",
        "--output", "json"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "irab_case" in data


def test_murab_graph_json():
    result = run_cli("murab-graph", "--text", "جاء الطالبُ", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "nodes" in data
    assert "edges" in data


def test_irab_certainty_json():
    result = run_cli("irab-certainty", "--token", "الكتابُ", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "syntactic_certainty" in data
    assert data["evidence_effect"] == "syntactic_only"


def test_murab_trace_json():
    result = run_cli("murab-trace", "--token", "أب", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "unicode_trace" in data
    assert all(cp.startswith("U+") for cp in data["unicode_trace"])


def test_murab_analyze_markdown():
    result = run_cli("murab-analyze", "--text", "العلمُ نورٌ", "--output", "markdown")
    assert result.returncode == 0
    assert "#" in result.stdout or "|" in result.stdout
