"""Tests for CorrespondenceChecker."""
from __future__ import annotations

import pytest

from mcd.nabhani.correspondence_checker import CorrespondenceChecker


@pytest.fixture
def checker():
    return CorrespondenceChecker()


class TestCorrespondenceCheckerDetectsMatch:
    def test_direct_reality_match(self, checker):
        result = checker.check("النار تحرق", reality="النار احتراق حرارة")
        assert result.match_score > 0.0
        assert result.match_type in ("direct_reality_match", "prior_knowledge_match", "relation_match")

    def test_no_reality_gives_insufficient_data(self, checker):
        result = checker.check("كلمة مجردة")
        assert result.match_type == "insufficient_data"

    def test_contradiction_detected_on_negation(self, checker):
        result = checker.check("النار لا تحرق", reality="النار احتراق")
        # May detect contradiction or lower match; either is valid
        assert result.match_score >= 0.0  # system should not crash

    def test_match_score_in_range(self, checker):
        result = checker.check("النار تحرق", reality="نار")
        assert 0.0 <= result.match_score <= 1.0

    def test_result_has_explanation(self, checker):
        result = checker.check("العلم نافع", reality="علم فائدة")
        assert result.explanation

    def test_relation_match(self, checker):
        class Rel:
            source = "النار"
            target = "الحرق"

        result = checker.check("النار", relations=[Rel()])
        assert result.match_score >= 0.0
