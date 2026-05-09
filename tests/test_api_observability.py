"""Test: API observability — in-memory request tracing.

Phase 6.1 acceptance:
- Each request creates an APILogTrace record
- Trace has path, method, status_code, execution_time_ms
- TraceStore holds recent traces
- No persistent storage (purely in-memory)
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.observability import APILogTrace, TraceStore, get_trace_store

client = TestClient(build_app())

_ARABIC_TEXT = "ما هو دور العقل في الإسلام؟"


# ---------------------------------------------------------------------------
# TraceStore unit tests
# ---------------------------------------------------------------------------


def test_trace_store_records_trace():
    store = TraceStore()
    t = APILogTrace(
        request_id="abc",
        path="/v1/classify",
        method="POST",
        status_code=200,
        execution_time_ms=12.5,
    )
    store.record(t)
    assert len(store.all()) == 1


def test_trace_store_recent_returns_n():
    store = TraceStore()
    for i in range(10):
        store.record(APILogTrace(
            request_id=f"id-{i}",
            path="/v1/classify",
            method="POST",
            status_code=200,
            execution_time_ms=float(i),
        ))
    recent = store.recent(5)
    assert len(recent) == 5


def test_trace_store_max_traces():
    store = TraceStore()
    for i in range(store._MAX_TRACES + 50):
        store.record(APILogTrace(
            request_id=f"id-{i}",
            path="/test",
            method="GET",
            status_code=200,
            execution_time_ms=1.0,
        ))
    assert len(store.all()) == store._MAX_TRACES


def test_trace_store_clear():
    store = TraceStore()
    store.record(APILogTrace("x", "/", "GET", 200, 1.0))
    store.clear()
    assert len(store.all()) == 0


def test_trace_store_thread_safe():
    import threading
    store = TraceStore()
    errors = []

    def add_traces():
        try:
            for i in range(20):
                store.record(APILogTrace(f"id-{i}", "/test", "GET", 200, 1.0))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=add_traces) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors


# ---------------------------------------------------------------------------
# APILogTrace dataclass
# ---------------------------------------------------------------------------


def test_trace_has_required_fields():
    t = APILogTrace(
        request_id="req-001",
        path="/v1/classify",
        method="POST",
        status_code=200,
        execution_time_ms=42.5,
    )
    assert t.request_id == "req-001"
    assert t.path == "/v1/classify"
    assert t.method == "POST"
    assert t.status_code == 200
    assert t.execution_time_ms == 42.5


def test_trace_to_dict():
    t = APILogTrace(
        request_id="req-001",
        path="/v1/classify",
        method="POST",
        status_code=200,
        execution_time_ms=42.5,
        warning_count=1,
        error_count=0,
    )
    d = t.to_dict()
    assert d["request_id"] == "req-001"
    assert d["path"] == "/v1/classify"
    assert d["method"] == "POST"
    assert d["status_code"] == 200
    assert d["execution_time_ms"] == 42.5
    assert d["warning_count"] == 1
    assert d["error_count"] == 0


def test_trace_has_path_method_latency():
    t = APILogTrace(
        request_id="r",
        path="/v1/health",
        method="GET",
        status_code=200,
        execution_time_ms=5.0,
    )
    d = t.to_dict()
    assert "path" in d
    assert "method" in d
    assert "execution_time_ms" in d


# ---------------------------------------------------------------------------
# Request creates trace in store (integration)
# ---------------------------------------------------------------------------


def test_request_trace_created():
    """After a request, the trace store must have at least one trace."""
    store = get_trace_store()
    initial_count = len(store.all())
    client.get("/v1/health")
    assert len(store.all()) > initial_count


def test_trace_has_correct_path():
    store = get_trace_store()
    store.clear()
    client.get("/v1/health")
    traces = store.all()
    assert any(t.path == "/v1/health" for t in traces)


def test_trace_has_correct_method():
    store = get_trace_store()
    store.clear()
    client.get("/v1/health")
    traces = store.all()
    assert any(t.method == "GET" for t in traces)


def test_trace_has_positive_latency():
    store = get_trace_store()
    store.clear()
    client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    traces = store.all()
    assert any(t.execution_time_ms >= 0 for t in traces)


def test_trace_has_status_code():
    store = get_trace_store()
    store.clear()
    client.get("/v1/health")
    traces = store.all()
    assert any(t.status_code == 200 for t in traces)


def test_debug_mode_includes_trace():
    """In debug mode (/classify with include_debug=True), trace is still recorded."""
    store = get_trace_store()
    store.clear()
    client.post("/v1/classify", json={"text": _ARABIC_TEXT, "include_debug": True})
    traces = store.all()
    assert any("/v1/classify" in t.path for t in traces)


def test_get_trace_store_returns_singleton():
    store1 = get_trace_store()
    store2 = get_trace_store()
    assert store1 is store2
