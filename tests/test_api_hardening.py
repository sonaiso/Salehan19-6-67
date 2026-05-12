from __future__ import annotations

from fastapi.testclient import TestClient

from mcd.api.app import build_app


def test_staging_requires_api_key(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "staging")
    monkeypatch.setenv("MCD_API_KEY", "secret")
    client = TestClient(build_app())
    resp = client.post("/v1/classify", json={"text": "النار حارة"})
    assert resp.status_code == 401


def test_staging_accepts_valid_api_key(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "staging")
    monkeypatch.setenv("MCD_API_KEY", "secret")
    client = TestClient(build_app())
    resp = client.post("/v1/classify", json={"text": "النار حارة"}, headers={"x-api-key": "secret"})
    assert resp.status_code == 200
    assert "X-Replay-ID" in resp.headers


def test_production_requires_role(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "production")
    monkeypatch.setenv("MCD_API_KEY", "secret")
    client = TestClient(build_app())
    resp = client.post("/v1/classify", json={"text": "النار حارة"}, headers={"x-api-key": "secret"})
    assert resp.status_code == 403


def test_rate_limiting(monkeypatch):
    monkeypatch.setenv("MCD_API_PROFILE", "staging")
    monkeypatch.setenv("MCD_API_KEY", "secret-rate")
    monkeypatch.setenv("MCD_RATE_LIMIT_PER_MIN", "1")
    client = TestClient(build_app())
    h = {"x-api-key": "secret-rate"}
    first = client.post("/v1/classify", json={"text": "النار حارة"}, headers=h)
    second = client.post("/v1/classify", json={"text": "النار حارة"}, headers=h)
    assert first.status_code == 200
    assert second.status_code == 429
