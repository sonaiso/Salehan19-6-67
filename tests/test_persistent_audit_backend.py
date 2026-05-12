from __future__ import annotations

import threading

from mcd.audit.backend import PersistentAuditBackend
from mcd.observability import GovernanceTraceEvent


def _sample_trace(i: int, **overrides) -> GovernanceTraceEvent:
    payload = dict(
        request_id=f"req-{i}",
        replay_id=f"replay-{i}",
        path="/v1/classify",
        method="POST",
        status_code=200,
        execution_time_ms=1.2,
        residual_preserved=True,
        trace_complete=True,
        governance_consistent=True,
        public_judgment="zero",
    )
    payload.update(overrides)
    return GovernanceTraceEvent(**payload)


def test_audit_persistence_survives_reopen(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_sample_trace(1, public_judgment="certificate"))

    reopened = PersistentAuditBackend()
    traces = reopened.read_traces()
    events = reopened.read_events()
    assert len(traces) == 1
    assert any(e["event_type"] == "certificate" for e in events)


def test_replay_from_stored_events(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_sample_trace(1, public_judgment="certificate"))
    backend.append_trace(_sample_trace(2, hypothesis_downgrade=True))
    backend.append_trace(_sample_trace(3, forbidden_transition=True))
    backend.append_trace(_sample_trace(4, collapse_event=True))

    snapshot = backend.replay_from_events().to_dict()
    replay = snapshot["replay"]
    assert replay["replay_success"] is True
    assert replay["reconstruction"]["certificate"] >= 1
    assert replay["reconstruction"]["hypothesis_downgrade"] >= 1
    assert replay["reconstruction"]["forbidden_transition"] >= 1
    assert replay["reconstruction"]["collapse_event"] >= 1
    assert replay["reconstruction"]["residual_preservation"] >= 1


def test_trace_integrity(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_sample_trace(1))
    trace = backend.read_traces()[0]
    assert trace["request_id"] == "req-1"
    assert trace["replay_id"] == "replay-1"
    assert trace["residual_preserved"] is True


def test_concurrent_writes(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()

    errors: list[Exception] = []

    def _write(offset: int) -> None:
        try:
            for i in range(25):
                backend.append_trace(_sample_trace(offset + i))
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(exc)

    threads = [threading.Thread(target=_write, args=(n * 1000,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(backend.read_traces()) == 100


def test_certificate_forensic_reconstruction(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_sample_trace(10, public_judgment="certificate", residual_preserved=True))
    backend.append_trace(_sample_trace(11, hypothesis_downgrade=True, public_judgment="hypothesis"))

    snapshot = backend.replay_from_events().to_dict()
    forensics = snapshot["certificate_forensics"]
    assert forensics["certificate_candidate_events"] >= 1
    assert forensics["hypothesis_downgrade_events"] >= 1
    assert forensics["residual_preservation_events"] >= 1
