"""Production runtime metrics and readiness snapshots."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from mcd.api.observability import get_trace_store
from mcd.audit import replay_trace_events
from mcd.events import ImmutableGovernanceEventLog
from mcd.metrics import compute_governance_metrics


@dataclass
class RuntimeMetricsSnapshot:
    trace_event_count: int
    governance_event_count: int
    immutable_event_log_valid: bool
    replay_success: bool
    profile: str
    governance_metrics: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_event_count": self.trace_event_count,
            "governance_event_count": self.governance_event_count,
            "immutable_event_log_valid": self.immutable_event_log_valid,
            "replay_success": self.replay_success,
            "profile": self.profile,
            "governance_metrics": self.governance_metrics,
        }


def collect_runtime_metrics() -> RuntimeMetricsSnapshot:
    trace_store = get_trace_store()
    traces = trace_store.all_persistent()
    event_log = ImmutableGovernanceEventLog()
    event_records = event_log.read_all()
    immutable_ok, _ = event_log.verify_integrity()
    replay = replay_trace_events(traces).to_dict()
    metrics = compute_governance_metrics(traces).to_dict()
    profile = os.environ.get("MCD_API_PROFILE", "local").strip().lower()
    return RuntimeMetricsSnapshot(
        trace_event_count=len(traces),
        governance_event_count=len(event_records),
        immutable_event_log_valid=immutable_ok,
        replay_success=bool(replay["replay_success"]),
        profile=profile,
        governance_metrics=metrics,
    )


def build_liveness_payload() -> dict[str, Any]:
    snapshot = collect_runtime_metrics()
    return {
        "status": "ok",
        "profile": snapshot.profile,
        "governance_event_count": snapshot.governance_event_count,
    }


def build_readiness_payload() -> dict[str, Any]:
    snapshot = collect_runtime_metrics()
    ready = snapshot.replay_success and snapshot.immutable_event_log_valid
    return {
        "status": "ready" if ready else "degraded",
        "profile": snapshot.profile,
        "trace_events": snapshot.trace_event_count,
        "governance_events": snapshot.governance_event_count,
        "replay_success": snapshot.replay_success,
        "immutable_event_log_valid": snapshot.immutable_event_log_valid,
    }
