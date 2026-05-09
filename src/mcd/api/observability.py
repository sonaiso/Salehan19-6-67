"""API observability — lightweight in-memory request tracing.

Phase 6.1: No persistent storage. Traces are held in memory and
accessible via debug mode. No DB, no network, no file I/O.

APILogTrace fields:
- request_id
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

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "execution_time_ms": self.execution_time_ms,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
        }


class TraceStore:
    """Thread-safe in-memory store for recent request traces.

    Keeps at most ``max_traces`` entries (oldest discarded first).
    """
    _MAX_TRACES = 200

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._traces: List[APILogTrace] = []

    def record(self, trace: APILogTrace) -> None:
        with self._lock:
            self._traces.append(trace)
            if len(self._traces) > self._MAX_TRACES:
                self._traces = self._traces[-self._MAX_TRACES:]

    def recent(self, n: int = 20) -> List[APILogTrace]:
        with self._lock:
            return list(self._traces[-n:])

    def all(self) -> List[APILogTrace]:
        with self._lock:
            return list(self._traces)

    def clear(self) -> None:
        with self._lock:
            self._traces.clear()


# Module-level singleton
_store = TraceStore()


def get_trace_store() -> TraceStore:
    """Return the module-level TraceStore singleton."""
    return _store
