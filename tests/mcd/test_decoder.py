"""Tests for MinimalCognitiveDecoder."""
from __future__ import annotations

import pytest
from mcd.engines.decoder import MinimalCognitiveDecoder
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data


@pytest.fixture
def decoder():
    store = PriorKnowledgeStore()
    load_seed_data(store)
    return MinimalCognitiveDecoder(store=store)


def test_fire_burns_claim_has_high_certainty(decoder):
    result = decoder.decode("النار تحرق")
    assert result.claims
    assert result.claims[0]["certainty"]["score"] >= 0.75


def test_student_wrote_lesson_relations(decoder):
    result = decoder.decode("كتب الطالب الدرس")
    relation_types = [r["relation_type"] for r in result.relations]
    assert any(t in relation_types for t in ["agent_of", "patient_of", "has_root"])


def test_katib_word_analysis(decoder):
    result = decoder.decode("كاتب")
    node_features = [n.get("features", {}) for n in result.nodes]
    roots = [f.get("root", "") for f in node_features]
    assert any("كتب" in r or "ك" in r for r in roots if r)


def test_ilm_ambiguity(decoder):
    result = decoder.decode("علم")
    assert result.answer


def test_decoder_produces_output_fields(decoder):
    result = decoder.decode("النار تحرق")
    assert result.input == "النار تحرق"
    assert result.normalized
    assert isinstance(result.unicode_vectors, list)
    assert isinstance(result.role_vectors, list)
    assert isinstance(result.nodes, list)
    assert isinstance(result.relations, list)
    assert isinstance(result.claims, list)
    assert isinstance(result.certainty, dict)
    assert result.answer


def test_learner_mode_produces_actions():
    store = PriorKnowledgeStore()
    load_seed_data(store)
    decoder = MinimalCognitiveDecoder(store=store, allow_learning=True)
    result = decoder.decode("النار تحرق", mode="learner")
    assert isinstance(result.learning_actions, list)
