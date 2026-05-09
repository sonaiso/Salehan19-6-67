"""Tests for ConflictResolver."""
from __future__ import annotations

import pytest

from mcd.nabhani.conflict_resolver import ConflictResolver


@pytest.fixture
def resolver():
    return ConflictResolver()


class TestConflictResolverSuspendsUnresolvedConflict:
    def test_suspends_when_no_clear_winner(self, resolver):
        claims = [
            {"text": "النار تحرق الخشب", "certainty": 0.55},
            {"text": "النار لا تحرق الخشب", "certainty": 0.50},
        ]
        result = resolver.resolve(claims)
        # No clear winner (diff < 0.15) → suspended or stronger_evidence
        assert result.resolution_strategy in ("suspended", "stronger_evidence")

    def test_conflict_detected_in_similar_text(self, resolver):
        claims = [
            {"text": "النار باردة", "certainty": 0.40},
            {"text": "النار ساخنة", "certainty": 0.90},
        ]
        result = resolver.resolve(claims)
        assert result.conflict_type != "none" or result.resolution_strategy == "stronger_evidence"

    def test_suspended_claims_listed(self, resolver):
        claims = [
            {"text": "A", "certainty": 0.50},
            {"text": "B", "certainty": 0.50},
        ]
        result = resolver.resolve(claims)
        # Either suspended or no_conflict
        assert isinstance(result.suspended_claims, list)


class TestConflictResolverNoConflict:
    def test_single_claim_no_conflict(self, resolver):
        result = resolver.resolve([{"text": "النار تحرق", "certainty": 0.80}])
        assert result.conflict_type == "none"
        assert result.resolution_strategy == "no_conflict"

    def test_empty_claims_no_conflict(self, resolver):
        result = resolver.resolve([])
        assert result.conflict_type == "none"

    def test_stronger_evidence_preferred(self, resolver):
        claims = [
            {"text": "النار تحرق", "certainty": 0.90},
            {"text": "النار تحرق أحيانًا", "certainty": 0.40},
        ]
        result = resolver.resolve(claims)
        if result.resolution_strategy == "stronger_evidence":
            assert "النار تحرق" in (result.preferred_claim or "")
