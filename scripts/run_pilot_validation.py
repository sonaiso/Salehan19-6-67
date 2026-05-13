"""Generate reproducible pilot validation report artifacts."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from mcd.audit.backend import PersistentAuditBackend
from mcd.events import ImmutableGovernanceEventLog
from mcd.observability import GovernanceTraceEvent, PersistentTraceStore
from mcd.qualification import LayerSovereigntyRegistry, runtime_formal_truth_table

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_EQUIVALENCE_ARTIFACT = REPO_ROOT / "research/formal/runtime_formal_equivalence_truth_table.json"


def _runtime_formal_summary() -> dict[str, Any]:
    runtime_rows = runtime_formal_truth_table()
    committed_payload = json.loads(COMMITTED_EQUIVALENCE_ARTIFACT.read_text(encoding="utf-8"))
    committed_rows = committed_payload.get("truth_table", [])

    runtime_by_case = {row["case_id"]: row for row in runtime_rows}
    committed_by_case = {row["case_id"]: row for row in committed_rows}

    case_ids_match = set(runtime_by_case) == set(committed_by_case)
    values_match = True
    if case_ids_match:
        for case_id, runtime_row in runtime_by_case.items():
            committed_row = committed_by_case[case_id]
            if (
                runtime_row["python_public_judgment"] != committed_row["python_public_judgment"]
                or runtime_row["lean_public_judgment"] != committed_row["lean_public_judgment"]
            ):
                values_match = False
                break
    else:
        values_match = False

    equivalent = all(row.get("equivalent") == "true" for row in runtime_rows)
    return {
        "artifact_path": str(COMMITTED_EQUIVALENCE_ARTIFACT.relative_to(REPO_ROOT)),
        "total_cases": len(runtime_rows),
        "all_runtime_formal_equivalent": equivalent,
        "matches_committed_truth_table": case_ids_match and values_match,
    }


def _replay_integrity_summary() -> dict[str, Any]:
    with TemporaryDirectory(prefix="mcd-pilot-validation-") as temp_dir:
        temp_path = Path(temp_dir)
        trace_store = PersistentTraceStore(trace_file=str(temp_path / "api_traces.jsonl"))
        event_log = ImmutableGovernanceEventLog(log_file=str(temp_path / "governance_events.jsonl"))
        backend = PersistentAuditBackend(trace_store=trace_store, event_log=event_log)
        backend.clear()
        backend.append_trace(
            GovernanceTraceEvent(
                request_id="pilot-rq-1",
                replay_id="pilot-replay-1",
                path="/v1/classify",
                method="POST",
                status_code=200,
                execution_time_ms=1.0,
                residual_preserved=True,
                public_judgment="hypothesis",
            ),
        )
        backend.append_trace(
            GovernanceTraceEvent(
                request_id="pilot-rq-2",
                replay_id="pilot-replay-1",
                path="/v1/classify",
                method="POST",
                status_code=200,
                execution_time_ms=1.1,
                residual_preserved=True,
                public_judgment="zero",
            ),
        )

        snapshot = backend.replay_from_events().to_dict()
        contract = dict(snapshot["replay_integrity_contract"])
        return {
            "statement": contract["statement"],
            "valid_event_log": contract["valid_event_log"],
            "original_judgment_sequence": contract["original_judgment_sequence"],
            "replayed_judgment_sequence": contract["replayed_judgment_sequence"],
            "judgment_consistent": contract["judgment_consistent"],
            "contract_holds": contract["contract_holds"],
        }


def _layer_sovereignty_summary() -> dict[str, Any]:
    registry = LayerSovereigntyRegistry()
    entries = registry.as_dict()

    silent_skip_blocked = True
    for idx, entry in enumerate(entries):
        allowed_ascent = list(entry["allowed_ascent"])
        layer_name = str(entry["layer"])
        if idx < len(entries) - 1:
            expected = [entries[idx + 1]["layer"]]
            if allowed_ascent != expected:
                silent_skip_blocked = False
                break
        elif allowed_ascent:
            silent_skip_blocked = False
            break
        if layer_name not in entry["forbidden_ascent"]:
            silent_skip_blocked = False
            break

    return {
        "layers_registered": len(entries),
        "silent_level_skip_blocked": silent_skip_blocked,
        "registry_path": "src/mcd/qualification/layer_sovereignty_registry.py",
    }


def build_report() -> dict[str, Any]:
    runtime_equivalence = _runtime_formal_summary()
    replay_integrity = _replay_integrity_summary()
    layer_sovereignty = _layer_sovereignty_summary()

    report_holds = (
        runtime_equivalence["all_runtime_formal_equivalent"]
        and runtime_equivalence["matches_committed_truth_table"]
        and replay_integrity["contract_holds"]
        and layer_sovereignty["silent_level_skip_blocked"]
    )

    return {
        "version": "v0.1.0-pilot",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage": "pilot-qualified",
        "final_epistemic_status": "HYPOTHESIS",
        "report_holds": report_holds,
        "runtime_formal_equivalence": runtime_equivalence,
        "replay_integrity_contract": replay_integrity,
        "layer_sovereignty_registry": layer_sovereignty,
        "proves": [
            "bounded_runtime_formal_equivalence_baseline",
            "replay_judgment_sequence_integrity_contract",
            "layer_sovereignty_registry_enforced_for_ordered_ascent",
        ],
        "does_not_prove": [
            "full_runtime_refinement_proof",
            "full_replay_lean_formalization",
            "meaning_ascent_algebra_complete_formalization",
            "production_certification",
        ],
        "certificate_semantics": {
            "local_certificate": "Scoped local certificate decision under local evidence and gate conditions.",
            "global_certificate": "Cross-layer governed certificate requires complete chain closure and no blocking residuals.",
        },
        "certificate_failure_conditions": [
            "missing_proof_object",
            "governance_gate_failed",
            "reverse_trace_incomplete",
            "forbidden_transition_detected",
            "residual_erasure_detected",
            "insufficient_evidence_rank",
            "rank_gap_or_missing_evidence_or_unresolved_conflict",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate pilot validation report for external audit package.")
    parser.add_argument("--output", default=None, help="Optional path to write JSON report.")
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
