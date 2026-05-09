"""Tests for EpistemicAxiom registry."""
from __future__ import annotations

import pytest

from mcd.nabhani.epistemic_axioms import AXIOM_REGISTRY, EpistemicAxiom

EXPECTED_AXIOM_NAMES = [
    "no_knowledge_without_reality",
    "no_thought_without_sense_or_source",
    "no_understanding_without_prior",
    "prior_is_not_opinion",
    "thought_from_linking",
    "concept_not_just_meaning",
    "thought_validity_by_correspondence",
    "no_knowledge_without_evidence",
    "certainty_is_degree",
    "certainty_becomes_measure",
    "measure_governs_cognition",
    "reason_governs_perception",
    "pre_revelation_epistemic",
]


def test_registry_has_13_axioms():
    assert len(AXIOM_REGISTRY) == 13


def test_all_expected_axioms_present():
    for name in EXPECTED_AXIOM_NAMES:
        assert name in AXIOM_REGISTRY, f"Missing axiom: {name}"


def test_each_axiom_has_required_fields():
    for name, axiom in AXIOM_REGISTRY.items():
        assert isinstance(axiom, EpistemicAxiom), f"{name} is not EpistemicAxiom"
        assert axiom.axiom_id, f"{name} missing axiom_id"
        assert axiom.arabic_name, f"{name} missing arabic_name"
        assert axiom.statement, f"{name} missing statement"
        assert axiom.domain, f"{name} missing domain"
        assert axiom.gate_name, f"{name} missing gate_name"
        assert axiom.certainty_policy, f"{name} missing certainty_policy"


def test_axiom_ids_are_unique():
    ids = [a.axiom_id for a in AXIOM_REGISTRY.values()]
    assert len(ids) == len(set(ids)), "Duplicate axiom IDs found"


def test_arabic_names_present():
    for name, axiom in AXIOM_REGISTRY.items():
        assert "ا" in axiom.arabic_name or "ل" in axiom.arabic_name, (
            f"{name} arabic_name does not look Arabic"
        )


def test_no_knowledge_without_reality_requires_target_reality():
    axiom = AXIOM_REGISTRY["no_knowledge_without_reality"]
    assert "target_reality" in axiom.required_inputs


def test_no_knowledge_without_evidence_requires_evidence():
    axiom = AXIOM_REGISTRY["no_knowledge_without_evidence"]
    assert "evidence" in axiom.required_inputs


def test_certainty_becomes_measure_threshold_mentioned():
    axiom = AXIOM_REGISTRY["certainty_becomes_measure"]
    assert "0.85" in axiom.statement or "مقياس" in axiom.arabic_name


def test_pre_revelation_epistemic_allows_epistemic():
    axiom = AXIOM_REGISTRY["pre_revelation_epistemic"]
    assert "epistemic" in axiom.certainty_policy


def test_reason_governs_perception_domain():
    axiom = AXIOM_REGISTRY["reason_governs_perception"]
    assert "meta" in axiom.domain or "epistemology" in axiom.domain
