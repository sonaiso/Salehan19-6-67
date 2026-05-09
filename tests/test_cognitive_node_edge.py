"""Tests for CognitiveNode and CognitiveEdge."""
from __future__ import annotations

import pytest
from mcd.curriculum.cognitive_node import CognitiveNode, NODE_TYPES, GROUNDING_STATUSES
from mcd.curriculum.cognitive_edge import CognitiveEdge, VALID_RELATIONS


def _make_node(node_type: str = "thing", grounding: str = "ungrounded") -> CognitiveNode:
    return CognitiveNode(
        node_id="n1",
        surface="الطبيب",
        normalized="طبيب",
        node_type=node_type,
        grounding_status=grounding,
    )


def _make_edge(relation: str = "entails") -> CognitiveEdge:
    return CognitiveEdge(edge_id="e1", source="n1", relation=relation, target="n2")


class TestCognitiveNode:
    def test_basic_creation(self):
        n = _make_node()
        assert n.node_id == "n1"
        assert n.surface == "الطبيب"
        assert n.node_type == "thing"

    def test_invalid_node_type(self):
        with pytest.raises(ValueError, match="node_type"):
            CognitiveNode(node_id="x", surface="x", normalized="x", node_type="invalid_type")

    def test_invalid_grounding_status(self):
        with pytest.raises(ValueError, match="grounding_status"):
            CognitiveNode(node_id="x", surface="x", normalized="x", node_type="thing", grounding_status="bad")

    def test_invalid_certainty(self):
        with pytest.raises(ValueError, match="certainty"):
            CognitiveNode(node_id="x", surface="x", normalized="x", node_type="thing", certainty=1.5)

    def test_all_valid_node_types(self):
        for nt in NODE_TYPES:
            n = CognitiveNode(node_id="n", surface="s", normalized="n", node_type=nt)
            assert n.node_type == nt

    def test_all_valid_grounding_statuses(self):
        for gs in GROUNDING_STATUSES:
            n = _make_node(grounding=gs)
            assert n.grounding_status == gs

    def test_to_dict(self):
        n = _make_node()
        d = n.to_dict()
        assert d["node_id"] == "n1"
        assert d["node_type"] == "thing"
        assert "role_vector" in d
        assert "domain_vector" in d

    def test_from_dict(self):
        n = _make_node()
        d = n.to_dict()
        n2 = CognitiveNode.from_dict(d)
        assert n2.node_id == n.node_id
        assert n2.node_type == n.node_type

    def test_default_certainty(self):
        n = _make_node()
        assert n.certainty == 0.5

    def test_custom_certainty(self):
        n = CognitiveNode(node_id="n", surface="s", normalized="n", node_type="thing", certainty=0.9)
        assert n.certainty == 0.9


class TestCognitiveEdge:
    def test_basic_creation(self):
        e = _make_edge()
        assert e.edge_id == "e1"
        assert e.source == "n1"
        assert e.target == "n2"

    def test_invalid_relation(self):
        with pytest.raises(ValueError, match="relation"):
            CognitiveEdge(edge_id="e", source="a", relation="fake_relation", target="b")

    def test_invalid_certainty(self):
        with pytest.raises(ValueError, match="certainty"):
            CognitiveEdge(edge_id="e", source="a", relation="entails", target="b", certainty=2.0)

    def test_all_valid_relations(self):
        for rel in VALID_RELATIONS:
            e = CognitiveEdge(edge_id="e", source="a", relation=rel, target="b")
            assert e.relation == rel

    def test_to_dict(self):
        e = _make_edge()
        d = e.to_dict()
        assert d["edge_id"] == "e1"
        assert d["relation"] == "entails"

    def test_from_dict(self):
        e = _make_edge()
        d = e.to_dict()
        e2 = CognitiveEdge.from_dict(d)
        assert e2.edge_id == e.edge_id
        assert e2.relation == e.relation

    def test_qualifier_optional(self):
        e = _make_edge()
        assert e.qualifier is None

    def test_custom_qualifier(self):
        e = CognitiveEdge(edge_id="e", source="a", relation="entails", target="b", qualifier="conditional")
        assert e.qualifier == "conditional"
