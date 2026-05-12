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

    def to_dict(self) -> dict:
        return {
            "total_events": self.total_events,
            "replay_success": self.replay_success,
            "metrics": self.metrics,
            "failures": self.failures,
        }


def replay_trace_events(events: list[dict]) -> ReplayResult:
    failures: list[str] = []
    for i, e in enumerate(events):
        if not e.get("request_id"):
            failures.append(f"event[{i}] missing request_id")
        if not e.get("replay_id"):
            failures.append(f"event[{i}] missing replay_id")
    metrics = compute_governance_metrics(events).to_dict()
    return ReplayResult(
        total_events=len(events),
        replay_success=len(failures) == 0,
        metrics=metrics,
        failures=failures,
    )


def reconstruct_certificate_forensics(events: list[dict]) -> dict:
    cert_events = [e for e in events if e.get("status_code") == 200]
    return {
        "events_considered": len(events),
        "certificate_candidate_events": len(cert_events),
        "forensic_note": "Certificate reconstruction is evidence-bound and replay-driven.",
    }

