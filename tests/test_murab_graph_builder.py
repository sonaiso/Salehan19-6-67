"""Tests for MurabGraphBuilder."""
import pytest
from mcd.murab.murab_graph_builder import MurabGraphBuilder, MurabGraph, MurabEdge, MurabUnitNode
from mcd.murab.murab_schema import MurabUnit


def _make_units():
    return [
        MurabUnit(
            unit_id="u1", surface="جاءَ", normalized="جاء",
            token_id="t1", word_type="verb",
            irab_case="nominative", irab_marker="damma",
            marker_visibility="apparent", governing_factor_id=None,
            syntactic_role="verb", semantic_role="unknown",
        ),
        MurabUnit(
            unit_id="u2", surface="الطالبُ", normalized="طالب",
            token_id="t2", word_type="noun",
            irab_case="nominative", irab_marker="damma",
            marker_visibility="apparent", governing_factor_id=None,
            syntactic_role="agent", semantic_role="agent",
        ),
    ]


def test_graph_builder_returns_graph():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    assert isinstance(graph, MurabGraph)


def test_graph_has_nodes():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    assert len(graph.nodes) > 0


def test_graph_has_edges():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    assert len(graph.edges) > 0


def test_murab_unit_nodes_present():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    unit_ids = [n.to_dict().get("unit_id", "") for n in graph.nodes if hasattr(n, "to_dict") and n.to_dict().get("node_type") == "MurabUnitNode"]
    assert "u1" in unit_ids
    assert "u2" in unit_ids


def test_case_nodes_present():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    case_nodes = [n for n in graph.nodes if hasattr(n, "to_dict") and n.to_dict().get("node_type") == "IrabCaseNode"]
    assert len(case_nodes) > 0


def test_graph_to_dict():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units, "جاء الطالب")
    d = graph.to_dict()
    assert "nodes" in d
    assert "edges" in d


def test_governing_factor_node():
    builder = MurabGraphBuilder()
    unit = MurabUnit(
        unit_id="u3", surface="المدرسةِ", normalized="مدرسة",
        token_id="t3", word_type="noun",
        irab_case="genitive", irab_marker="kasra",
        marker_visibility="apparent", governing_factor_id="prep_fi",
        syntactic_role="object_of_preposition", semantic_role="unknown",
    )
    graph = builder.build([unit], "المدرسةِ")
    gf_nodes = [n for n in graph.nodes if hasattr(n, "to_dict") and n.to_dict().get("node_type") == "GoverningFactorNode"]
    assert len(gf_nodes) > 0
