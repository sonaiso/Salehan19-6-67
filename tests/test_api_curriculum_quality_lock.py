"""Test: POST /curriculum/quality-lock returns locked or blocked."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app

client = TestClient(build_app())


def test_quality_lock_status_200():
    resp = client.post("/curriculum/quality-lock")
    assert resp.status_code == 200


def test_quality_lock_has_request_id():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()
    assert "request_id" in data
    assert len(data["request_id"]) > 0


def test_quality_lock_has_execution_time_ms():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()
    assert "execution_time_ms" in data
    assert isinstance(data["execution_time_ms"], float)


def test_quality_lock_status_ok():
    resp = client.post("/curriculum/quality-lock")
    assert resp.json()["status"] == "ok"


def test_quality_lock_data_has_status():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()["data"]
    assert "status" in data
    assert data["status"] in ("locked", "blocked")


def test_quality_lock_data_has_contract_score():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()["data"]
    assert "contract_score" in data
    assert isinstance(data["contract_score"], float)


def test_quality_lock_data_has_is_locked():
    resp = client.post("/curriculum/quality-lock")
    data = resp.json()["data"]
    assert "is_locked" in data
    assert isinstance(data["is_locked"], bool)


def test_quality_lock_warnings_is_list():
    resp = client.post("/curriculum/quality-lock")
    assert isinstance(resp.json()["warnings"], list)
