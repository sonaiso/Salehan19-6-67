"""Tests for DomainJudge."""
from __future__ import annotations

import pytest

from mcd.nabhani.domain_judge import DomainJudge


@pytest.fixture
def judge():
    return DomainJudge()


class TestDomainJudgeClassifiesEpistemicClaim:
    def test_harm_domain_is_epistemic(self, judge):
        result = judge.classify({"domain": "harm"})
        assert result.judgment_type == "epistemic"
        assert result.can_reason_without_revelation is True
        assert result.status == "proceed_epistemic"

    def test_utility_domain_is_epistemic(self, judge):
        result = judge.classify({"domain": "utility"})
        assert result.judgment_type == "epistemic"

    def test_causality_domain_is_epistemic(self, judge):
        result = judge.classify({"domain": "causality"})
        assert result.judgment_type == "epistemic"

    def test_existence_domain_is_epistemic(self, judge):
        result = judge.classify({"domain": "existence"})
        assert result.judgment_type == "epistemic"


class TestDomainJudgeBlocksShariClaimWithoutRevelation:
    def test_prohibition_domain_blocked_without_revelation(self, judge):
        result = judge.classify({"domain": "prohibition"})
        assert result.judgment_type == "normative_shari"
        assert result.can_reason_without_revelation is False
        assert result.status == "no_shari_ruling_available"

    def test_obligation_domain_blocked_without_revelation(self, judge):
        result = judge.classify({"domain": "obligation"})
        assert result.status == "no_shari_ruling_available"

    def test_normative_with_revelation_evidence_accepted(self, judge):
        result = judge.classify({
            "domain": "prohibition",
            "revelation_evidence": "قرآن كريم: وَلَا تَقْرَبُوا الزِّنَا",
        })
        assert result.status == "shari_judgment_with_evidence"


class TestDomainJudgeHarmVsHaram:
    def test_kidhb_darr_is_epistemic(self, judge):
        result = judge.classify_text("الكذب ضار")
        assert result.judgment_type == "epistemic"
        assert result.status == "proceed_epistemic"

    def test_kidhb_haram_is_normative(self, judge):
        result = judge.classify_text("الكذب حرام")
        assert result.judgment_type == "normative_shari"
        assert result.status == "no_shari_ruling_available"

    def test_is_harm_claim_darr(self, judge):
        assert judge.is_harm_claim("الكذب ضار") is True

    def test_is_harm_claim_naafi(self, judge):
        assert judge.is_harm_claim("العلم نافع") is True

    def test_is_prohibition_claim_haram(self, judge):
        assert judge.is_prohibition_claim("الكذب حرام") is True

    def test_is_prohibition_claim_wajib(self, judge):
        assert judge.is_prohibition_claim("الصلاة واجبة") is True

    def test_neutral_text_is_epistemic(self, judge):
        result = judge.classify_text("النار تحرق")
        assert result.judgment_type == "epistemic"
