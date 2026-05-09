"""Tests for CLI evaluate-project command."""
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


def test_evaluate_project_json():
    result = _run_cli("evaluate-project", "--output", "json")
    assert result.returncode == 0, result.stderr


def test_evaluate_project_markdown():
    result = _run_cli("evaluate-project", "--output", "markdown")
    assert result.returncode == 0, result.stderr
    assert "Repository Industrial Audit" in result.stdout or len(result.stdout) > 100
