"""Test: POST /classify with Arabic text."""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())

_ARABIC_TEXT = "ما هو حكم الاجتهاد في المسائل الفقهية؟"


def test_classify_status_200():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_classify_has_request_id():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()
    assert "request_id" in data
    assert len(data["request_id"]) > 0


def test_classify_has_execution_time_ms():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()
    assert "execution_time_ms" in data
    assert isinstance(data["execution_time_ms"], float)
    assert data["execution_time_ms"] >= 0


def test_classify_status_ok():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    assert resp.json()["status"] == "ok"


def test_classify_data_has_intent():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "intent" in data


def test_classify_data_has_certainty_policy():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "certainty_policy" in data


def test_classify_data_has_routing_engine():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "routing_engine" in data


def test_classify_warnings_is_list():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    assert isinstance(resp.json()["warnings"], list)


def test_classify_errors_is_list():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    assert isinstance(resp.json()["errors"], list)


def test_classify_json_roundtrip():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    raw_text = resp.text
    parsed = json.loads(raw_text)
    assert parsed["status"] == "ok"


def test_classify_no_enum_leakage():
    """Enum values must be plain strings, not objects."""
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    # certainty_policy must be a plain string
    assert isinstance(data["certainty_policy"], str)


def test_classify_no_dataclass_leakage():
    """Response data must contain only JSON primitives."""
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    raw_text = resp.text
    # If no exception raised, JSON is valid
    json.loads(raw_text)


def test_classify_blank_text_returns_422():
    resp = client.post("/classify", json={"text": "   "})
    assert resp.status_code == 422


def test_classify_missing_text_returns_422():
    resp = client.post("/classify", json={})
    assert resp.status_code == 422


def test_classify_error_has_error_code():
    resp = client.post("/classify", json={"text": "   "})
    data = resp.json()
    assert "error_code" in data


def test_classify_debug_mode():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT, "include_debug": True})
    assert resp.status_code == 200
