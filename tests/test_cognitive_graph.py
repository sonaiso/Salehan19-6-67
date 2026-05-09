"""Tests for CognitiveGraph."""
from __future__ import annotations

import pytest
from mcd.curriculum.cognitive_graph import CognitiveGraph, EVIDENCE_STATUSES, CERTAINTY_POLICIES
from mcd.curriculum.cognitive_node import CognitiveNode
from mcd.curriculum.cognitive_edge import CognitiveEdge


def _node(node_id: str, node_type: str = "thing") -> CognitiveNode:
    return CognitiveNode(node_id=node_id, surface=node_id, normalized=node_id, node_type=node_type)


def _edge(edge_id: str, source: str, target: str, relation: str = "entails") -> CognitiveEdge:
    return CognitiveEdge(edge_id=edge_id, source=source, relation=relation, target=target)


def _graph(graph_id: str = "g1", nodes=None, edges=None) -> CognitiveGraph:
    return CognitiveGraph(
        graph_id=graph_id,
        nodes=nodes or [],
        edges=edges or [],
        evidence_status="sufficient",
        certainty_policy="certain_knowledge",
    )


def test_graph_creation():
    g = _graph()
    assert g.graph_id == "g1"
    assert g.nodes == []
    assert g.edges == []


def test_graph_with_nodes():
    nodes = [_node("n1"), _node("n2", "action")]
    g = _graph(nodes=nodes)
    assert len(g.nodes) == 2


def test_graph_node_ids():
    nodes = [_node("n1"), _node("n2")]
    g = _graph(nodes=nodes)
    assert g.node_ids() == {"n1", "n2"}


def test_graph_invalid_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        CognitiveGraph(graph_id="g", evidence_status="unknown", certainty_policy="certain_knowledge")


def test_graph_invalid_certainty_policy():
    with pytest.raises(ValueError, match="certainty_policy"):
        CognitiveGraph(graph_id="g", evidence_status="sufficient", certainty_policy="made_up")


def test_graph_to_dict():
    g = _graph()
    d = g.to_dict()
    assert "graph_id" in d
    assert "nodes" in d
    assert "edges" in d
    assert "certainty_policy" in d


def test_graph_from_dict():
    g = _graph("test_g")
    d = g.to_dict()
    g2 = CognitiveGraph.from_dict(d)
    assert g2.graph_id == "test_g"
    assert g2.certainty_policy == g.certainty_policy


def test_graph_is_json_serializable():
    g = _graph()
    assert g.is_json_serializable()


def test_graph_with_edges():
    n1, n2 = _node("n1"), _node("n2", "cause")
    e = _edge("e1", "n1", "n2")
    g = _graph(nodes=[n1, n2], edges=[e])
    assert len(g.edges) == 1


def test_valid_evidence_statuses():
    for status in EVIDENCE_STATUSES:
        g = CognitiveGraph(graph_id="g", evidence_status=status, certainty_policy="certain_knowledge")
        assert g.evidence_status == status


def test_valid_certainty_policies():
    for policy in CERTAINTY_POLICIES:
        g = CognitiveGraph(graph_id="g", evidence_status="sufficient", certainty_policy=policy)
        assert g.certainty_policy == policy
