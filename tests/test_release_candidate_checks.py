from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_release_candidate_checks.py"


REQUIRED_FIELDS = {
    "pilot_validation_available",
    "runtime_formal_equivalence_checked",
    "replay_integrity_contract_checked",
    "layer_sovereignty_registry_checked",
    "formal_theorem_track_checked",
    "public_judgment_triad_preserved",
    "no_certificate_bypass_claimed",
    "no_consciousness_claim",
    "production_certified",
    "pilot_status",
    "remaining_production_gaps",
}


REQUIRED_ARTIFACT_KEYS = {
    "pilot_validation_report",
    "runtime_formal_equivalence_artifact",
    "replay_integrity_test",
    "layer_sovereignty_test",
    "formal_theorem_contract",
    "repository_integrity_test",
    "cli_dispatch_integrity_test",
}


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src:."},
    )


def test_release_candidate_report_shape_and_required_fields(tmp_path: Path) -> None:
    output_path = tmp_path / "release_candidate_report.json"
    result = _run_script("--output", str(output_path))
    assert result.returncode == 0

    from_stdout = json.loads(result.stdout)
    from_file = json.loads(output_path.read_text(encoding="utf-8"))
    assert from_stdout == from_file

    missing = REQUIRED_FIELDS - set(from_file)
    assert not missing, f"missing required report fields: {sorted(missing)}"


def test_release_candidate_claim_boundaries_and_artifact_references(tmp_path: Path) -> None:
    output_path = tmp_path / "release_candidate_report.json"
    payload = json.loads(_run_script("--output", str(output_path)).stdout)

    assert payload["pilot_status"] == "HYPOTHESIS"
    assert payload["production_certified"] is False
    assert payload["no_consciousness_claim"] is True
    assert payload["public_judgment_triad_preserved"] is True
    assert payload["no_certificate_bypass_claimed"] is True

    artifacts = payload["artifacts_referenced"]
    assert REQUIRED_ARTIFACT_KEYS.issubset(artifacts)
    assert all(isinstance(value, str) and value for value in artifacts.values())

    for path in artifacts.values():
        assert (REPO_ROOT / path).exists(), f"missing referenced artifact/test path: {path}"

    assert payload["remaining_production_gaps"]
