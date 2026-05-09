"""Tests for CLI ground command."""
import json
import subprocess
import sys
import pytest


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd="/home/runner/work/Salehan19-6-67/Salehan19-6-67",
        env={"PYTHONPATH": "src", "PATH": __import__("os").environ.get("PATH", "")},
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
