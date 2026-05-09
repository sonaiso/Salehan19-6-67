"""Tests for RationalMethodJudge."""
from __future__ import annotations

import pytest

from mcd.nabhani.rational_method_judge import RationalMethodJudge


@pytest.fixture
def judge():
    return RationalMethodJudge()


FULL_CLAIM = {
    "text": "النار تحرق",
    "target_reality": "نار",
    "sense_source": "sensory",
    "prior_information": "النار مادة مشتعلة",
    "relation_chain": [{"source": "نار", "relation": "causes", "target": "حرق"}],
    "correspondence_test": True,
    "evidence": [{"source_type": "sensory", "strength": 0.90}],
    "certainty": 0.85,
}


class TestRationalMethodJudgeRejectsWithoutReality:
    def test_rejects_claim_without_reality(self, judge):
        claim = {"text": "شيء ما يحدث", "target_reality": None}
        result = judge.judge(claim)
        assert result.status == "rejected"
        assert result.accepted is False

    def test_rejects_missing_target_reality_key(self, judge):
        result = judge.judge({"text": "شيء"})
        assert result.status == "rejected"

    def test_rejected_claim_has_explanation(self, judge):
        result = judge.judge({"target_reality": ""})
        assert result.explanation
        assert "no_knowledge_without_reality" in result.violated_axioms


class TestRationalMethodJudgeSuspendsWithoutEvidence:
    def test_suspends_claim_without_evidence(self, judge):
        claim = {
            "text": "شيء ما",
            "target_reality": "شيء",
            "sense_source": "linguistic",
            "prior_information": "معلومة",
            "relation_chain": [{"r": "x"}],
            "correspondence_test": True,
            "evidence": [],
            "certainty": 0.70,
        }
        result = judge.judge(claim)
        assert result.status == "suspended"
        assert "no_knowledge_without_evidence" in result.violated_axioms

    def test_suspends_claim_with_empty_evidence_list(self, judge):
        claim = dict(FULL_CLAIM)
        claim["evidence"] = []
        result = judge.judge(claim)
        assert result.status == "suspended"


class TestRationalMethodJudgeAcceptsFullClaim:
    def test_accepts_full_claim(self, judge):
        result = judge.judge(FULL_CLAIM)
        assert result.accepted is True
        assert result.status == "accepted"
        assert result.missing_requirements == []

    def test_suspends_low_certainty_claim(self, judge):
        claim = dict(FULL_CLAIM)
        claim["certainty"] = 0.20
        result = judge.judge(claim)
        assert result.status == "suspended"
        assert result.accepted is False

    def test_certainty_hint_present(self, judge):
        result = judge.judge(FULL_CLAIM)
        assert result.certainty_hint in (
            "near_certainty", "strong_knowledge", "probable_knowledge",
            "hypothesis", "weak_or_unverified",
        )

    def test_missing_sense_source_causes_suspension(self, judge):
        claim = dict(FULL_CLAIM)
        claim["sense_source"] = None
        result = judge.judge(claim)
        assert result.status == "suspended"
        assert "no_thought_without_sense_or_source" in result.violated_axioms
