"""Test: POST /industrial/test runs industrial test profile."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


def test_industrial_test_status_200():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    assert resp.status_code == 200


def test_industrial_test_has_request_id():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    data = resp.json()
    assert "request_id" in data


def test_industrial_test_has_execution_time_ms():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    data = resp.json()
    assert "execution_time_ms" in data
    assert isinstance(data["execution_time_ms"], float)


def test_industrial_test_status_ok():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    assert resp.json()["status"] == "success"


def test_industrial_test_data_has_summary():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    data = resp.json()["data"]
    assert "summary" in data


def test_industrial_test_data_has_results():
    resp = client.post("/industrial/test", json={"profile": "quick"})
    data = resp.json()["data"]
    assert "results" in data
    assert isinstance(data["results"], list)


def test_industrial_test_unsupported_profile():
    resp = client.post("/industrial/test", json={"profile": "nonexistent_profile"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error_code"] == "UNSUPPORTED_PROFILE"


def test_industrial_test_default_profile():
    """Default profile (quick) should work without specifying profile."""
    resp = client.post("/industrial/test", json={})
    assert resp.status_code == 200
