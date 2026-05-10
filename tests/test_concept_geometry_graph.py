"""Tests for Phase 8.3 ConceptGeometryGraph."""
import pytest
from mcd.concept_geometry.concept_geometry_graph import (
    ConceptGeometryGraph, ConceptGeometryGraphBuilder, EDGE_TYPES, NODE_TYPES, CGNode, CGEdge
)
from mcd.concept_geometry.jamid_essence_ontology import JamidEssenceOntology
from mcd.concept_geometry.mushtaq_derivation_engine import MushtaqDerivationEngine


def test_edge_types_set():
    assert "has_essence" in EDGE_TYPES
    assert "derived_from_root" in EDGE_TYPES
    assert "projects_agency" in EDGE_TYPES
    assert "contributes_to_concept_center" in EDGE_TYPES


def test_node_types_set():
    assert "JamidEssenceNode" in NODE_TYPES
    assert "MushtaqNode" in NODE_TYPES
    assert "RootFamilyNode" in NODE_TYPES


def test_build_for_jamid_insan():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("إنسان")
    assert je is not None
    builder = ConceptGeometryGraphBuilder()
    g = builder.build_for_jamid("إنسان", je)
    assert len(g.nodes) > 0
    assert len(g.edges) > 0
    node_types = {n.node_type for n in g.nodes}
    assert "JamidEssenceNode" in node_types
    assert "ConceptCenterNode" in node_types
    edge_types = {e.edge_type for e in g.edges}
    assert "has_essence" in edge_types


def test_build_for_mushtaq_katib():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("كاتب")
    builder = ConceptGeometryGraphBuilder()
    g = builder.build_for_mushtaq("كاتب", mu)
    assert len(g.nodes) > 0
    assert len(g.edges) > 0
    edge_types = {e.edge_type for e in g.edges}
    assert "derived_from_root" in edge_types
    assert "projects_agency" in edge_types
    assert "contributes_to_concept_center" in edge_types


def test_all_edge_types_in_set():
    engine = MushtaqDerivationEngine()
    builder = ConceptGeometryGraphBuilder()
    for word in ["كاتب", "مكتوب", "مكتبة", "كتابي"]:
        mu = engine.analyze(word)
        g = builder.build_for_mushtaq(word, mu)
        for e in g.edges:
            assert e.edge_type in EDGE_TYPES, f"Unknown edge type: {e.edge_type} for {word}"


def test_graph_to_dict():
    ont = JamidEssenceOntology()
    je = ont.get_by_surface("حجر")
    builder = ConceptGeometryGraphBuilder()
    g = builder.build_for_jamid("حجر", je)
    d = g.to_dict()
    assert "nodes" in d
    assert "edges" in d
    assert d["word"] == "حجر"


def test_graph_to_markdown():
    engine = MushtaqDerivationEngine()
    mu = engine.analyze("زارع")
    builder = ConceptGeometryGraphBuilder()
    g = builder.build_for_mushtaq("زارع", mu)
    md = g.to_markdown()
    assert "زارع" in md
    assert "Nodes" in md
    assert "Edges" in md
