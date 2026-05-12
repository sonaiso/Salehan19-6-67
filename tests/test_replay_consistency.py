from __future__ import annotations

from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.observability import get_trace_store
from mcd.audit import replay_trace_events


def test_replay_consistency_for_persistent_traces(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "local")
    client = TestClient(build_app())
    store = get_trace_store()
    store.clear()
    client.get("/v1/health")
    client.get("/v1/version")

    events = store.all_persistent()
    replay1 = replay_trace_events(events).to_dict()
    replay2 = replay_trace_events(events).to_dict()
    assert replay1["replay_success"] is True
    assert replay1["metrics"] == replay2["metrics"]


def test_replay_endpoint_matches_offline_replay(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "local")
    client = TestClient(build_app())
    store = get_trace_store()
    store.clear()
    client.get("/v1/health")

    offline = replay_trace_events(store.all_persistent()).to_dict()
    online = client.get("/v1/audit/replay").json()
    assert online["replay_success"] == offline["replay_success"]
    assert online["total_events"] == offline["total_events"]

