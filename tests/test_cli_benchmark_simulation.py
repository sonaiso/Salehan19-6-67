"""Tests for CLI benchmark-simulation command."""
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


def test_benchmark_simulation_json():
    result = _run_cli("benchmark-simulation", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert "total_examples" in data


def test_benchmark_simulation_markdown():
    result = _run_cli("benchmark-simulation", "--output", "markdown")
    assert result.returncode == 0, result.stderr
