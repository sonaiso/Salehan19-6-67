"""Test: /v1 versioned routes exist and work.

Phase 6.1 acceptance:
- /v1/health
- /v1/version
- /v1/classify
- /v1/curriculum/evaluate
- /v1/curriculum/quality-lock
- /v1/industrial/test
- /v1/pre-api/qualification
- /v1/reasoning/evaluate
- Old unversioned routes still work
- /v1/version lists api_version: v1
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())

_ARABIC_TEXT = "ما هو حكم الاجتهاد في المسائل الفقهية؟"


# ---------------------------------------------------------------------------
# /v1/health
# ---------------------------------------------------------------------------


def test_v1_health_status_200():
    resp = client.get("/v1/health")
    assert resp.status_code == 200


def test_v1_health_status_ok():
    resp = client.get("/v1/health")
    assert resp.json()["status"] == "ok"


def test_v1_health_service_name():
    resp = client.get("/v1/health")
    assert resp.json()["service"] == "mcd-api"


def test_v1_health_has_version_key():
    resp = client.get("/v1/health")
    assert "version" in resp.json()


def test_v1_health_has_request_id_header():
    resp = client.get("/v1/health")
    assert "x-request-id" in resp.headers


def test_v1_health_has_execution_time_header():
    resp = client.get("/v1/health")
    assert "x-execution-time-ms" in resp.headers
    ms = float(resp.headers["x-execution-time-ms"])
    assert ms >= 0


# ---------------------------------------------------------------------------
# /v1/version
# ---------------------------------------------------------------------------


def test_v1_version_status_200():
    resp = client.get("/v1/version")
    assert resp.status_code == 200


def test_v1_version_lists_api_version():
    resp = client.get("/v1/version")
    data = resp.json()
    assert data.get("api_version") == "v1"


def test_v1_version_has_version_field():
    resp = client.get("/v1/version")
    assert "version" in resp.json()


def test_v1_version_has_layers():
    resp = client.get("/v1/version")
    layers = resp.json().get("layers")
    assert isinstance(layers, list)
    assert len(layers) > 0


# ---------------------------------------------------------------------------
# /v1/classify
# ---------------------------------------------------------------------------


def test_v1_classify_status_200():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_v1_classify_has_request_id():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert "request_id" in resp.json()


def test_v1_classify_has_execution_time_ms():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert "execution_time_ms" in resp.json()
    assert isinstance(resp.json()["execution_time_ms"], float)


def test_v1_classify_status_success():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert resp.json()["status"] == "success"


def test_v1_classify_data_has_intent():
    resp = client.post("/v1/classify", json={"text": _ARABIC_TEXT})
    assert "intent" in resp.json()["data"]


def test_v1_classify_blank_returns_422():
    resp = client.post("/v1/classify", json={"text": "   "})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /v1/curriculum/quality-lock
# ---------------------------------------------------------------------------


def test_v1_quality_lock_200():
    resp = client.post("/v1/curriculum/quality-lock")
    assert resp.status_code == 200


def test_v1_quality_lock_status_success():
    resp = client.post("/v1/curriculum/quality-lock")
    assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# /v1/pre-api/qualification
# ---------------------------------------------------------------------------


def test_v1_pre_api_qualification_200():
    resp = client.post("/v1/pre-api/qualification")
    assert resp.status_code == 200


def test_v1_pre_api_qualification_status_success():
    resp = client.post("/v1/pre-api/qualification")
    assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# /v1/industrial/test
# ---------------------------------------------------------------------------


def test_v1_industrial_test_200():
    resp = client.post("/v1/industrial/test", json={"profile": "quick"})
    assert resp.status_code == 200


def test_v1_industrial_test_status_success():
    resp = client.post("/v1/industrial/test", json={"profile": "quick"})
    assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# /v1/reasoning/evaluate
# ---------------------------------------------------------------------------


def test_v1_reasoning_evaluate_200():
    resp = client.post("/v1/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_v1_reasoning_evaluate_status_success():
    resp = client.post("/v1/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# Old (unversioned) routes still work
# ---------------------------------------------------------------------------


def test_old_health_still_works():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_old_classify_still_works():
    resp = client.post("/classify", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_old_quality_lock_still_works():
    resp = client.post("/curriculum/quality-lock")
    assert resp.status_code == 200


def test_old_pre_api_qualification_still_works():
    resp = client.post("/pre-api/qualification")
    assert resp.status_code == 200


def test_old_reasoning_still_works():
    resp = client.post("/reasoning/evaluate", json={"text": _ARABIC_TEXT})
    assert resp.status_code == 200


def test_old_version_still_works():
    resp = client.get("/version")
    assert resp.status_code == 200


def test_old_industrial_still_works():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    assert resp.status_code == 200
