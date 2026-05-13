from __future__ import annotations

import json

from mcd.audit.backend import PersistentAuditBackend
from mcd.observability import GovernanceTraceEvent


def _trace(i: int, **overrides) -> GovernanceTraceEvent:
    payload = {
        "request_id": f"rq-{i}",
        "replay_id": "rp-1",
        "path": "/v1/classify",
        "method": "POST",
        "status_code": 200,
        "execution_time_ms": 1.0,
        "residual_preserved": True,
        "public_judgment": "hypothesis",
    }
    payload.update(overrides)
    return GovernanceTraceEvent(**payload)


def test_replay_integrity_contract_holds_for_valid_log(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_trace(1, public_judgment="certificate"))
    backend.append_trace(_trace(2, public_judgment="hypothesis", hypothesis_downgrade=True))

    contract = backend.replay_from_events().to_dict()["replay_integrity_contract"]
    assert contract["valid_event_log"] is True
    assert contract["judgment_consistent"] is True
    assert contract["contract_holds"] is True


def test_replay_integrity_contract_fails_for_tampered_log(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    backend = PersistentAuditBackend()
    backend.clear()
    backend.append_trace(_trace(1, public_judgment="certificate"))

    log_path = tmp_path / "governance_events.jsonl"
    raw = log_path.read_text(encoding="utf-8").splitlines()
    event = json.loads(raw[0])
    event["payload"]["public_judgment"] = "zero"
    raw[0] = json.dumps(event, ensure_ascii=False)
    log_path.write_text("\n".join(raw) + "\n", encoding="utf-8")

    snapshot = backend.replay_from_events().to_dict()
    contract = snapshot["replay_integrity_contract"]
    assert snapshot["immutable_log_valid"] is False
    assert contract["valid_event_log"] is False
    assert contract["contract_holds"] is False
