"""Test: POST /pre-api/qualification returns qualification status."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


def test_pre_api_qualification_status_200():
    resp = client.post("/pre-api/qualification")
    assert resp.status_code == 200


def test_pre_api_qualification_has_request_id():
    resp = client.post("/pre-api/qualification")
    data = resp.json()
    assert "request_id" in data
    assert len(data["request_id"]) > 0


def test_pre_api_qualification_has_execution_time_ms():
    resp = client.post("/pre-api/qualification")
    data = resp.json()
    assert "execution_time_ms" in data
    assert isinstance(data["execution_time_ms"], float)


def test_pre_api_qualification_status_ok():
    resp = client.post("/pre-api/qualification")
    assert resp.json()["status"] == "success"


def test_pre_api_qualification_data_has_status():
    resp = client.post("/pre-api/qualification")
    data = resp.json()["data"]
    assert "status" in data
    assert data["status"] in ("qualified_for_api_phase", "blocked_before_api")


def test_pre_api_qualification_data_has_dimensions():
    resp = client.post("/pre-api/qualification")
    data = resp.json()["data"]
    assert "dimensions" in data
    assert isinstance(data["dimensions"], list)


def test_pre_api_qualification_data_has_api_score():
    resp = client.post("/pre-api/qualification")
    data = resp.json()["data"]
    assert "api_score" in data


def test_pre_api_qualification_warnings_is_list():
    resp = client.post("/pre-api/qualification")
    assert isinstance(resp.json()["warnings"], list)
