"""Test: GET /version returns layers."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcd.api.app import build_app
from mcd.api.version import API_VERSION, LAYERS

client = TestClient(build_app())


def test_version_status_200():
    resp = client.get("/version")
    assert resp.status_code == 200


def test_version_has_version_field():
    resp = client.get("/version")
    assert resp.json()["version"] == API_VERSION


def test_version_has_layers():
    resp = client.get("/version")
    layers = resp.json()["layers"]
    assert isinstance(layers, list)
    assert len(layers) > 0


def test_version_layers_contain_expected():
    resp = client.get("/version")
    layers = resp.json()["layers"]
    for expected in ["MCD", "NERL", "FPCL", "EIRL", "Industrial", "Curriculum"]:
        assert expected in layers


def test_version_has_service():
    resp = client.get("/version")
    assert "service" in resp.json()


def test_version_request_id_header():
    resp = client.get("/version")
    assert "x-request-id" in resp.headers


def test_version_execution_time_header():
    resp = client.get("/version")
    assert "x-execution-time-ms" in resp.headers
