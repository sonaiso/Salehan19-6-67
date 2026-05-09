"""Tests for CLI readiness-score command."""
import subprocess
import sys
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = str(REPO_ROOT / "src")


def _run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
        timeout=60,
    )
    return result


def test_readiness_score_json():
    result = _run_cli("readiness-score", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "dimensions" in data
    assert "average_score" in data
    assert "maturity_level" in data


def test_readiness_score_has_10_dimensions():
    result = _run_cli("readiness-score", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["dimensions"]) == 10


def test_readiness_score_maturity_valid():
    result = _run_cli("readiness-score", "--output", "json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    valid = {"concept", "research_prototype", "working_prototype", "pilot_ready", "production_ready"}
    assert data["maturity_level"] in valid
