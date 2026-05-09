"""Tests for curriculum CLI commands."""
from __future__ import annotations

import subprocess
import sys
import json
import pytest


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    env = {"PYTHONPATH": "src"}
    import os
    full_env = {**os.environ, **env}
    return subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + cmd,
        capture_output=True,
        text=True,
        env=full_env,
        cwd="/home/runner/work/Salehan19-6-67/Salehan19-6-67",
    )


def test_curriculum_validate_exits_0():
    result = _run(["curriculum-validate"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_validate_text_output():
    result = _run(["curriculum-validate", "--output", "text"])
    assert result.returncode == 0
    assert "Total" in result.stdout or "Curriculum" in result.stdout


def test_curriculum_validate_json_output():
    result = _run(["curriculum-validate", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "total_units" in data
    assert "status" in data


def test_curriculum_validate_single_file():
    result = _run(["curriculum-validate", "data/curriculum/level_01_things_ar.jsonl", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total_units"] == 50


def test_curriculum_generate_exits_0():
    result = _run(["curriculum-generate", "--level", "1", "--count", "5"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_generate_jsonl_output():
    result = _run(["curriculum-generate", "--level", "1", "--count", "5", "--output", "jsonl"])
    assert result.returncode == 0
    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    assert len(lines) == 5
    for line in lines:
        obj = json.loads(line)
        assert "unit_id" in obj


def test_curriculum_generate_json_output():
    result = _run(["curriculum-generate", "--level", "2", "--count", "3", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 3


def test_curriculum_generate_text_output():
    result = _run(["curriculum-generate", "--level", "1", "--count", "3", "--output", "text"])
    assert result.returncode == 0
    assert "Generated" in result.stdout


def test_curriculum_evaluate_exits_0():
    result = _run(["curriculum-evaluate", "--profile", "full_curriculum"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_evaluate_markdown_output():
    result = _run(["curriculum-evaluate", "--profile", "full_curriculum", "--output", "markdown"])
    assert result.returncode == 0
    assert "Curriculum" in result.stdout


def test_curriculum_evaluate_json_output():
    result = _run(["curriculum-evaluate", "--profile", "full_curriculum", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "total_units" in data


def test_curriculum_report_exits_0():
    result = _run(["curriculum-report"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_report_markdown_output():
    result = _run(["curriculum-report", "--output", "markdown"])
    assert result.returncode == 0
    assert "Curriculum" in result.stdout


def test_curriculum_report_json_output():
    result = _run(["curriculum-report", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "validation" in data
    assert "evaluation" in data


def test_curriculum_export_industrial_exits_0():
    result = _run(["curriculum-export-industrial", "--profile", "industrial_curriculum"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_export_industrial_produces_jsonl():
    result = _run(["curriculum-export-industrial", "--profile", "industrial_curriculum"])
    assert result.returncode == 0
    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    assert len(lines) > 0
    for line in lines:
        obj = json.loads(line)
        assert "case_id" in obj
        assert "expected_behavior" in obj
