"""Tests for EdgeTraceLink."""
import pytest
from mcd.traceability.edge_trace import EdgeTraceLink


def test_basic_edge():
    el = EdgeTraceLink(
        edge_id="E-001",
        source_node_id="N-1",
        target_node_id="N-2",
        relation="causes",
        supporting_unicode_trace_ids=[],
        supporting_token_ids=[],
        confidence=0.8,
        explanation="test",
    )
    assert el.edge_id == "E-001"
    assert el.is_inferred is False


def test_inferred_edge():
    el = EdgeTraceLink(
        edge_id="E-002",
        source_node_id="N-1",
        target_node_id="N-2",
        relation="implies",
        supporting_unicode_trace_ids=[],
        supporting_token_ids=[],
        confidence=0.5,
        explanation="inferred",
        metadata={"inferred": True},
    )
    assert el.is_inferred is True


def test_invalid_confidence():
    with pytest.raises(ValueError):
        EdgeTraceLink(
            edge_id="E-bad",
            source_node_id="N-1",
            target_node_id="N-2",
            relation="r",
            supporting_unicode_trace_ids=[],
            supporting_token_ids=[],
            confidence=1.5,
            explanation="bad",
        )


def test_to_dict():
    el = EdgeTraceLink(
        edge_id="E-003",
        source_node_id="A",
        target_node_id="B",
        relation="r",
        supporting_unicode_trace_ids=["U-1"],
        supporting_token_ids=["T-1"],
        confidence=0.9,
        explanation="ok",
    )
    d = el.to_dict()
    assert "edge_id" in d
    assert "confidence" in d
