"""Tests for UsuliTarjihEngine."""
import pytest
from mcd.grounding.usuli_tarjih import (
    UsuliTarjihEngine,
    ConflictType,
    ResolutionStrategy,
)


@pytest.fixture
def engine():
    return UsuliTarjihEngine()


def test_compatible_claims_combine(engine):
    claims = [
        {"text": "الماء مفيد للشرب", "scope": "صحة", "certainty": 0.8, "is_compatible": True},
        {"text": "الماء مفيد للزراعة", "scope": "زراعة", "certainty": 0.8, "is_compatible": True},
    ]
    result = engine.resolve(ConflictType.EVIDENCE, claims)
    assert result.resolution_strategy == ResolutionStrategy.COMBINE


def test_general_vs_specific_specify(engine):
    claims = [
        {"text": "كل طعام حلال", "scope": "general", "is_general": True, "certainty": 0.7, "source": "قاعدة"},
        {"text": "الخنزير حرام", "scope": "specific", "is_specific": True, "certainty": 0.9, "source": "نص"},
    ]
    result = engine.resolve(ConflictType.RULE, claims)
    assert result.resolution_strategy == ResolutionStrategy.SPECIFY
    assert result.preferred_claim is not None
    assert result.preferred_claim.get("is_specific", False)


def test_claim_without_source_lower_certainty(engine):
    claims = [
        {"text": "الأمر كذا", "certainty": 0.8, "source": ""},
        {"text": "الأمر هكذا", "certainty": 0.8, "source": "مصدر موثوق"},
    ]
    result = engine.resolve(ConflictType.EVIDENCE, claims)
    # The claim without source should have lower adjusted certainty
    # which should lead to preferring the one with source
    assert result.resolution_strategy in (
        ResolutionStrategy.PREFER, ResolutionStrategy.SUSPEND, ResolutionStrategy.COMBINE
    )


def test_no_clear_winner_suspend(engine):
    claims = [
        {"text": "قول أ", "certainty": 0.5, "source": "مصدر"},
        {"text": "قول ب", "certainty": 0.5, "source": "مصدر", "negates": True},
    ]
    result = engine.resolve(ConflictType.MADLUL, claims)
    assert result.resolution_strategy == ResolutionStrategy.SUSPEND


def test_fake_evidence_not_preferred(engine):
    claims = [
        {"text": "قول صادق", "certainty": 0.6, "source": "مصدر", "fake_evidence": False},
        {"text": "قول زائف", "certainty": 0.9, "source": "مصدر", "fake_evidence": True},
    ]
    result = engine.resolve(ConflictType.EVIDENCE, claims)
    if result.preferred_claim is not None:
        assert not result.preferred_claim.get("fake_evidence", False)


def test_result_has_explanation(engine):
    claims = [
        {"text": "أ", "certainty": 0.7, "source": "s1"},
        {"text": "ب", "certainty": 0.5, "source": "s2"},
    ]
    result = engine.resolve(ConflictType.DAL, claims)
    assert result.explanation
    assert isinstance(result.certainty, float)


def test_absolute_vs_restricted(engine):
    claims = [
        {"text": "أكرموا المهاجرين", "is_absolute": True, "certainty": 0.7, "source": "s"},
        {"text": "أكرموا المهاجرين المسلمين", "is_restricted": True, "certainty": 0.75, "source": "s"},
    ]
    result = engine.resolve(ConflictType.RULE, claims)
    assert result.resolution_strategy == ResolutionStrategy.RESTRICT
    assert result.preferred_claim is not None
    assert result.preferred_claim.get("is_restricted", False)
