"""Tests for RelationBuilder."""
from __future__ import annotations

import pytest
from mcd.engines.relation_builder import RelationBuilder
from mcd.core.nodes import KnowledgeNode
from mcd.core.certainty import Certainty
from mcd.core.relations import RelationType


@pytest.fixture
def builder():
    return RelationBuilder()


def _make_word_node(word: str, root: str = "") -> KnowledgeNode:
    return KnowledgeNode(
        node_id=f"word_{word}",
        level="word",
        surface=word,
        features={"root": root} if root else {},
        certainty=Certainty.from_score(0.7),
    )


def test_relations_produced(builder):
    nodes = [_make_word_node(w) for w in ['كتب', 'الطالب', 'الدرس']]
    rels = builder.build_relations('كتب الطالب الدرس', nodes)
    assert len(rels) >= 1


def test_relation_has_agent_of(builder):
    nodes = [_make_word_node(w) for w in ['كتب', 'الطالب', 'الدرس']]
    rels = builder.build_relations('كتب الطالب الدرس', nodes)
    types = [r.relation_type for r in rels]
    assert RelationType.AGENT_OF.value in types


def test_relation_has_patient_of(builder):
    nodes = [_make_word_node(w) for w in ['كتب', 'الطالب', 'الدرس']]
    rels = builder.build_relations('كتب الطالب الدرس', nodes)
    types = [r.relation_type for r in rels]
    assert RelationType.PATIENT_OF.value in types


def test_relation_source_and_target_set(builder):
    nodes = [_make_word_node('كتب')]
    rels = builder.build_relations('كتب', nodes)
    for rel in rels:
        assert rel.source
        assert rel.target


def test_has_root_relation_when_root_present(builder):
    nodes = [_make_word_node('كاتب', root='كتب')]
    rels = builder.build_relations('كاتب', nodes)
    types = [r.relation_type for r in rels]
    assert RelationType.HAS_ROOT.value in types
