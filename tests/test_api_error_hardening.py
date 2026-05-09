"""Test: Error handling hardening.

Phase 6.1 acceptance criteria:
- Empty text returns 4xx JSON error (not 200)
- Missing text returns 422 JSON error
- Non-string text returns 422 JSON error
- Unsupported profile returns JSON error
- Invalid JSON returns 422 JSON error
- Engine exception returns JSON error (no stack trace)
- All errors return structured JSON (not stack traces)

These tests MUST FAIL if:
- error returns a stack trace
- error returns non-JSON
- error returns 200 with raw exception text
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


# ---------------------------------------------------------------------------
# Empty text
# ---------------------------------------------------------------------------


def test_empty_text_returns_400_or_422():
    """Blank text must return 4xx, not 200."""
    resp = client.post("/v1/classify", json={"text": "   "})
    assert resp.status_code in (400, 422)


def test_empty_text_returns_json_error():
    resp = client.post("/v1/classify", json={"text": "   "})
    data = json.loads(resp.text)
    assert isinstance(data, dict)
    assert "error_code" in data or "request_id" in data


def test_empty_text_no_stack_trace():
    resp = client.post("/v1/classify", json={"text": "   "})
    assert "Traceback" not in resp.text
    assert "traceback" not in resp.text


def test_empty_reasoning_returns_422():
    resp = client.post("/v1/reasoning/evaluate", json={"text": "  "})
    assert resp.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Missing text
# ---------------------------------------------------------------------------


def test_missing_text_returns_422_or_400():
    resp = client.post("/v1/classify", json={})
    assert resp.status_code in (400, 422)


def test_missing_text_has_error_code():
    resp = client.post("/v1/classify", json={})
    data = resp.json()
    assert "error_code" in data


def test_missing_text_has_request_id():
    resp = client.post("/v1/classify", json={})
    data = resp.json()
    assert "request_id" in data


def test_missing_reasoning_text_returns_422():
    resp = client.post("/v1/reasoning/evaluate", json={})
    assert resp.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Invalid JSON
# ---------------------------------------------------------------------------


def test_invalid_json_returns_422():
    resp = client.post(
        "/v1/classify",
        content=b"not-valid-json",
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 422


def test_invalid_json_has_error_code():
    resp = client.post(
        "/v1/classify",
        content=b"not-valid-json",
        headers={"content-type": "application/json"},
    )
    data = resp.json()
    assert "error_code" in data


# ---------------------------------------------------------------------------
# Unsupported profile
# ---------------------------------------------------------------------------


def test_unsupported_profile_returns_json_error():
    resp = client.post("/v1/industrial/test", json={"profile": "nonexistent_profile_xyz"})
    assert resp.status_code == 400
    data = resp.json()
    assert "error_code" in data
    assert data["error_code"] == "UNSUPPORTED_PROFILE"


def test_unsupported_curriculum_profile_returns_json_error():
    resp = client.post("/v1/curriculum/evaluate", json={"profile": "bad_profile"})
    assert resp.status_code == 400
    data = resp.json()
    assert "error_code" in data


def test_unsupported_profile_no_traceback():
    resp = client.post("/v1/industrial/test", json={"profile": "nonexistent_xyz"})
    assert "Traceback" not in resp.text
    assert "traceback" not in resp.text


# ---------------------------------------------------------------------------
# Engine exception simulated
# ---------------------------------------------------------------------------


def test_engine_exception_returns_json_error():
    """When the engine raises an unexpected exception, must return structured JSON error."""
    with patch(
        "mcd.classification.fractal_prompt_classifier.FractalPromptClassifier.classify",
        side_effect=RuntimeError("simulated engine failure"),
    ):
        resp = client.post("/v1/classify", json={"text": "اختبار"})
        assert resp.status_code in (500, 503)
        data = resp.json()
        assert isinstance(data, dict)


def test_engine_exception_no_stack_trace():
    """Engine exception must not leak stack trace."""
    with patch(
        "mcd.classification.fractal_prompt_classifier.FractalPromptClassifier.classify",
        side_effect=RuntimeError("simulated engine failure"),
    ):
        resp = client.post("/v1/classify", json={"text": "اختبار"})
        assert "Traceback" not in resp.text
        assert "RuntimeError" not in resp.text


def test_engine_exception_has_request_id():
    with patch(
        "mcd.classification.fractal_prompt_classifier.FractalPromptClassifier.classify",
        side_effect=RuntimeError("simulated engine failure"),
    ):
        resp = client.post("/v1/classify", json={"text": "اختبار"})
        data = resp.json()
        assert "request_id" in data


# ---------------------------------------------------------------------------
# No stack trace leaked in any error
# ---------------------------------------------------------------------------


def test_no_stack_trace_leaked_on_blank():
    for endpoint, body in [
        ("/v1/classify", {"text": "   "}),
        ("/v1/reasoning/evaluate", {"text": "   "}),
    ]:
        resp = client.post(endpoint, json=body)
        assert "Traceback" not in resp.text, f"{endpoint} leaked traceback"
        assert "File \"" not in resp.text, f"{endpoint} leaked file path"


def test_no_stack_trace_on_404():
    resp = client.get("/v1/nonexistent-route-xyz")
    assert resp.status_code == 404
    assert "Traceback" not in resp.text


# ---------------------------------------------------------------------------
# All errors are JSON-parseable
# ---------------------------------------------------------------------------


def test_all_errors_are_valid_json():
    bad_requests = [
        ("/v1/classify", {"text": "   "}),
        ("/v1/classify", {}),
        ("/v1/industrial/test", {"profile": "bad_profile"}),
        ("/v1/reasoning/evaluate", {}),
    ]
    for endpoint, body in bad_requests:
        resp = client.post(endpoint, json=body)
        assert resp.status_code >= 400
        data = json.loads(resp.text)
        assert isinstance(data, dict)
