"""Tests for MabniGraphBuilder."""
from __future__ import annotations

import pytest
from mcd.mabni.mabni_graph_builder import MabniGraph, MabniGraphBuilder


@pytest.fixture
def builder():
    return MabniGraphBuilder()


def test_build_returns_graph(builder):
    unfold_result = {
        "text": "ما جاء زيد",
        "ma_result": {"operator_id": "MA_NEG", "surface": "ما", "mabni_type": "negation"},
    }
    graph = builder.build(unfold_result)
    assert isinstance(graph, MabniGraph)
    assert len(graph.nodes) > 0


def test_graph_has_root(builder):
    unfold_result = {"text": "إن جاء فأكرمه", "in_result": {"operator_id": "IN_COND", "surface": "إن"}}
    graph = builder.build(unfold_result)
    node_types = [n.node_type for n in graph.nodes]
    assert "utterance_root" in node_types


def test_graph_has_edges(builder):
    unfold_result = {
        "text": "ما جاء",
        "ma_result": {"operator_id": "MA_NEG", "surface": "ما"},
    }
    graph = builder.build(unfold_result)
    assert len(graph.edges) > 0


def test_to_dict(builder):
    unfold_result = {"text": "test", "ma_result": {"operator_id": "MA", "surface": "ما"}}
    graph = builder.build(unfold_result)
    d = graph.to_dict()
    assert "nodes" in d
    assert "edges" in d
    assert "graph_id" in d
