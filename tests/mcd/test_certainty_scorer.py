"""Tests for CertaintyScorer."""
from __future__ import annotations

import pytest
from mcd.engines.certainty_scorer import CertaintyScorer
from mcd.core.evidence import Evidence, EvidenceType


@pytest.fixture
def scorer():
    return CertaintyScorer()


def test_all_zeros_gives_zero_score(scorer):
    result = scorer.score(
        reality_match=0.0,
        evidence_strength=0.0,
        semantic_fit=0.0,
        relation_validity=0.0,
        prior_relevance=0.0,
        context_fit=0.0,
    )
    assert result.score == 0.0


def test_high_inputs_gives_high_score(scorer):
    result = scorer.score(
        reality_match=1.0,
        evidence_strength=1.0,
        semantic_fit=1.0,
        relation_validity=1.0,
        prior_relevance=1.0,
        context_fit=1.0,
    )
    assert result.score >= 0.8


def test_penalties_reduce_score(scorer):
    base = scorer.score(reality_match=0.8, evidence_strength=0.8)
    penalized = scorer.score(reality_match=0.8, evidence_strength=0.8, ambiguity_penalty=1.0, contradiction_penalty=1.0)
    assert penalized.score <= base.score


def test_score_always_in_range(scorer):
    for ev_str in [0.0, 0.5, 1.0]:
        for penalty in [0.0, 0.5, 1.0]:
            result = scorer.score(
                evidence_strength=ev_str,
                ambiguity_penalty=penalty,
                contradiction_penalty=penalty,
            )
            assert 0.0 <= result.score <= 1.0


def test_score_maps_to_certainty_level(scorer):
    result = scorer.score(evidence_strength=0.9, reality_match=0.9, prior_relevance=0.9)
    assert result.level in ["weak_or_unverified", "hypothesis", "probable_knowledge", "strong_knowledge", "near_certainty"]


def test_score_from_evidence(scorer):
    evs = [
        Evidence("s1", "experimental", "obs", strength=0.9, reliability=0.9),
    ]
    result = scorer.score_from_evidence(evs)
    assert result.score > 0.0
