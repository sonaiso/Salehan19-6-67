"""Tests for CLI ground command."""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

# Determine repo root dynamically
_REPO_ROOT = str(Path(__file__).parent.parent)


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(Path(_REPO_ROOT) / "src")}
    return subprocess.run(
        [sys.executable, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=_REPO_ROOT,
        env=env,
    )


def test_ground_json_output():
    result = _run_cli("ground", "كتب زيد الدرس بالقلم في المدرسة أمس", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_ground_json_has_grounded_lexemes():
    result = _run_cli("ground", "كتب زيد الدرس بالقلم في المدرسة أمس", "--output", "json")
    data = json.loads(result.stdout)
    assert "grounded_lexemes" in data


def test_ground_json_has_role_frames():
    result = _run_cli("ground", "كتب زيد الدرس بالقلم في المدرسة أمس", "--output", "json")
    data = json.loads(result.stdout)
    assert "role_frames" in data


def test_ground_json_has_nisbah_frames():
    result = _run_cli("ground", "كتب زيد الدرس بالقلم في المدرسة أمس", "--output", "json")
    data = json.loads(result.stdout)
    assert "nisbah_frames" in data


def test_ground_json_has_final_status():
    result = _run_cli("ground", "كتب زيد الدرس بالقلم في المدرسة أمس", "--output", "json")
    data = json.loads(result.stdout)
    assert "final_status" in data
    assert data["final_status"] in ("grounded", "partially_grounded", "ungrounded", "pending")


def test_ground_value_sentence():
    result = _run_cli("ground", "الكذب ضار أم حرام؟", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_ground_civilization_sentence():
    result = _run_cli("ground", "الذكاء الاصطناعي أداة مدنية أم مفهوم حضاري؟", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_ground_society_sentence():
    result = _run_cli("ground", "المجتمع يرفض الفساد", "--output", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_ground_text_output():
    result = _run_cli("ground", "كتب زيد الدرس", "--output", "text")
    assert result.returncode == 0, result.stderr
    assert "GLCFL" in result.stdout or "المعرفي" in result.stdout
