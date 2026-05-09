"""Tests for CLI classify subcommand."""
import json
import subprocess
import sys

import pytest


def run_cli(args: list[str], *, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + args,
        capture_output=True,
        text=True,
        env=env,
        cwd="/home/runner/work/Salehan19-6-67/Salehan19-6-67",
    )


def test_classify_json_output():
    result = run_cli(["classify", "النار تحرق", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "raw_text" in data
    assert "certainty_policy" in data


def test_classify_haraam_shari_suspend():
    result = run_cli(["classify", "هل الكذب حرام؟", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    shari = data.get("judgment_types", {}).get("shari", 0.0)
    assert shari >= 0.80
    assert data["certainty_policy"] == "suspend"


def test_classify_daar_not_shari_primary():
    result = run_cli(["classify", "هل الكذب ضار؟", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    shari = data.get("judgment_types", {}).get("shari", 0.0)
    assert shari < 0.70


def test_classify_api_technical():
    result = run_cli(["classify", "كيف نبني API للديكودر؟", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    technical = data.get("judgment_types", {}).get("technical", 0.0)
    assert technical >= 0.50


def test_classify_ilm_suspend():
    result = run_cli(["classify", "ما معنى علم؟", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["certainty_policy"] == "suspend"


def test_classify_text_output():
    result = run_cli(["classify", "النار تحرق", "--output", "text"])
    assert result.returncode == 0
    assert "النار تحرق" in result.stdout


def test_classify_debug_flag():
    result = run_cli(["classify", "النار تحرق", "--output", "json", "--debug"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "debug" in data
    assert "concept_vectors" in data["debug"]


def test_classify_json_valid():
    result = run_cli(["classify", "ما معنى علم؟"])
    assert result.returncode == 0
    # Default output is json
    data = json.loads(result.stdout)
    assert isinstance(data, dict)
