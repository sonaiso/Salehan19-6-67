"""Tests for VectorComposer."""
import pytest

from mcd.classification.prompt_frame import PromptConcept
from mcd.classification.taxonomy import ConceptType, KnowledgeCategory, RootDomain
from mcd.classification.vector_composer import VectorComposer


def _concept(root_domain=None, concept_type=None, knowledge_category=None,
             judgment_hint=None, evidence_hint=None) -> PromptConcept:
    return PromptConcept(
        surface="x",
        normalized="x",
        root_domain=root_domain or {},
        concept_type=concept_type or {},
        knowledge_category=knowledge_category or {},
        judgment_hint=judgment_hint or {},
        evidence_hint=evidence_hint or {},
    )


def test_compose_empty_returns_empty_dicts():
    vc = VectorComposer()
    result = vc.compose([])
    assert result["root_domain"] == {}
    assert result["concept_types"] == {}


def test_compose_single_concept():
    vc = VectorComposer()
    concept = _concept(root_domain={"universe": 0.9})
    result = vc.compose([concept])
    assert result["root_domain"].get("universe", 0.0) > 0.0


def test_compose_scores_in_range():
    vc = VectorComposer()
    concepts = [
        _concept(root_domain={"universe": 0.9}, concept_type={"thing": 0.8}),
        _concept(root_domain={"human": 0.7}, concept_type={"system": 0.6}),
    ]
    result = vc.compose(concepts)
    for dim in result.values():
        for score in dim.values():
            assert 0.0 <= score <= 1.0


def test_compose_multi_label_preserved():
    """Secondary labels must not be eliminated."""
    vc = VectorComposer()
    concepts = [
        _concept(root_domain={"universe": 0.9, "human": 0.4}),
    ]
    result = vc.compose(concepts)
    assert "universe" in result["root_domain"]
    assert "human" in result["root_domain"]


def test_compose_intent_bias_applied():
    vc = VectorComposer()
    concepts = [_concept(judgment_hint={"epistemic": 0.5})]
    result_no_intent = vc.compose(concepts, intent="")
    result_build = vc.compose(concepts, intent="build")
    # build intent should boost technical
    tech_no_intent = result_no_intent["judgment_types"].get("technical", 0.0)
    tech_build = result_build["judgment_types"].get("technical", 0.0)
    assert tech_build >= tech_no_intent


def test_compose_no_winner_takes_all():
    """Even with one dominant concept, others should appear."""
    vc = VectorComposer()
    concepts = [
        _concept(root_domain={"universe": 0.9, "human": 0.5, "life": 0.6}),
    ]
    result = vc.compose(concepts)
    domains = result["root_domain"]
    assert len(domains) >= 2


def test_compose_many_concepts_all_dimensions():
    vc = VectorComposer()
    concepts = [
        _concept(
            root_domain={"human": 0.8, "life": 0.6},
            concept_type={"system": 0.7, "tool": 0.5},
            knowledge_category={"technology": 0.8, "culture": 0.6},
            judgment_hint={"technical": 0.7, "practical": 0.5},
            evidence_hint={"technical": 0.8},
        )
    ]
    result = vc.compose(concepts, intent="build")
    assert result["root_domain"]
    assert result["concept_types"]
    assert result["knowledge_categories"]
