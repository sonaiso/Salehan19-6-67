"""Test: API schema stability — no Enum leakage, no dataclass leakage, JSON roundtrip.

Phase 6.1 additions: schema_stability checker integration, _has_enum_leakage unit tests.
"""
from __future__ import annotations

import enum
import json
import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.serializers import safe_serialize
from mcd.api.schema_stability import (
    run_schema_checks,
    _has_enum_leakage,
    _has_dataclass_leakage,
    _all_numbers_serializable,
)

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
    assert re_parsed["status"] == "success"


def test_reasoning_json_roundtrip():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    data = json.loads(resp.text)
    re_encoded = json.dumps(data)
    re_parsed = json.loads(re_encoded)
    assert re_parsed["status"] == "success"


def test_quality_lock_json_roundtrip():
    resp = client.post("/curriculum/quality-lock")
    data = json.loads(resp.text)
    re_encoded = json.dumps(data)
    re_parsed = json.loads(re_encoded)
    assert re_parsed["status"] == "success"


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


# ---------------------------------------------------------------------------
# Phase 6.1 — schema_stability checker integration
# ---------------------------------------------------------------------------


def test_api_schema_stability_checker_runs():
    result = run_schema_checks(client)
    assert result is not None
    assert result.total > 0


def test_api_schema_no_enum_leakage():
    result = run_schema_checks(client)
    enum_checks = [c for c in result.checks if "no_enum_leakage" in c["check"] or "no_enum_class_names" in c["check"]]
    assert len(enum_checks) > 0
    for check in enum_checks:
        assert check["passed"], f"Enum leakage detected: {check['check']}"


def test_api_schema_json_roundtrip():
    result = run_schema_checks(client)
    roundtrip_checks = [c for c in result.checks if "json_roundtrip" in c["check"]]
    assert len(roundtrip_checks) > 0
    for check in roundtrip_checks:
        assert check["passed"], f"JSON roundtrip failed: {check['check']}"


def test_api_schema_stability_checker_passes():
    result = run_schema_checks(client)
    failed = [c for c in result.checks if not c["passed"]]
    assert result.passed, f"Schema stability checks failed: {failed}"


def test_reasoning_evaluate_schema_stable():
    resp = client.post("/v1/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert "classification" in data
    assert "evidence_need" in data
    assert "certainty_policy" in data
    assert isinstance(data["certainty_policy"], str)


def test_classify_schema_stable():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert "intent" in data
    assert "certainty_policy" in data
    assert "routing_engine" in data


def test_has_enum_leakage_helper():
    class E(enum.Enum):
        A = "a"
    assert _has_enum_leakage({"x": E.A})
    assert not _has_enum_leakage({"x": "a"})


def test_has_dataclass_leakage_helper():
    import dataclasses

    @dataclasses.dataclass
    class D:
        val: int = 1

    assert _has_dataclass_leakage({"d": D()})
    assert not _has_dataclass_leakage({"d": {"val": 1}})


def test_all_numbers_serializable_helper():
    import math
    assert _all_numbers_serializable({"x": 1.0, "y": 2})
    assert not _all_numbers_serializable({"x": float("nan")})
    assert not _all_numbers_serializable({"x": float("inf")})
