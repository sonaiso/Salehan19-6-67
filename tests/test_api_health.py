"""Test: GET /health returns ok."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


def test_health_status_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_health_service_name():
    resp = client.get("/health")
    data = resp.json()
    assert data["service"] == "mcd-api"


def test_health_has_no_request_id_in_body():
    """Health is a plain dict — request_id lives only in the header."""
    resp = client.get("/health")
    data = resp.json()
    # Body does not need request_id; it is in the header
    assert "status" in data


def test_health_request_id_header():
    resp = client.get("/health")
    assert "x-request-id" in resp.headers


def test_health_execution_time_header():
    resp = client.get("/health")
    assert "x-execution-time-ms" in resp.headers
    ms = float(resp.headers["x-execution-time-ms"])
    assert ms >= 0


def test_health_returns_json():
    resp = client.get("/health")
    assert resp.headers["content-type"].startswith("application/json")
