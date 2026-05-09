"""Tests for PromptFrame data models."""
import pytest

from mcd.classification.prompt_frame import ClassificationScore, PromptConcept, PromptFrame


def test_classification_score_valid():
    cs = ClassificationScore(label="epistemic", score=0.75, reason="test")
    assert cs.label == "epistemic"
    assert cs.score == 0.75


def test_classification_score_boundary():
    ClassificationScore(label="x", score=0.0)
    ClassificationScore(label="x", score=1.0)


def test_classification_score_invalid_score():
    with pytest.raises(ValueError):
        ClassificationScore(label="x", score=1.1)
    with pytest.raises(ValueError):
        ClassificationScore(label="x", score=-0.01)


def test_classification_score_empty_label():
    with pytest.raises(ValueError):
        ClassificationScore(label="", score=0.5)


def test_prompt_concept_basic():
    pc = PromptConcept(surface="نار", normalized="نار")
    assert pc.surface == "نار"
    assert pc.root_domain == {}


def test_prompt_concept_with_scores():
    pc = PromptConcept(
        surface="نار",
        normalized="نار",
        root_domain={"universe": 0.9},
        concept_type={"thing": 0.85},
    )
    assert pc.root_domain["universe"] == 0.9
    assert pc.concept_type["thing"] == 0.85


def test_prompt_concept_to_dict():
    pc = PromptConcept(surface="نار", normalized="نار", root_domain={"universe": 0.9})
    d = pc.to_dict()
    assert d["surface"] == "نار"
    assert d["root_domain"]["universe"] == 0.9
    assert "concept_type" in d


def test_prompt_frame_basic():
    frame = PromptFrame(
        raw_text="النار تحرق",
        normalized_text="النار تحرق",
        intent="general",
        concepts=[],
        root_domain={"universe": 0.9},
        concept_types={"thing": 0.8},
        knowledge_categories={"science": 0.7},
        judgment_types={"epistemic": 0.6},
        evidence_needs={"sensory": 0.8},
        certainty_policy="strong_knowledge",
        certainty_reason="test",
        routing_engine="nabhani_decoder",
        sub_engines=["evidence_gate"],
    )
    assert frame.raw_text == "النار تحرق"
    assert frame.certainty_policy == "strong_knowledge"


def test_prompt_frame_to_dict():
    frame = PromptFrame(
        raw_text="test",
        normalized_text="test",
        intent="general",
        concepts=[],
        root_domain={},
        concept_types={},
        knowledge_categories={},
        judgment_types={"epistemic": 0.5},
        evidence_needs={},
        certainty_policy="hypothesis",
        certainty_reason="reason",
        routing_engine="mcd",
        sub_engines=[],
        warnings=["warn1"],
    )
    d = frame.to_dict()
    assert d["raw_text"] == "test"
    assert d["judgment_types"]["epistemic"] == 0.5
    assert "warn1" in d["warnings"]


def test_prompt_frame_to_dict_json_serializable():
    import json
    frame = PromptFrame(
        raw_text="x",
        normalized_text="x",
        intent="general",
        concepts=[],
        root_domain={"universe": 0.8},
        concept_types={},
        knowledge_categories={},
        judgment_types={},
        evidence_needs={},
        certainty_policy="hypothesis",
        certainty_reason="r",
        routing_engine="mcd",
        sub_engines=[],
    )
    # Should not raise
    json.dumps(frame.to_dict())
