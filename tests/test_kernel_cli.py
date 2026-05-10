import json
import subprocess
import sys


def run_cli(*args):
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + list(args),
        capture_output=True, text=True,
        env={"PYTHONPATH": "src", **__import__("os").environ},
    )
    return result


def test_kernel_validate_json():
    r = run_cli("kernel-validate", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "kernel_validation_score" in data


def test_kernel_report_markdown():
    r = run_cli("kernel-report", "--output", "markdown")
    assert r.returncode == 0
    assert "Fractal Geometry Kernel" in r.stdout


def test_kernel_demo_fold_json():
    r = run_cli("kernel-demo-fold", "--text", "النموذج قال إن كل الشركات تستخدم GraphRAG بلا مصدر", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "fold_operation" in data
    assert "law_checks" in data


def test_kernel_proof_demo_json():
    r = run_cli("kernel-proof-demo", "--text", "النار حارة", "--output", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "proof_object" in data
    assert data["proof_object"]["proof_status"] == "hypothesis"
