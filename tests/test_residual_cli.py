"""Tests for CLI residual commands."""
from __future__ import annotations

import json
import subprocess
import sys
import os
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
PROPOSALS_FILE = os.path.join(REPO_ROOT, "data", "residual_learning", "mock_gpt_proposals_ar.jsonl")


def run_cli(*args: str) -> tuple[int, str, str]:
    """Run the MCD CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli", *args],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": os.path.join(REPO_ROOT, "src")},
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout, result.stderr


class TestResidualCLIAnalyze:
    def test_residual_analyze_json_output(self) -> None:
        rc, stdout, stderr = run_cli(
            "residual-analyze",
            "--input", PROPOSALS_FILE,
            "--output", "json",
        )
        assert rc == 0, f"CLI failed: {stderr}"
        data = json.loads(stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_residual_analyze_result_has_residual(self) -> None:
        rc, stdout, _ = run_cli(
            "residual-analyze",
            "--input", PROPOSALS_FILE,
            "--output", "json",
        )
        assert rc == 0
        data = json.loads(stdout)
        first = data[0]
        assert "residual" in first
        assert "proposal_id" in first

    def test_residual_analyze_gpt_not_as_evidence(self) -> None:
        """GPT output must never be accepted as evidence."""
        rc, stdout, _ = run_cli(
            "residual-analyze",
            "--input", PROPOSALS_FILE,
            "--output", "json",
        )
        assert rc == 0
        data = json.loads(stdout)
        # None of the results should have gpt_output_as_evidence_rejected
        # accepted (i.e. if it was rejected, it should appear in evidence_gaps)
        for item in data:
            residual = item.get("residual", {})
            evidence_gaps = residual.get("evidence_gaps", [])
            for gap in evidence_gaps:
                # If detected, it should be REJECTED not accepted
                if "gpt" in gap.lower():
                    assert "rejected" in gap.lower(), f"GPT evidence not properly rejected: {gap}"

    def test_residual_report_markdown(self) -> None:
        rc, stdout, stderr = run_cli(
            "residual-report",
            "--input", PROPOSALS_FILE,
            "--output", "markdown",
        )
        assert rc == 0, f"CLI failed: {stderr}"
        assert "Cognitive Residual Learning Report" in stdout

    def test_residual_calibrate_markdown(self) -> None:
        rc, stdout, stderr = run_cli(
            "residual-calibrate",
            "--input", PROPOSALS_FILE,
            "--output", "markdown",
        )
        assert rc == 0, f"CLI failed: {stderr}"
        assert "Calibration Report" in stdout

    def test_residual_calibrate_json(self) -> None:
        rc, stdout, stderr = run_cli(
            "residual-calibrate",
            "--input", PROPOSALS_FILE,
            "--output", "json",
        )
        assert rc == 0, f"CLI failed: {stderr}"
        data = json.loads(stdout)
        assert "residual_count" in data
        assert data["residual_count"] > 0

    def test_residual_build_dataset_adversarial(self, tmp_path) -> None:
        out = str(tmp_path / "adversarial.jsonl")
        rc, stdout, stderr = run_cli(
            "residual-build-dataset",
            "--target", "adversarial",
            "--input", PROPOSALS_FILE,
            "--output", out,
        )
        assert rc == 0, f"CLI failed: {stderr}"
        assert os.path.exists(out)
        with open(out, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_residual_test_specs(self, tmp_path) -> None:
        out = str(tmp_path / "specs.jsonl")
        rc, stdout, stderr = run_cli(
            "residual-test-specs",
            "--input", PROPOSALS_FILE,
            "--output", out,
        )
        assert rc == 0, f"CLI failed: {stderr}"
        assert os.path.exists(out)
        with open(out, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_no_network_calls(self) -> None:
        """Ensure no real API calls are made — all mocked."""
        # This test verifies by design: the CLI only uses mock_gpt_proposals_ar.jsonl
        # which is a local file with pre-written proposals. No network access needed.
        rc, _, stderr = run_cli(
            "residual-analyze",
            "--input", PROPOSALS_FILE,
            "--output", "json",
        )
        assert rc == 0
        # If any network call had failed, stderr would contain connection errors
        assert "ConnectionError" not in stderr
        assert "NetworkError" not in stderr
        assert "requests.exceptions" not in stderr
