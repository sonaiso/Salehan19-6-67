"""Tests for NodeTraceLink."""
import pytest
from mcd.traceability.node_trace import NodeTraceLink


def test_basic_node_link():
    nl = NodeTraceLink(
        node_id="N-001",
        token_ids=["T-000001-abc"],
        unicode_trace_ids=["U-000001-abc"],
        role_vector_contribution={"root_candidate": 0.8},
        domain_vector_contribution={"fiqh": 0.5},
        explanation="Test node",
    )
    assert nl.node_id == "N-001"
    assert nl.is_generated is False


def test_generated_node():
    nl = NodeTraceLink(
        node_id="N-002",
        token_ids=[],
        unicode_trace_ids=[],
        role_vector_contribution={},
        domain_vector_contribution={},
        explanation="Generated",
        metadata={"generated_node": True},
    )
    assert nl.is_generated is True


def test_to_dict():
    nl = NodeTraceLink(
        node_id="N-003",
        token_ids=["T-1"],
        unicode_trace_ids=["U-1"],
        role_vector_contribution={},
        domain_vector_contribution={},
        explanation="x",
    )
    d = nl.to_dict()
    assert "node_id" in d
    assert "token_ids" in d
    assert "explanation" in d
