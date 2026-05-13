import json
import os
import subprocess
import sys


def _run(*args):
    env = {"PYTHONPATH": "src", **os.environ}
    result = subprocess.run([sys.executable, "-m", "mcd.cli", *args], capture_output=True, text=True, env=env)
    return result


def test_math_governance_json():
    r = _run("math-governance", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "governance_score" in data


def test_math_chain_markdown():
    r = _run("math-chain", "--text", "زيد كاتب", "--output", "markdown")
    assert r.returncode == 0
    assert "Mathematical Chain" in r.stdout


def test_math_morphisms_markdown():
    r = _run("math-morphisms", "--output", "markdown")
    assert r.returncode == 0
    assert "Registered Morphisms" in r.stdout


def test_math_operators_json():
    r = _run("math-operators", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert isinstance(data, list)


def test_math_jami_mani_json():
    r = _run("math-jami-mani", "--concept", "evidence", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["concept_id"] == "evidence"


def test_math_annotate_dataset_json():
    r = _run(
        "math-annotate-dataset",
        "--path",
        "data/evaluation/ambiguity_ar.jsonl",
        "--output",
        "json",
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "dataset_annotation_score" in data


def test_math_judgment_vector_json():
    r = _run("math-judgment-vector", "--text", "زيد كاتب", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "layer_judgments" in data
    assert "global_judgment" in data


def test_math_bridge_report_json():
    r = _run("math-bridge-report", "--text", "زيد كاتب", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "bridges" in data
    assert isinstance(data["bridges"], list)


def test_math_global_certificate_json():
    r = _run("math-global-certificate", "--text", "زيد كاتب", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "judgment" in data
    assert data["judgment"] in {"zero", "hypothesis", "certificate"}
