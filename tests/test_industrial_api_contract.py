"""Tests for api_contract.py."""
from __future__ import annotations

import pytest
from mcd.industrial.api_contract import SourceQuery, SourceDocument, SourceAPIResponse


def test_source_query_defaults():
    q = SourceQuery(query_id="q1", text="test")
    assert q.query_id == "q1"
    assert q.text == "test"
    assert q.requested_source_types == []
    assert q.domain_hint is None
    assert q.evidence_need == []
    assert q.max_results == 5
    assert q.timeout_ms == 3000


def test_source_document_defaults():
    doc = SourceDocument(source_id="d1", title="Title", content="Content")
    assert doc.source_id == "d1"
    assert doc.title == "Title"
    assert doc.content == "Content"
    assert doc.source_type == "document"
    assert doc.authority_level == "medium"
    assert doc.freshness == "acceptable"
    assert doc.retrieved_at == ""
    assert doc.metadata == {}


def test_source_api_response_defaults():
    r = SourceAPIResponse(query_id="q1")
    assert r.query_id == "q1"
    assert r.status == "ok"
    assert r.documents == []
    assert r.latency_ms == 0
    assert r.error_message is None
    assert r.warnings == []


def test_source_api_response_status_variants():
    for status in ("ok", "empty", "timeout", "error", "unauthorized"):
        r = SourceAPIResponse(query_id="q", status=status)
        assert r.status == status


def test_source_query_field_types():
    q = SourceQuery(query_id="q", text="t", max_results=10, timeout_ms=5000)
    assert isinstance(q.max_results, int)
    assert isinstance(q.timeout_ms, int)


def test_source_document_with_metadata():
    doc = SourceDocument(
        source_id="d2",
        title="T",
        content="C",
        metadata={"lang": "ar"},
    )
    assert doc.metadata["lang"] == "ar"


def test_source_api_response_with_docs():
    doc = SourceDocument(source_id="d1", title="T", content="C")
    r = SourceAPIResponse(query_id="q", documents=[doc])
    assert len(r.documents) == 1
    assert r.documents[0].source_id == "d1"
