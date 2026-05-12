"""Persistent trace storage for industrial observability."""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mcd.events import ImmutableGovernanceEventLog


def _default_trace_file() -> str:
    root = os.environ.get("MCD_AUDIT_DIR", os.path.join(os.getcwd(), ".mcd_audit"))
    os.makedirs(root, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except PermissionError:
        pass
    return os.path.join(root, "api_traces.jsonl")


@dataclass
class GovernanceTraceEvent:
    request_id: str
    replay_id: str
    path: str
    method: str
    status_code: int
    execution_time_ms: float
    forbidden_transition: bool = False
    certificate_blocked: bool = False
    residual_preserved: bool = True
    trace_complete: bool = True
    governance_consistent: bool = True
    collapse_event: bool = False
    hypothesis_downgrade: bool = False
    public_judgment: str = "zero"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "replay_id": self.replay_id,
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "execution_time_ms": self.execution_time_ms,
            "forbidden_transition": self.forbidden_transition,
            "certificate_blocked": self.certificate_blocked,
            "residual_preserved": self.residual_preserved,
            "trace_complete": self.trace_complete,
            "governance_consistent": self.governance_consistent,
            "collapse_event": self.collapse_event,
            "hypothesis_downgrade": self.hypothesis_downgrade,
            "public_judgment": self.public_judgment,
        }


class PersistentTraceStore:
    def __init__(self, trace_file: str | None = None) -> None:
        self._trace_file = trace_file or _default_trace_file()
        self._lock = threading.Lock()

    def append(self, event: GovernanceTraceEvent) -> None:
        payload = event.to_dict()
        with self._lock:
            with open(self._trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict]:
        if not os.path.exists(self._trace_file):
            return []
        out: list[dict] = []
        with self._lock:
            with open(self._trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    out.append(json.loads(line))
        return out

    def clear(self) -> None:
        with self._lock:
            if os.path.exists(self._trace_file):
                os.remove(self._trace_file)


class GovernanceEventSink:
    """Append governance events to immutable event log."""

    def __init__(self, event_log: ImmutableGovernanceEventLog | None = None) -> None:
        self._event_log = event_log or ImmutableGovernanceEventLog()

    def append_trace_events(self, payload: dict[str, Any]) -> None:
        request_id = str(payload.get("request_id", ""))
        replay_id = str(payload.get("replay_id", request_id))
        self._event_log.append(
            event_type="trace_recorded",
            request_id=request_id,
            replay_id=replay_id,
            payload=payload,
        )
        event_flags = (
            ("certificate", payload.get("public_judgment", "").strip().lower() == "certificate"),
            ("hypothesis_downgrade", bool(payload.get("hypothesis_downgrade", False))),
            ("forbidden_transition", bool(payload.get("forbidden_transition", False))),
            ("residual_preservation", bool(payload.get("residual_preserved", False))),
            ("collapse_event", bool(payload.get("collapse_event", False))),
        )
        for event_type, should_emit in event_flags:
            if should_emit:
                self._event_log.append(
                    event_type=event_type,
                    request_id=request_id,
                    replay_id=replay_id,
                    payload=payload,
                )

    def clear(self) -> None:
        self._event_log.clear()
