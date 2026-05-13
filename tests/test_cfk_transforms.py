"""Tests for Phase 8 CFK three transforms (Statistical, Arabic, Epistemic)."""
from __future__ import annotations

import pytest
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform, compute_epistemic_certainty
from mcd.cfk.cfk_schema import CoordinateType, JudgmentStatus


# ---------------------------------------------------------------------------
# StatisticalTransform tests
# ---------------------------------------------------------------------------

class TestStatisticalTransform:
    def setup_method(self):
        self.transform = StatisticalTransform()

    def _make_proposal(self, text="النار حارة", claimed=None, evidence=None):
        return {
            "proposal_id": "P-1",
            "gpt_output": text,
            "input_text": text,
            "proposal_type": "answer",
            "claimed_certainty": claimed,
            "claimed_evidence": evidence or [],
        }

    def test_basic_transform(self):
        proj = self.transform.transform(self._make_proposal())
        assert proj.coordinate_type == CoordinateType.STATISTICAL.value
        assert proj.projection_id.startswith("KP-S-")
        assert 0.0 <= proj.comparable_score <= 1.0

    def test_near_certainty_mapping(self):
        prop = self._make_proposal(claimed="near_certainty", evidence=["ref1"])
        proj = self.transform.transform(prop)
        assert proj.comparable_score >= 0.90  # near_certainty = 0.92

    def test_no_evidence_caps_score(self):
        prop = self._make_proposal(claimed="near_certainty", evidence=[])
        proj = self.transform.transform(prop)
        assert proj.comparable_score <= 0.60  # capped without evidence

    def test_missing_evidence_state(self):
        prop = self._make_proposal(evidence=[])
        proj = self.transform.transform(prop)
        assert proj.unit.E.evidence_state == "missing"

    def test_with_evidence_state(self):
        prop = self._make_proposal(evidence=["ref1"])
        proj = self.transform.transform(prop)
        assert proj.unit.E.evidence_state == "present"

    def test_coordinate_type_is_statistical(self):
        proj = self.transform.transform(self._make_proposal())
        assert proj.unit.C.coordinate_type == CoordinateType.STATISTICAL.value

    def test_epistemic_certainty_zero(self):
        """S(x) must NOT set epistemic certainty."""
        proj = self.transform.transform(self._make_proposal())
        assert proj.unit.C.epistemic_certainty == 0.0

    def test_hypothesis_default(self):
        """Default judgment from S(x) is hypothesis."""
        proj = self.transform.transform(self._make_proposal())
        assert proj.judgment == JudgmentStatus.HYPOTHESIS.value

    def test_unit_id_unique(self):
        p1 = self.transform.transform(self._make_proposal())
        p2 = self.transform.transform(self._make_proposal())
        assert p1.unit.unit_id != p2.unit.unit_id

    def test_transform_notes_non_empty(self):
        proj = self.transform.transform(self._make_proposal())
        assert len(proj.transform_notes) > 0

    def test_all_certainty_levels(self):
        levels = [
            "near_certainty", "strong_knowledge", "probable_knowledge",
            "hypothesis", "weak_or_unverified", "unknown",
        ]
        for level in levels:
            prop = self._make_proposal(claimed=level, evidence=["ref1"])
            proj = self.transform.transform(prop)
            assert 0.0 <= proj.comparable_score <= 1.0


# ---------------------------------------------------------------------------
# ArabicSemanticTransform tests
# ---------------------------------------------------------------------------

class TestArabicSemanticTransform:
    def setup_method(self):
        self.transform = ArabicSemanticTransform()

    def test_basic_transform(self):
        proj = self.transform.transform("زيد كاتب")
        assert proj.coordinate_type == CoordinateType.ARABIC.value
        assert proj.projection_id.startswith("KP-A-")

    def test_emphasis_detected(self):
        proj = self.transform.transform("إن زيداً كاتب")
        assert proj.unit.C.linguistic_force == "emphasis"

    def test_negation_detected(self):
        proj = self.transform.transform("ما جاء زيد")
        assert proj.unit.C.linguistic_force == "negation"

    def test_universal_detected(self):
        proj = self.transform.transform("كل الشركات تستخدم هذه التقنية")
        assert proj.unit.C.linguistic_force == "universal"
        assert proj.unit.O.logical_function == "universal_quantifier"

    def test_condition_detected(self):
        proj = self.transform.transform("إذا جاء زيد")
        assert proj.unit.C.linguistic_force == "condition"

    def test_neutral_for_plain_sentence(self):
        proj = self.transform.transform("زيد كاتب")
        assert proj.unit.C.linguistic_force == "neutral"

    def test_coordinate_type_arabic(self):
        proj = self.transform.transform("زيد كاتب")
        assert proj.unit.C.coordinate_type == CoordinateType.ARABIC.value

    def test_epistemic_certainty_zero(self):
        """A(x) must NOT set epistemic certainty."""
        proj = self.transform.transform("زيد كاتب")
        assert proj.unit.C.epistemic_certainty == 0.0

    def test_statistical_weight_zero(self):
        """A(x) must NOT set statistical weight."""
        proj = self.transform.transform("زيد كاتب")
        assert proj.unit.V.statistical_weight == 0.0

    def test_comparable_score_range(self):
        proj = self.transform.transform("إن زيداً لكاتب")
        assert 0.0 <= proj.comparable_score <= 1.0

    def test_transform_notes_contain_coordinate(self):
        proj = self.transform.transform("زيد كاتب")
        assert any("arabic" in note.lower() for note in proj.transform_notes)


