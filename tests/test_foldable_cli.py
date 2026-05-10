"""Tests for foldable CLI commands."""
import subprocess
import sys
import os
import json

PYTHONPATH = os.path.join(os.path.dirname(__file__), "..", "src")


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + list(args),
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PYTHONPATH},
    )
    return result


def test_fold_residuals_command():
    r = run_cli("fold-residuals", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "total_proposals" in data
    assert data["total_proposals"] == 100


def test_fold_memory_report_command():
    r = run_cli("fold-memory-report", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "fold_consistency_score" in data


def test_fold_consistency_command():
    r = run_cli("fold-consistency", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "fold_consistency_score" in data
    assert data["fold_consistency_score"] >= 0.95


def test_pattern_mine_command():
    r = run_cli("pattern-mine", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert isinstance(data, list)


def test_fold_recall_command():
    r = run_cli("fold-recall", "--text", "هذا دليل", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "explanation" in data
