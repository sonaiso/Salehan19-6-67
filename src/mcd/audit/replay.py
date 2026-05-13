"""Audit replay and forensic reconstruction tools."""
from __future__ import annotations

from dataclasses import dataclass

from mcd.metrics import compute_governance_metrics


@dataclass
class ReplayResult:
    total_events: int
    replay_success: bool
    metrics: dict
    failures: list[str]
    reconstruction: dict
    judgment_sequence: list[str]
    last_public_judgment: str

    def to_dict(self) -> dict:
        return {
            "total_events": self.total_events,
            "replay_success": self.replay_success,
            "metrics": self.metrics,
            "failures": self.failures,
            "reconstruction": self.reconstruction,
            "judgment_sequence": self.judgment_sequence,
            "last_public_judgment": self.last_public_judgment,
        }


def reconstruct_governance_events(events: list[dict]) -> dict:
    """Categorize replayable governance events by reconstruction path type."""
    def _filter(predicate) -> list[dict]:
        return [e for e in events if predicate(e)]

    return {
        "certificate": _filter(
            lambda e: (e.get("public_judgment", "").strip().lower() == "certificate")
            or e.get("event_type") == "certificate",
        ),
        "hypothesis_downgrade": _filter(
            lambda e: bool(e.get("hypothesis_downgrade", False))
            or e.get("event_type") == "hypothesis_downgrade",
        ),
        "forbidden_transition": _filter(
            lambda e: bool(e.get("forbidden_transition", False))
            or e.get("event_type") == "forbidden_transition",
        ),
        "residual_preservation": _filter(
            lambda e: bool(e.get("residual_preserved", False))
            or e.get("event_type") == "residual_preservation",
        ),
        "collapse_event": _filter(
            lambda e: bool(e.get("collapse_event", False))
            or e.get("event_type") == "collapse_event",
        ),
    }


def replay_trace_events(events: list[dict]) -> ReplayResult:
    failures: list[str] = []
    judgment_sequence = [
        str(e.get("public_judgment", "")).strip().lower()
        for e in events
        if str(e.get("public_judgment", "")).strip()
    ]
    for i, e in enumerate(events):
        if not e.get("request_id"):
            failures.append(f"event[{i}] missing request_id")
        if not e.get("replay_id"):
            failures.append(f"event[{i}] missing replay_id")
        if "residual_preserved" not in e:
            failures.append(f"event[{i}] missing residual_preserved")
        elif not e.get("residual_preserved"):
            failures.append(f"event[{i}] residual_preserved=false")
    reconstruction = reconstruct_governance_events(events)
    has_valid_residual_preservation = any(
        e.get("residual_preserved", False) for e in reconstruction["residual_preservation"]
    )
    if events and not has_valid_residual_preservation:
        failures.append("no residual_preservation events found")
    metrics = compute_governance_metrics(events).to_dict()
    return ReplayResult(
        total_events=len(events),
        replay_success=len(failures) == 0,
        metrics=metrics,
        failures=failures,
        reconstruction={k: len(v) for k, v in reconstruction.items()},
        judgment_sequence=judgment_sequence,
        last_public_judgment=judgment_sequence[-1] if judgment_sequence else "zero",
    )


def reconstruct_certificate_forensics(events: list[dict]) -> dict:
    reconstruction = reconstruct_governance_events(events)
    cert_events = reconstruction["certificate"]
    return {
        "events_considered": len(events),
        "certificate_candidate_events": len(cert_events),
        "hypothesis_downgrade_events": len(reconstruction["hypothesis_downgrade"]),
        "forbidden_transition_events": len(reconstruction["forbidden_transition"]),
        "residual_preservation_events": len(reconstruction["residual_preservation"]),
        "collapse_events": len(reconstruction["collapse_event"]),
        "forensic_note": "Certificate reconstruction is evidence-bound and replay-driven.",
    }
