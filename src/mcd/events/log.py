"""Immutable governance event log with append-only semantics."""
from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _default_event_log_file() -> str:
    root = os.environ.get("MCD_AUDIT_DIR", os.path.join(os.getcwd(), ".mcd_audit"))
    os.makedirs(root, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except PermissionError:
        pass
    return os.path.join(root, "governance_events.jsonl")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(payload: dict[str, Any]) -> str:
    """Return stable JSON encoding used by the hash chain.

    Hash verification depends on byte-identical serialization across writes/reads,
    so keys are sorted and whitespace is minimized.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GovernanceEventRecord:
    index: int
    event_id: str
    event_type: str
    request_id: str
    replay_id: str
    timestamp: str
    payload: dict[str, Any]
    previous_hash: str
    record_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "request_id": self.request_id,
            "replay_id": self.replay_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "record_hash": self.record_hash,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "GovernanceEventRecord":
        return cls(
            index=int(raw["index"]),
            event_id=str(raw["event_id"]),
            event_type=str(raw["event_type"]),
            request_id=str(raw.get("request_id", "")),
            replay_id=str(raw.get("replay_id", "")),
            timestamp=str(raw["timestamp"]),
            payload=dict(raw.get("payload", {})),
            previous_hash=str(raw.get("previous_hash", "")),
            record_hash=str(raw["record_hash"]),
        )


class ImmutableGovernanceEventLog:
    """Thread-safe append-only event log with hash-chain immutability checks."""

    def __init__(self, log_file: str | None = None) -> None:
        self._log_file = log_file or _default_event_log_file()
        self._lock = threading.Lock()
        self._last_index = -1
        self._last_hash = ""
        self._load_tail_state()

    def _load_tail_state(self) -> None:
        if not os.path.exists(self._log_file):
            return
        with open(self._log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                self._last_index = int(raw.get("index", self._last_index))
                self._last_hash = str(raw.get("record_hash", self._last_hash))

    def append(
        self,
        *,
        event_type: str,
        request_id: str,
        replay_id: str,
        payload: dict[str, Any] | None = None,
        event_id: str | None = None,
        timestamp: str | None = None,
    ) -> GovernanceEventRecord:
        data = payload or {}
        with self._lock:
            index = self._last_index + 1
            ts = timestamp or _utc_now_iso()
            eid = event_id or f"evt-{index:09d}"
            body = {
                "index": index,
                "event_id": eid,
                "event_type": event_type,
                "request_id": request_id,
                "replay_id": replay_id,
                "timestamp": ts,
                "payload": data,
                "previous_hash": self._last_hash,
            }
            body["record_hash"] = _hash(body)
            record = GovernanceEventRecord.from_dict(body)
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._last_index = index
            self._last_hash = record.record_hash
            return record

    def read_all(self) -> list[GovernanceEventRecord]:
        if not os.path.exists(self._log_file):
            return []
        out: list[GovernanceEventRecord] = []
        with self._lock:
            with open(self._log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    out.append(GovernanceEventRecord.from_dict(json.loads(line)))
        return out

    def read_all_dicts(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.read_all()]

    def verify_integrity(self) -> tuple[bool, list[str]]:
        failures: list[str] = []
        previous_hash = ""
        previous_index = -1
        for i, record in enumerate(self.read_all()):
            if record.index != previous_index + 1:
                failures.append(
                    f"event[{i}] index sequence broken: expected {previous_index + 1}, got {record.index}",
                )
            if record.previous_hash != previous_hash:
                failures.append(
                    f"event[{i}] previous_hash mismatch: expected {previous_hash}, got {record.previous_hash}",
                )
            payload = {
                "index": record.index,
                "event_id": record.event_id,
                "event_type": record.event_type,
                "request_id": record.request_id,
                "replay_id": record.replay_id,
                "timestamp": record.timestamp,
                "payload": record.payload,
                "previous_hash": record.previous_hash,
            }
            computed_hash = _hash(payload)
            if computed_hash != record.record_hash:
                failures.append(f"event[{i}] record_hash mismatch")
            previous_hash = record.record_hash
            previous_index = record.index
        return (len(failures) == 0, failures)

    def clear(self) -> None:
        with self._lock:
            if os.path.exists(self._log_file):
                os.remove(self._log_file)
            self._last_index = -1
            self._last_hash = ""
