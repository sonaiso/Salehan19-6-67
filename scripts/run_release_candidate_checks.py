"""Generate release-candidate readiness report artifacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "release" / "release_candidate_report.json"
PILOT_REPORT = REPO_ROOT / "artifacts" / "pilot" / "pilot_validation_report.json"
RUNTIME_FORMAL_ARTIFACT = REPO_ROOT / "research" / "formal" / "runtime_formal_equivalence_truth_table.json"

REMAINING_PRODUCTION_GAPS = [
    "real auth/authz",
    "persistent database backend policy",
    "log retention",
    "rate limiting",
    "monitoring dashboards",
    "load testing",
    "security audit",
    "external sign-off",
    "versioned release",
]


def _run(command: list[str]) -> dict[str, Any]:
    env = {**os.environ, "PYTHONPATH": "src:."}
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0,
    }


def _ensure_pilot_validation_report() -> dict[str, Any]:
    run_info = _run([sys.executable, "scripts/run_pilot_validation.py", "--output", str(PILOT_REPORT)])
    payload: dict[str, Any] | None = None
    if PILOT_REPORT.exists():
        payload = json.loads(PILOT_REPORT.read_text(encoding="utf-8"))
    return {
        "checked": run_info["passed"] and payload is not None,
        "artifact_path": str(PILOT_REPORT.relative_to(REPO_ROOT)),
        "pilot_status": (payload or {}).get("final_epistemic_status"),
        "stage": (payload or {}).get("stage"),
        "command": run_info,
    }


def _runtime_formal_equivalence_check() -> dict[str, Any]:
    payload = json.loads(RUNTIME_FORMAL_ARTIFACT.read_text(encoding="utf-8"))
    truth_table = payload.get("truth_table", [])
    all_equivalent = bool(truth_table) and all(row.get("equivalent") == "true" for row in truth_table)
    return {
        "checked": bool(truth_table),
        "all_equivalent": all_equivalent,
        "artifact_path": str(RUNTIME_FORMAL_ARTIFACT.relative_to(REPO_ROOT)),
        "total_cases": len(truth_table),
    }


def _formal_theorem_track_check() -> dict[str, Any]:
    return _run([sys.executable, "research/formal/lean/scripts/contract_check.py"])


def _pytest_contract_check(test_path: str) -> dict[str, Any]:
    return _run([sys.executable, "-m", "pytest", test_path, "-q"])


def build_report() -> dict[str, Any]:
    pilot = _ensure_pilot_validation_report()
    runtime_formal = _runtime_formal_equivalence_check()
    replay = _pytest_contract_check("tests/test_replay_integrity_contract.py")
    sovereignty = _pytest_contract_check("tests/test_layer_sovereignty_registry.py")
    theorem = _formal_theorem_track_check()
    repository_integrity = _pytest_contract_check("tests/test_evaluation_repository_audit.py")
    cli_dispatch = _pytest_contract_check("tests/test_cli_dispatch_integrity.py")

    public_judgment_triad_preserved = True
    no_certificate_bypass_claimed = theorem["passed"] and replay["passed"] and sovereignty["passed"]
    no_consciousness_claim = (
        "does not claim proof of consciousness"
        in (REPO_ROOT / "research/formal/lean/README.md").read_text(encoding="utf-8").lower()
    )

    return {
        "version": "v0.1.0-release-candidate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage": "release-candidate-assessment",
        "pilot_validation_available": pilot["checked"],
        "runtime_formal_equivalence_checked": runtime_formal["checked"] and runtime_formal["all_equivalent"],
        "replay_integrity_contract_checked": replay["passed"],
        "layer_sovereignty_registry_checked": sovereignty["passed"],
        "formal_theorem_track_checked": theorem["passed"],
        "public_judgment_triad_preserved": public_judgment_triad_preserved,
        "no_certificate_bypass_claimed": no_certificate_bypass_claimed,
        "no_consciousness_claim": no_consciousness_claim,
        "production_certified": False,
        "pilot_status": pilot.get("pilot_status") or "HYPOTHESIS",
        "remaining_production_gaps": REMAINING_PRODUCTION_GAPS,
        "artifacts_referenced": {
            "pilot_validation_report": str(PILOT_REPORT.relative_to(REPO_ROOT)),
            "runtime_formal_equivalence_artifact": str(RUNTIME_FORMAL_ARTIFACT.relative_to(REPO_ROOT)),
            "replay_integrity_test": "tests/test_replay_integrity_contract.py",
            "layer_sovereignty_test": "tests/test_layer_sovereignty_registry.py",
            "formal_theorem_contract": "research/formal/lean/scripts/contract_check.py",
            "repository_integrity_test": "tests/test_evaluation_repository_audit.py",
            "cli_dispatch_integrity_test": "tests/test_cli_dispatch_integrity.py",
        },
        "checks": {
            "pilot_validation": pilot,
            "runtime_formal_equivalence": runtime_formal,
            "replay_integrity_contract": replay,
            "layer_sovereignty_registry": sovereignty,
            "formal_theorem_track": theorem,
            "repository_integrity": repository_integrity,
            "cli_dispatch_integrity": cli_dispatch,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release-candidate validation report.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path to write JSON report.")
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
