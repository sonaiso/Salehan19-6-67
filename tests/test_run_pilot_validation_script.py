from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_pilot_validation.py"


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": "src:."},
    )


def test_run_pilot_validation_outputs_json_to_stdout() -> None:
    result = _run_script()
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["stage"] == "pilot-qualified"
    assert payload["final_epistemic_status"] == "HYPOTHESIS"
    assert payload["runtime_formal_equivalence"]["all_runtime_formal_equivalent"] is True
    assert payload["runtime_formal_equivalence"]["matches_committed_truth_table"] is True
    assert payload["replay_integrity_contract"]["contract_holds"] is True
    assert payload["layer_sovereignty_registry"]["silent_level_skip_blocked"] is True


def test_run_pilot_validation_writes_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "pilot_validation_report.json"
    result = _run_script("--output", str(output_path))
    assert result.returncode == 0
    assert output_path.exists()

    from_stdout = json.loads(result.stdout)
    from_file = json.loads(output_path.read_text(encoding="utf-8"))
    assert from_stdout == from_file

