"""Test: Unified response envelope on all POST endpoints.

Phase 6.1 acceptance criteria:
- All POST endpoints return envelope: request_id, status, data, warnings, errors, execution_time_ms
- status is "success" (not "ok")
- warnings is a list
- errors is a list
- execution_time_ms is a non-negative float
- request_id is a non-empty string
- data is a dict

These tests MUST FAIL if:
- endpoint returns raw dict without envelope
- request_id is absent
- execution_time_ms is absent
- status is not 'success' or 'error'
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())

_ARABIC_TEXT = "ما هي أسباب ضعف الإرادة عند الإنسان؟"

# All POST v1 endpoints to test with their default payloads
_POST_ENDPOINTS = [
    ("/v1/classify", {"text": _ARABIC_TEXT}),
    ("/v1/curriculum/evaluate", {"profile": "full_curriculum"}),
    ("/v1/curriculum/quality-lock", None),
    ("/v1/industrial/test", {"profile": "quick"}),
    ("/v1/pre-api/qualification", None),
    ("/v1/reasoning/evaluate", {"text": _ARABIC_TEXT}),
]


def _post(endpoint: str, body: dict | None) -> dict:
    if body is None:
        return client.post(endpoint).json()
    return client.post(endpoint, json=body).json()


# ---------------------------------------------------------------------------
# All POST endpoints use response envelope
# ---------------------------------------------------------------------------


def test_all_post_endpoints_use_response_envelope():
    """Each POST endpoint must return all required envelope keys."""
    required = {"request_id", "status", "data", "warnings", "errors", "execution_time_ms"}
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        missing = required - set(data.keys())
        assert not missing, f"{endpoint} missing keys: {missing}"


# ---------------------------------------------------------------------------
# request_id present and non-empty
# ---------------------------------------------------------------------------


def test_request_id_present():
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert "request_id" in data, f"{endpoint} missing request_id"
        assert isinstance(data["request_id"], str), f"{endpoint} request_id not str"
        assert len(data["request_id"]) > 0, f"{endpoint} request_id is empty"


def test_request_id_different_per_request():
    """Each request must generate a unique request_id."""
    r1 = client.post("/v1/classify", json={"text": _ARABIC_TEXT}).json()["request_id"]
    r2 = client.post("/v1/classify", json={"text": _ARABIC_TEXT}).json()["request_id"]
    assert r1 != r2


# ---------------------------------------------------------------------------
# execution_time_ms present and valid
# ---------------------------------------------------------------------------


def test_execution_time_present():
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert "execution_time_ms" in data, f"{endpoint} missing execution_time_ms"
        assert isinstance(data["execution_time_ms"], (int, float)), f"{endpoint} execution_time_ms not numeric"
        assert data["execution_time_ms"] >= 0, f"{endpoint} execution_time_ms negative"


# ---------------------------------------------------------------------------
# status is 'success' (not 'ok')
# ---------------------------------------------------------------------------


def test_status_is_success():
    """status must be 'success' on successful responses — not 'ok'."""
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert data["status"] == "success", f"{endpoint} status={data['status']!r} expected 'success'"


def test_status_not_ok():
    """Fail if any endpoint returns status='ok' (old format)."""
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert data["status"] != "ok", f"{endpoint} returned legacy status='ok'"


# ---------------------------------------------------------------------------
# warnings is list
# ---------------------------------------------------------------------------


def test_warnings_is_list():
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert isinstance(data.get("warnings"), list), f"{endpoint} warnings not list"


# ---------------------------------------------------------------------------
# errors is list
# ---------------------------------------------------------------------------


def test_errors_is_list():
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert isinstance(data.get("errors"), list), f"{endpoint} errors not list"


# ---------------------------------------------------------------------------
# data is dict
# ---------------------------------------------------------------------------


def test_data_is_dict():
    for endpoint, body in _POST_ENDPOINTS:
        data = _post(endpoint, body)
        assert isinstance(data.get("data"), dict), f"{endpoint} data not dict"


# ---------------------------------------------------------------------------
# Envelope must fail if raw dict returned (validation test)
# ---------------------------------------------------------------------------


def test_classify_returns_envelope_not_raw():
    """Verify /v1/classify does NOT return a raw classification dict (no envelope)."""
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    body = resp.json()
    # If raw dict was returned, it would not have 'request_id' or 'execution_time_ms'
    assert "request_id" in body
    assert "execution_time_ms" in body
    # And status would not be in the raw classification dict
    assert "status" in body


def test_reasoning_returns_envelope_not_raw():
    """Verify /v1/reasoning/evaluate uses envelope (not raw frame dict)."""
    resp = client.post("/v1/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    body = resp.json()
    assert "request_id" in body
    assert "status" in body
    assert body["status"] == "success"
