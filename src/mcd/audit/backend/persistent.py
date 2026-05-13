"""Persistent audit backend for durable traces + immutable governance events."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcd.audit.replay import extract_judgment_sequence, reconstruct_certificate_forensics, replay_trace_events
from mcd.events import ImmutableGovernanceEventLog
from mcd.observability.store import (
    GovernanceTraceEvent,
    PersistentTraceStore,
    governance_event_types_from_payload,
)


@dataclass
class AuditReplaySnapshot:
    replay: dict[str, Any]
    certificate_forensics: dict[str, Any]
    immutable_log_valid: bool
    immutable_log_failures: list[str]
    replay_integrity_contract: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay": self.replay,
            "certificate_forensics": self.certificate_forensics,
            "immutable_log_valid": self.immutable_log_valid,
            "immutable_log_failures": self.immutable_log_failures,
            "replay_integrity_contract": self.replay_integrity_contract,
        }


class PersistentAuditBackend:
    """Durable audit backend with event-sourced governance log."""

    def __init__(
        self,
        *,
        trace_store: PersistentTraceStore | None = None,
        event_log: ImmutableGovernanceEventLog | None = None,
    ) -> None:
        self._trace_store = trace_store or PersistentTraceStore()
        self._event_log = event_log or ImmutableGovernanceEventLog()

    def append_trace(self, trace: GovernanceTraceEvent) -> None:
        payload = trace.to_dict()
        request_id = payload.get("request_id", "")
        replay_id = payload.get("replay_id", request_id)
        self._trace_store.append(trace)
        self._event_log.append(
            event_type="trace_recorded",
            request_id=request_id,
            replay_id=replay_id,
            payload=payload,
        )
        for event_type in governance_event_types_from_payload(payload):
            self.append_governance_event(
                event_type=event_type,
                request_id=request_id,
                replay_id=replay_id,
                payload=payload,
            )

    def append_governance_event(
        self,
        *,
        event_type: str,
        request_id: str,
        replay_id: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._event_log.append(
            event_type=event_type,
            request_id=request_id,
            replay_id=replay_id,
            payload=payload or {},
        )

    def read_traces(self) -> list[dict[str, Any]]:
        return self._trace_store.read_all()

    def read_events(self) -> list[dict[str, Any]]:
        return self._event_log.read_all_dicts()

    def replay_from_events(self, replay_id: str | None = None) -> AuditReplaySnapshot:
        """Replay immutable governance events, optionally scoped to one replay_id."""
        events = self.read_events()
        governance_events: list[dict[str, Any]] = []
        for event in events:
            if replay_id and event.get("replay_id") != replay_id:
                continue
            payload = dict(event.get("payload") or {})
            payload.setdefault("request_id", event.get("request_id", ""))
            payload.setdefault("replay_id", event.get("replay_id", ""))
            payload.setdefault("event_type", event.get("event_type", ""))
            governance_events.append(payload)
        replay = replay_trace_events(governance_events).to_dict()
        immutable_ok, immutable_failures = self._event_log.verify_integrity()
        forensics = reconstruct_certificate_forensics(governance_events)
        original_sequence = extract_judgment_sequence(governance_events)
        replay_sequence = list(replay.get("judgment_sequence", []))
        judgment_consistent = original_sequence == replay_sequence
        replay_integrity_contract = {
            "statement": "Precondition: ValidEventLog=true. Guarantee: Replay(log) preserves public_judgment sequence.",
            "valid_event_log": immutable_ok,
            "original_judgment_sequence": original_sequence,
            "replayed_judgment_sequence": replay_sequence,
            "judgment_consistent": judgment_consistent,
            "contract_holds": immutable_ok and judgment_consistent and bool(replay.get("replay_success", False)),
        }
        return AuditReplaySnapshot(
            replay=replay,
            certificate_forensics=forensics,
            immutable_log_valid=immutable_ok,
            immutable_log_failures=immutable_failures,
            replay_integrity_contract=replay_integrity_contract,
        )

    def verify_event_immutability(self) -> tuple[bool, list[str]]:
        return self._event_log.verify_integrity()

    def clear(self) -> None:
        self._trace_store.clear()
        self._event_log.clear()