# ---------------------------------------------------------------------------
# EpistemicTransform tests
# ---------------------------------------------------------------------------

class TestEpistemicTransform:
    def setup_method(self):
        self.transform = EpistemicTransform()

    def test_missing_evidence_low_certainty(self):
        proj = self.transform.transform("إن هذا لحق", statistical_confidence=0.9)
        assert proj.comparable_score <= 0.40  # missing → capped
        assert proj.unit.E.evidence_state == "missing"

    def test_partial_evidence(self):
        proj = self.transform.transform(
            "النار حارة",
            statistical_confidence=0.9,
            evidence_refs=["ref1"],
        )
        assert proj.unit.E.evidence_state == "partial"
        assert proj.comparable_score <= 0.65

    def test_full_evidence_raises_certainty(self):
        proj = self.transform.transform(
            "النار حارة",
            statistical_confidence=0.9,
            evidence_refs=["ref1", "ref2"],
        )
        assert proj.unit.E.evidence_state == "present"
        assert proj.comparable_score > 0.40

    def test_certificate_with_full_evidence_high_confidence(self):
        proj = self.transform.transform(
            "النار حارة",
            statistical_confidence=0.95,
            evidence_refs=["ref1", "ref2", "ref3"],
        )
        assert proj.judgment == JudgmentStatus.CERTIFICATE.value

    def test_missing_evidence_maps_to_hypothesis_publicly(self):
        proj = self.transform.transform("إن هذا لحق", statistical_confidence=0.5)
        assert proj.judgment == JudgmentStatus.HYPOTHESIS.value
        assert proj.unit.metadata["internal_state"] == JudgmentStatus.SUSPENDED.value

    def test_coordinate_type_epistemic(self):
        proj = self.transform.transform("test")
        assert proj.unit.C.coordinate_type == CoordinateType.EPISTEMIC.value

    def test_transform_notes_mention_evidence(self):
        proj = self.transform.transform("test", evidence_refs=[])
        assert any("evidence_state" in note for note in proj.transform_notes)

    def test_residual_z_score_gap(self):
        """Z.residual_score should reflect the gap between statistical and epistemic."""
        proj = self.transform.transform(
            "test", statistical_confidence=0.9, evidence_refs=[]
        )
        # with missing evidence, epistemic is capped at 0.40
        # so residual should be ~0.5 (0.9 - epistemic)
        assert proj.unit.Z.residual_score > 0.0


# ---------------------------------------------------------------------------
# compute_epistemic_certainty formula tests
# ---------------------------------------------------------------------------

class TestComputeEpistemicCertainty:
    def test_missing_evidence_caps_low(self):
        score = compute_epistemic_certainty(0.9, "missing", 10, True)
        assert score <= 0.40

    def test_partial_evidence_caps_at_65(self):
        score = compute_epistemic_certainty(0.9, "partial", 10, True)
        assert score <= 0.65

    def test_present_evidence_can_be_high(self):
        score = compute_epistemic_certainty(0.95, "present", 10, True)
        assert score >= 0.70

    def test_trace_boosts_score(self):
        score_trace = compute_epistemic_certainty(0.9, "present", 5, True)
        score_notrace = compute_epistemic_certainty(0.9, "present", 5, False)
        assert score_trace > score_notrace

    def test_zero_statistical_confidence_low_output(self):
        score = compute_epistemic_certainty(0.0, "present", 5, True)
        assert score < 0.20

    def test_score_bounded_0_1(self):
        for stat in [0.0, 0.5, 1.0]:
            for ev in ["missing", "partial", "present"]:
                score = compute_epistemic_certainty(stat, ev, 5, True)
                assert 0.0 <= score <= 1.0
