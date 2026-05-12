from __future__ import annotations

from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.observability import get_trace_store


def test_prometheus_metrics_exporter_exposes_governance_health(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    client = TestClient(build_app())
    get_trace_store().clear()

    client.get("/v1/health")
    resp = client.get("/v1/metrics/prometheus")
    assert resp.status_code == 200
    text = resp.text
    assert "mcd_trace_event_count" in text
    assert "mcd_governance_event_count" in text
    assert "mcd_event_log_immutable" in text
    assert "mcd_replay_success" in text


def test_production_readiness_endpoints(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    monkeypatch.setenv("MCD_API_PROFILE", "production")
    client = TestClient(build_app())
    get_trace_store().clear()

    client.get("/v1/health")

    live = client.get("/v1/production/livez")
    ready = client.get("/v1/production/readyz")
    legacy_ready = client.get("/v1/readiness")

    assert live.status_code == 200
    assert ready.status_code == 200
    assert legacy_ready.status_code == 200

    assert live.json()["status"] == "ok"
    assert ready.json()["status"] in {"ready", "degraded"}
    assert "immutable_event_log_valid" in ready.json()
    assert "governance_events" in ready.json()
    assert "trace_events" in legacy_ready.json()


def test_audit_replay_endpoint_reconstructs_governance_paths(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    client = TestClient(build_app())
    get_trace_store().clear()

    client.get("/v1/health")
    replay = client.get("/v1/audit/replay")
    assert replay.status_code == 200
    data = replay.json()
    assert "reconstruction" in data
    assert "certificate" in data["reconstruction"]
    assert "residual_preservation" in data["reconstruction"]


def test_metrics_json_contains_runtime_snapshot(monkeypatch, tmp_path):
    monkeypatch.setenv("MCD_AUDIT_DIR", str(tmp_path))
    client = TestClient(build_app())
    get_trace_store().clear()
    client.get("/v1/health")
    payload = client.get("/v1/metrics").json()
    assert "trace_event_count" in payload
    assert "governance_event_count" in payload
    assert "governance_metrics" in payload
