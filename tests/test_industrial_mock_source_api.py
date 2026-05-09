"""Tests for mock_source_api.py — all 10 scenarios."""
from __future__ import annotations

import pytest
from mcd.industrial.api_contract import SourceQuery
from mcd.industrial.mock_source_api import MockSourceAPI


def _query(qid: str = "test-001") -> SourceQuery:
    return SourceQuery(query_id=qid, text="اختبار")


def test_ok_with_relevant_docs_returns_documents():
    api = MockSourceAPI(scenario="ok_with_relevant_docs")
    resp = api.search(_query())
    assert resp.status == "ok"
    assert len(resp.documents) >= 2
    for doc in resp.documents:
        assert doc.content


def test_ok_with_irrelevant_docs_returns_ok():
    api = MockSourceAPI(scenario="ok_with_irrelevant_docs")
    resp = api.search(_query())
    assert resp.status == "ok"
    assert len(resp.documents) >= 1


def test_empty_scenario():
    api = MockSourceAPI(scenario="empty")
    resp = api.search(_query())
    assert resp.status == "empty"
    assert resp.documents == []


def test_timeout_scenario():
    api = MockSourceAPI(scenario="timeout")
    resp = api.search(_query())
    assert resp.status == "timeout"
    assert resp.latency_ms == 9999


def test_error_scenario():
    api = MockSourceAPI(scenario="error")
    resp = api.search(_query())
    assert resp.status == "error"
    assert resp.error_message is not None


def test_conflicting_docs_scenario():
    api = MockSourceAPI(scenario="conflicting_docs")
    resp = api.search(_query())
    assert resp.status == "ok"
    assert len(resp.documents) == 2
    assert any("conflict" in w for w in resp.warnings)


def test_stale_docs_scenario():
    api = MockSourceAPI(scenario="stale_docs")
    resp = api.search(_query())
    assert resp.status == "ok"
    assert all(doc.freshness == "stale" for doc in resp.documents)


def test_low_authority_docs_scenario():
    api = MockSourceAPI(scenario="low_authority_docs")
    resp = api.search(_query())
    assert resp.status == "ok"
    assert all(doc.authority_level == "low" for doc in resp.documents)


def test_injection_contaminated_doc_contains_phrase():
    api = MockSourceAPI(scenario="injection_contaminated_doc")
    resp = api.search(_query())
    assert resp.status == "ok"
    contents = " ".join(d.content for d in resp.documents)
    assert "تجاهل تعليمات" in contents


def test_missing_source_scenario():
    api = MockSourceAPI(scenario="missing_source")
    resp = api.search(_query())
    assert resp.status == "empty"
    assert "requested_source_not_found" in resp.warnings


def test_determinism_same_result_twice():
    api = MockSourceAPI(scenario="ok_with_relevant_docs")
    q = _query("det-001")
    r1 = api.search(q)
    r2 = api.search(q)
    assert r1.status == r2.status
    assert len(r1.documents) == len(r2.documents)
    assert r1.documents[0].source_id == r2.documents[0].source_id


def test_query_id_propagated():
    api = MockSourceAPI(scenario="empty")
    resp = api.search(_query("my-qid"))
    assert resp.query_id == "my-qid"
