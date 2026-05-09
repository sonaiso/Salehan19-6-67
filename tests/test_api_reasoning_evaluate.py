"""Test: POST /reasoning/evaluate returns full reasoning frame."""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())

_ARABIC_TEXT = "هل يجوز الاجتهاد في وجود النص الصريح؟"


def test_reasoning_evaluate_status_200():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_reasoning_evaluate_has_request_id():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()
    assert "request_id" in data
    assert len(data["request_id"]) > 0


def test_reasoning_evaluate_has_execution_time_ms():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()
    assert "execution_time_ms" in data
    assert isinstance(data["execution_time_ms"], float)


def test_reasoning_evaluate_status_ok():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.json()["status"] == "ok"


def test_reasoning_evaluate_data_has_classification():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "classification" in data
    assert "intent" in data["classification"]


def test_reasoning_evaluate_data_has_evidence_need():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "evidence_need" in data


def test_reasoning_evaluate_data_has_certainty_policy():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "certainty_policy" in data
    assert isinstance(data["certainty_policy"], str)


def test_reasoning_evaluate_data_has_warnings():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()["data"]
    assert "warnings" in data
    assert isinstance(data["warnings"], list)


def test_reasoning_evaluate_blank_text_returns_error():
    resp = client.post("/reasoning/evaluate", json={"text": "   "})
    assert resp.status_code == 422


def test_reasoning_evaluate_debug_includes_frame():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT, "include_debug": True})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "reasoning_frame" in data


def test_reasoning_evaluate_json_roundtrip():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    parsed = json.loads(resp.text)
    assert parsed["status"] == "ok"
