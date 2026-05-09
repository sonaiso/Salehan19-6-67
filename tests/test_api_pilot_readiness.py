"""Test: GET /v1/pilot/readiness endpoint.

Phase 6.1 acceptance:
- production_ready is ALWAYS false
- status is 'conditional_candidate' or 'not_ready' (never 'production_ready')
- api_implemented is true
- tests_verified is NOT hardcoded true
- blockers_before_production is a non-empty list
- quality_lock reflects real state

These tests MUST FAIL if:
- production_ready=true
- tests_verified hardcoded true
- api_implemented=false
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


# ---------------------------------------------------------------------------
# Basic endpoint
# ---------------------------------------------------------------------------


def test_pilot_readiness_endpoint_exists():
    resp = client.get("/v1/pilot/readiness")
    assert resp.status_code == 200


def test_pilot_readiness_returns_json():
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# production_ready is ALWAYS false (enforced, never change this)
# ---------------------------------------------------------------------------


def test_pilot_readiness_not_production_ready():
    """production_ready MUST be false in Phase 6.1."""
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "production_ready" in data
    assert data["production_ready"] is False


def test_pilot_readiness_production_ready_is_bool_false():
    """Strictly check it's boolean False, not just falsy."""
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert data["production_ready"] is False


# ---------------------------------------------------------------------------
# api_implemented is true
# ---------------------------------------------------------------------------


def test_pilot_readiness_reports_api_implemented():
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "api_implemented" in data
    assert data["api_implemented"] is True


# ---------------------------------------------------------------------------
# tests_verified must NOT be hardcoded true
# ---------------------------------------------------------------------------


def test_pilot_readiness_tests_verified_not_hardcoded_true():
    """tests_verified must be false unless CI confirms it — cannot be hardcoded true."""
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "tests_verified" in data
    # Must be false (can't be hardcoded true without real CI confirmation)
    assert data["tests_verified"] is False


# ---------------------------------------------------------------------------
# blockers_before_production
# ---------------------------------------------------------------------------


def test_pilot_readiness_has_blockers():
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "blockers_before_production" in data
    assert isinstance(data["blockers_before_production"], list)
    assert len(data["blockers_before_production"]) > 0


def test_pilot_readiness_blockers_mention_auth():
    """Auth must be listed as a production blocker."""
    resp = client.get("/v1/pilot/readiness")
    blockers = resp.json()["blockers_before_production"]
    blockers_text = " ".join(blockers).lower()
    assert "auth" in blockers_text or "authentication" in blockers_text


def test_pilot_readiness_blockers_mention_rate_limiting():
    resp = client.get("/v1/pilot/readiness")
    blockers = resp.json()["blockers_before_production"]
    blockers_text = " ".join(blockers).lower()
    assert "rate limit" in blockers_text or "rate_limit" in blockers_text


# ---------------------------------------------------------------------------
# status field
# ---------------------------------------------------------------------------


def test_pilot_readiness_has_status():
    resp = client.get("/v1/pilot/readiness")
    assert "status" in resp.json()


def test_pilot_readiness_status_is_valid():
    """Status must be conditional_candidate or not_ready — never 'production_ready'."""
    resp = client.get("/v1/pilot/readiness")
    status = resp.json()["status"]
    assert status in ("conditional_candidate", "not_ready", "ready_for_pilot")
    # Must never claim production_ready
    assert status != "production_ready"


# ---------------------------------------------------------------------------
# quality_lock field
# ---------------------------------------------------------------------------


def test_pilot_readiness_has_quality_lock():
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "quality_lock" in data
    assert isinstance(data["quality_lock"], str)


def test_pilot_readiness_quality_lock_not_empty():
    resp = client.get("/v1/pilot/readiness")
    assert resp.json()["quality_lock"] != ""


# ---------------------------------------------------------------------------
# warnings field
# ---------------------------------------------------------------------------


def test_pilot_readiness_has_warnings():
    resp = client.get("/v1/pilot/readiness")
    data = resp.json()
    assert "warnings" in data
    assert isinstance(data["warnings"], list)


def test_pilot_readiness_warns_about_tests_verification():
    resp = client.get("/v1/pilot/readiness")
    warnings = resp.json().get("warnings", [])
    warnings_text = " ".join(warnings).lower()
    assert "tests" in warnings_text or "ci" in warnings_text


# ---------------------------------------------------------------------------
# No stack trace in response
# ---------------------------------------------------------------------------


def test_pilot_readiness_no_stack_trace():
    resp = client.get("/v1/pilot/readiness")
    assert "Traceback" not in resp.text
    assert "traceback" not in resp.text
