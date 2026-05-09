"""Test: API schema stability — no Enum leakage, no dataclass leakage, JSON roundtrip."""
from __future__ import annotations

import enum
import json
import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.serializers import safe_serialize

client = TestClient(build_app())

_ARABIC_TEXT = "ما هي أسباب ضعف الإرادة عند الإنسان؟"


# ---------------------------------------------------------------------------
# JSON roundtrip
# ---------------------------------------------------------------------------


def test_classify_json_roundtrip():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = json.loads(resp.text)
    re_encoded = json.dumps(data)
    re_parsed = json.loads(re_encoded)
    assert re_parsed["status"] == "ok"


def test_reasoning_json_roundtrip():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = json.loads(resp.text)
    re_encoded = json.dumps(data)
    re_parsed = json.loads(re_encoded)
    assert re_parsed["status"] == "ok"


def test_quality_lock_json_roundtrip():
    resp = client.post("/curriculum/quality-lock")
    data = json.loads(resp.text)
    re_encoded = json.dumps(data)
    re_parsed = json.loads(re_encoded)
    assert re_parsed["status"] == "ok"


# ---------------------------------------------------------------------------
# No Enum leakage
# ---------------------------------------------------------------------------


def test_classify_no_enum_in_data():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    raw_text = resp.text
    # If enum objects leaked, JSON would contain class references
    assert "<" not in raw_text
    assert "JudgmentType" not in raw_text
    assert "EvidenceNeed" not in raw_text


def test_reasoning_certainty_policy_is_str():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    policy = resp.json()["data"]["certainty_policy"]
    assert isinstance(policy, str)


# ---------------------------------------------------------------------------
# No dataclass leakage
# ---------------------------------------------------------------------------


def test_classify_response_is_flat_json():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()
    # data must be a dict (not a dataclass repr)
    assert isinstance(data, dict)
    assert isinstance(data["data"], dict)


def test_quality_lock_response_is_flat_json():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()
    assert isinstance(data, dict)
    assert isinstance(data["data"], dict)


# ---------------------------------------------------------------------------
# safe_serialize unit tests
# ---------------------------------------------------------------------------


def test_safe_serialize_enum():
    class Color(enum.Enum):
        RED = "red"

    result = safe_serialize({"color": Color.RED})
    assert result["color"] == "red"


def test_safe_serialize_list_of_enums():
    class Status(enum.Enum):
        OK = "ok"
        FAIL = "fail"

    result = safe_serialize({"items": [Status.OK, Status.FAIL]})
    assert result["items"] == ["ok", "fail"]


def test_safe_serialize_none():
    result = safe_serialize(None)
    assert result == {"result": None}


def test_safe_serialize_plain_dict():
    result = safe_serialize({"a": 1, "b": "hello"})
    assert result == {"a": 1, "b": "hello"}


# ---------------------------------------------------------------------------
# Schema fields present on every response
# ---------------------------------------------------------------------------


def test_api_response_fields_classify():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    data = resp.json()
    for field in ("request_id", "status", "data", "warnings", "errors", "execution_time_ms"):
        assert field in data, f"Missing field: {field}"


def test_api_response_fields_reasoning():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = resp.json()
    for field in ("request_id", "status", "data", "warnings", "errors", "execution_time_ms"):
        assert field in data, f"Missing field: {field}"


def test_api_response_fields_quality_lock():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()
    for field in ("request_id", "status", "data", "warnings", "errors", "execution_time_ms"):
        assert field in data, f"Missing field: {field}"


def test_api_response_fields_pre_api():
    resp = client.post("/pre-api/qualification")
    data = resp.json()
    for field in ("request_id", "status", "data", "warnings", "errors", "execution_time_ms"):
        assert field in data, f"Missing field: {field}"
