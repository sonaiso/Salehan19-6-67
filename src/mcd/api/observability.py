"""API observability with in-memory + persistent request tracing.

APILogTrace fields:
- request_id
- replay_id
- path
- method
- status_code
- execution_time_ms
- warning_count
- error_count
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import List

from mcd.observability import GovernanceEventSink, GovernanceTraceEvent, PersistentTraceStore


@dataclass
class APILogTrace:
    """A single request trace record."""
    request_id: str
    path: str
    method: str
    status_code: int
    execution_time_ms: float
    warning_count: int = 0
    error_count: int = 0
    replay_id: str = ""
    forbidden_transition: bool = False
    certificate_blocked: bool = False
    residual_preserved: bool = True
    trace_complete: bool = True
    governance_consistent: bool = True
    collapse_event: bool = False
    hypothesis_downgrade: bool = False
    public_judgment: str = "zero"

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "replay_id": self.replay_id,
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "execution_time_ms": self.execution_time_ms,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "forbidden_transition": self.forbidden_transition,
            "certificate_blocked": self.certificate_blocked,
            "residual_preserved": self.residual_preserved,
            "trace_complete": self.trace_complete,
            "governance_consistent": self.governance_consistent,
            "collapse_event": self.collapse_event,
            "hypothesis_downgrade": self.hypothesis_downgrade,
            "public_judgment": self.public_judgment,
        }


class TraceStore:
    """Thread-safe in-memory store for recent request traces.

    Keeps at most ``max_traces`` entries (oldest discarded first).
    """
    _MAX_TRACES = 200

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._traces: List[APILogTrace] = []
        self._persistent = PersistentTraceStore()
        self._event_sink = GovernanceEventSink()

    def record(self, trace: APILogTrace) -> None:
        with self._lock:
            self._traces.append(trace)
            if len(self._traces) > self._MAX_TRACES:
                self._traces = self._traces[-self._MAX_TRACES:]
        self._persistent.append(
            GovernanceTraceEvent(
                request_id=trace.request_id,
                replay_id=trace.replay_id or trace.request_id,
                path=trace.path,
                method=trace.method,
                status_code=trace.status_code,
                execution_time_ms=trace.execution_time_ms,
                forbidden_transition=trace.forbidden_transition,
                certificate_blocked=trace.certificate_blocked,
                residual_preserved=trace.residual_preserved,
                trace_complete=trace.trace_complete,
                governance_consistent=trace.governance_consistent,
                collapse_event=trace.collapse_event,
                hypothesis_downgrade=trace.hypothesis_downgrade,
                public_judgment=trace.public_judgment,
            )
        )
        self._event_sink.append_trace_events(trace.to_dict())

    def recent(self, n: int = 20) -> List[APILogTrace]:
        with self._lock:
            return list(self._traces[-n:])

    def all(self) -> List[APILogTrace]:
        with self._lock:
            return list(self._traces)

    def clear(self) -> None:
        with self._lock:
            self._traces.clear()
        self._persistent.clear()
        self._event_sink.clear()

    def all_persistent(self) -> List[dict]:
        return self._persistent.read_all()


# Module-level singleton
_store = TraceStore()


def get_trace_store() -> TraceStore:
    """Return the module-level TraceStore singleton."""
    return _store
