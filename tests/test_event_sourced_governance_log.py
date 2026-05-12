from __future__ import annotations

import json

from mcd.audit.backend import PersistentAuditBackend
from mcd.events import ImmutableGovernanceEventLog
from mcd.observability import GovernanceTraceEvent


def test_event_log_immutability_and_integrity(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    log = ImmutableGovernanceEventLog()
    log.clear()
    log.append(event_type="certificate", request_id="r1", replay_id="rp1", payload={"public_judgment": "certificate"})
    log.append(event_type="residual_preservation", request_id="r1", replay_id="rp1", payload={"residual_preserved": True})
    ok, failures = log.verify_integrity()
    assert ok is True
    assert failures == []


def test_event_log_detects_tampering(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    log = ImmutableGovernanceEventLog()
    log.clear()
    log.append(event_type="trace_recorded", request_id="r1", replay_id="rp1", payload={"k": "v"})

    log_path = tmp_path / "governance_events.jsonl"
    lines = log_path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[0])
    tampered["payload"]["k"] = "tampered"
    lines[0] = json.dumps(tampered, ensure_ascii=False)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, failures = log.verify_integrity()
    assert ok is False
    assert any("record_hash mismatch" in item for item in failures)


def test_event_sourced_replay_reconstructs_required_paths(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(
        GovernanceTraceEvent(
            request_id="req-cert",
            replay_id="rp-cert",
            path="/v1/classify",
            method="POST",
            status_code=200,
            execution_time_ms=1.0,
            public_judgment="certificate",
            residual_preserved=True,
        ),
    )
    backend.append_trace(
        GovernanceTraceEvent(
            request_id="req-hyp",
            replay_id="rp-hyp",
            path="/v1/classify",
            method="POST",
            status_code=200,
            execution_time_ms=1.0,
            hypothesis_downgrade=True,
            public_judgment="hypothesis",
            residual_preserved=True,
            forbidden_transition=True,
            collapse_event=True,
        ),
    )

    replay = backend.replay_from_events().to_dict()["replay"]
    assert replay["reconstruction"]["certificate"] >= 1
    assert replay["reconstruction"]["hypothesis_downgrade"] >= 1
    assert replay["reconstruction"]["forbidden_transition"] >= 1
    assert replay["reconstruction"]["residual_preservation"] >= 1
    assert replay["reconstruction"]["collapse_event"] >= 1


def test_event_log_append_order_is_monotonic(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    log = ImmutableGovernanceEventLog()
    log.clear()
    log.append(event_type="trace_recorded", request_id="r1", replay_id="rp1", payload={})
    log.append(event_type="trace_recorded", request_id="r2", replay_id="rp2", payload={})
    records = log.read_all()
    assert [r.index for r in records] == [0, 1]
