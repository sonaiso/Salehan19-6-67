"""Tests for FakeEvidenceDetector."""
from __future__ import annotations

import pytest

from mcd.nabhani.fake_evidence_detector import FakeEvidenceDetector


@pytest.fixture
def detector():
    return FakeEvidenceDetector()


CLEAN_CLAIM = {
    "text": "النار تحرق",
    "target_reality": "نار",
    "sense_source": "sensory",
    "prior_information": "النار مادة مشتعلة",
    "relation_chain": [{"source": "نار", "target": "حرق"}],
    "evidence": [{"source_type": "sensory", "strength": 0.90}],
    "certainty": 0.88,
}


class TestFakeEvidenceDetectorFlagsSurfaceSimilarity:
    def test_analogy_without_illah_flagged(self, detector):
        claim = {
            "text": "هذا يشبه ذاك",
            "target_reality": "شيء",
            "sense_source": None,
            "prior_information": None,
            "relation_chain": None,
            "evidence": [{"source_type": "analogy", "strength": 0.40}],
            "certainty": 0.40,
        }
        report = detector.detect(claim)
        assert report.has_fake_evidence is True
        assert report.severity in ("low", "medium", "high")

    def test_opinion_as_evidence_flagged(self, detector):
        claim = {
            "text": "هذا صحيح",
            "target_reality": "شيء",
            "sense_source": "opinion",
            "prior_information": None,
            "relation_chain": None,
            "evidence": [{"source_type": "opinion", "strength": 0.50}],
            "certainty": 0.50,
        }
        report = detector.detect(claim)
        assert "opinion_as_evidence" in report.detected_types

    def test_missing_source_flagged(self, detector):
        claim = {
            "text": "شيء ما",
            "target_reality": "شيء",
            "sense_source": None,
            "prior_information": "معلومة",
            "relation_chain": None,
            "evidence": [],
            "certainty": 0.30,
        }
        report = detector.detect(claim)
        assert "missing_source" in report.detected_types

    def test_severity_none_for_clean_claim(self, detector):
        report = detector.detect(CLEAN_CLAIM)
        # A clean claim may still get some flags (e.g., no chain in text-only mode)
        # but severity should not be high
        assert report.severity in ("none", "low")

    def test_severity_escalates_with_more_issues(self, detector):
        bad_claim = {
            "text": "كل شيء صحيح دائمًا",
            "target_reality": None,
            "sense_source": None,
            "prior_information": None,
            "relation_chain": None,
            "evidence": [],
            "certainty": 0.10,
        }
        report = detector.detect(bad_claim)
        assert report.severity in ("medium", "high")


class TestFakeEvidenceDetectorOkForSensoryEvidence:
    def test_sensory_evidence_not_flagged(self, detector):
        report = detector.detect(CLEAN_CLAIM)
        assert "analogy_without_illah" not in report.detected_types
        assert "circular_reasoning" not in report.detected_types

    def test_recommendation_for_clean(self, detector):
        report = detector.detect(CLEAN_CLAIM)
        assert report.recommendation

    def test_weak_evidence_flagged(self, detector):
        claim = {
            "text": "شيء",
            "target_reality": "شيء",
            "sense_source": "linguistic",
            "prior_information": "معلومة",
            "relation_chain": None,
            "evidence": [{"source_type": "sensory", "strength": 0.10}],
            "certainty": 0.20,
        }
        report = detector.detect(claim)
        assert report.has_fake_evidence is True
