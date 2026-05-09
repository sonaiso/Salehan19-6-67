"""Test: API error handling returns JSON-structured errors (no stack traces)."""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


def test_invalid_json_body_returns_422():
    resp = client.post(
        "/classify",
        data="not-json",
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 422


def test_error_response_has_error_code():
    resp = client.post("/classify", json={"text": "  "})
    data = resp.json()
    assert "error_code" in data


def test_error_response_has_message():
    resp = client.post("/classify", json={"text": "  "})
    data = resp.json()
    assert "message" in data


def test_error_response_has_request_id():
    resp = client.post("/classify", json={"text": "  "})
    data = resp.json()
    assert "request_id" in data


def test_error_response_has_details():
    resp = client.post("/classify", json={"text": "  "})
    data = resp.json()
    assert "details" in data


def test_error_response_no_traceback():
    """Responses must not contain Python traceback text."""
    resp = client.post("/classify", json={"text": "  "})
    text = resp.text
    assert "Traceback" not in text
    assert "traceback" not in text


def test_unsupported_profile_error_code():
    resp = client.post("/industrial/test", json={"profile": "bad_profile"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error_code"] == "UNSUPPORTED_PROFILE"


def test_missing_required_field_422():
    resp = client.post("/classify", json={})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error_code"] == "VALIDATION_ERROR"


def test_unknown_route_404():
    resp = client.get("/nonexistent-endpoint")
    assert resp.status_code == 404


def test_error_is_json():
    resp = client.post("/classify", json={"text": "  "})
    # Must parse as JSON
    data = json.loads(resp.text)
    assert isinstance(data, dict)
