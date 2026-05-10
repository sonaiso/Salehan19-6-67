"""Tests for MurabGraphBuilder."""
import pytest
from mcd.murab.murab_graph_builder import MurabGraphBuilder, MurabGraph, MurabNode, MurabEdge
from mcd.murab.murab_schema import MurabUnit


def _make_units():
    return [
        MurabUnit(
            unit_id="u1", surface="جاءَ", normalized="جاء",
            token_id="t1", word_type="verb",
            irab_case="nominative", irab_marker="damma",
            marker_visibility="apparent", syntactic_role="verb",
        ),
        MurabUnit(
            unit_id="u2", surface="الطالبُ", normalized="طالب",
            token_id="t2", word_type="noun",
            irab_case="nominative", irab_marker="damma",
            marker_visibility="apparent", syntactic_role="agent",
        ),
    ]


def test_graph_builder_returns_graph():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    assert isinstance(graph, MurabGraph)


def test_graph_has_nodes():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    assert len(graph.nodes) > 0


def test_graph_has_edges():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    assert len(graph.edges) > 0


def test_murab_unit_nodes_present():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    unit_ids = [n.node_id for n in graph.nodes if hasattr(n, 'node_type') and n.node_type == "murab_unit"]
    assert "u1" in unit_ids
    assert "u2" in unit_ids


def test_case_nodes_present():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    case_nodes = [n for n in graph.nodes if hasattr(n, 'node_type') and n.node_type == "irab_case"]
    assert len(case_nodes) > 0


def test_graph_to_dict():
    builder = MurabGraphBuilder()
    units = _make_units()
    graph = builder.build(units)
    d = graph.to_dict()
    assert "nodes" in d
    assert "edges" in d


def test_governing_factor_node():
    builder = MurabGraphBuilder()
    unit = MurabUnit(
        unit_id="u3", surface="المدرسةِ", normalized="مدرسة",
        token_id="t3", word_type="noun",
        irab_case="genitive", irab_marker="kasra",
        marker_visibility="apparent", syntactic_role="object_of_preposition",
        governing_factor_id="prep_fi",
    )
    graph = builder.build([unit])
    gf_nodes = [n for n in graph.nodes if hasattr(n, 'node_type') and n.node_type == "governing_factor"]
    assert len(gf_nodes) > 0
