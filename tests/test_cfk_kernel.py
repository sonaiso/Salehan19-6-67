"""Tests for Phase 8 FractalKernel, ConservationLaw, and ProofObject."""
from __future__ import annotations

import pytest
from mcd.cfk.cfk_schema import (
    CognitiveFractalUnit,
    JudgmentStatus,
    CoordinateType,
    EvidenceInfo,
    CertaintyInfo,
)
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform
from mcd.cfk.fractal_kernel import FractalKernel, KernelResult
from mcd.cfk.conservation_law import ConservationLawChecker, ConservationViolation
from mcd.cfk.proof_object import ProofObject, ProofObjectBuilder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_projections(text: str, evidence_refs=None, claimed_certainty=None):
    evidence_refs = evidence_refs or []
    stat_t = StatisticalTransform()
    arab_t = ArabicSemanticTransform()
    epis_t = EpistemicTransform()

    proposal = {
        "proposal_id": "P-test",
        "gpt_output": text,
        "input_text": text,
        "proposal_type": "answer",
        "claimed_certainty": claimed_certainty,
        "claimed_evidence": evidence_refs,
    }
    s = stat_t.transform(proposal)
    a = arab_t.transform(text)
    e = epis_t.transform(
        text,
        statistical_confidence=s.comparable_score,
        evidence_refs=evidence_refs,
        linguistic_force=a.unit.C.linguistic_force,
        source_text=text,
    )
    return s, a, e


# ---------------------------------------------------------------------------
# FractalKernel tests
# ---------------------------------------------------------------------------

class TestFractalKernel:
    def setup_method(self):
        self.kernel = FractalKernel()

    def test_apply_returns_kernel_result(self):
        s, a, e = _make_projections("زيد كاتب")
        result = self.kernel.apply("زيد كاتب", s, a, e)
        assert isinstance(result, KernelResult)
        assert result.text == "زيد كاتب"

    def test_kernel_score_is_weighted_sum(self):
        s, a, e = _make_projections("زيد كاتب")
        result = self.kernel.apply("زيد كاتب", s, a, e)
        expected = s.comparable_score * 0.25 + a.comparable_score * 0.30 + e.comparable_score * 0.45
        assert abs(result.kernel_score - expected) < 1e-6

    def test_missing_evidence_caps_judgment(self):
        """No evidence → judgment ≤ hypothesis (not certificate)."""
        s, a, e = _make_projections("إن هذا لحق")
        result = self.kernel.apply("إن هذا لحق", s, a, e)
        assert result.kernel_judgment in (
            JudgmentStatus.HYPOTHESIS.value,
            JudgmentStatus.SUSPEND.value,
        )
        assert result.kernel_judgment != JudgmentStatus.CERTIFICATE.value

    def test_universal_without_evidence_is_suspend(self):
        s, a, e = _make_projections("كل الشركات تستخدم هذه التقنية")
        result = self.kernel.apply("كل الشركات تستخدم هذه التقنية", s, a, e)
        assert result.kernel_judgment == JudgmentStatus.SUSPEND.value
        assert result.residual_type == "unsupported_generalization_residual"

    def test_emphasis_does_not_upgrade_to_certificate(self):
        """emphasis ≠ evidence — can't produce certificate without proof."""
        s, a, e = _make_projections("إن زيداً لكريم")
        result = self.kernel.apply("إن زيداً لكريم", s, a, e)
        assert result.kernel_judgment != JudgmentStatus.CERTIFICATE.value

    def test_cognitive_residual_non_negative(self):
        s, a, e = _make_projections("زيد كاتب")
        result = self.kernel.apply("زيد كاتب", s, a, e)
        assert result.cognitive_residual >= 0.0

    def test_result_id_unique(self):
        s, a, e = _make_projections("test")
        r1 = self.kernel.apply("test", s, a, e)
        r2 = self.kernel.apply("test", s, a, e)
        assert r1.result_id != r2.result_id

    def test_to_dict_has_all_keys(self):
        s, a, e = _make_projections("زيد كاتب")
        result = self.kernel.apply("زيد كاتب", s, a, e)
        d = result.to_dict()
        for key in ("result_id", "text", "kernel_judgment", "kernel_score",
                    "k_statistical", "k_arabic", "k_epistemic",
                    "cognitive_residual", "residual_type", "notes"):
            assert key in d

    def test_certificate_with_evidence_high_confidence(self):
        s, a, e = _make_projections(
            "النار حارة",
            evidence_refs=["e1", "e2"],
            claimed_certainty="near_certainty",
        )
        result = self.kernel.apply("النار حارة", s, a, e)
        assert result.kernel_judgment == JudgmentStatus.CERTIFICATE.value

    def test_notes_are_populated(self):
        s, a, e = _make_projections("كل الناس يعلمون")
        result = self.kernel.apply("كل الناس يعلمون", s, a, e)
        assert len(result.notes) > 0


# ---------------------------------------------------------------------------
# ConservationLawChecker tests
# ---------------------------------------------------------------------------

class TestConservationLawChecker:
    def setup_method(self):
        self.checker = ConservationLawChecker()

    def test_valid_unit_passes(self):
        unit = CognitiveFractalUnit.make("كاتب")
        unit.T.reverse_path = ["origin"]
        unit.N.level = "word"  # not claim/sentence, so trace law not triggered
        result = self.checker.check(unit)
        assert result.passed

    def test_missing_unit_id_is_blocking(self):
        unit = CognitiveFractalUnit.make("test")
        unit.unit_id = ""
        result = self.checker.check(unit)
        assert not result.passed
        laws = [v.law for v in result.violations]
        assert "unit" in laws
        severities = [v.severity for v in result.violations]
        assert "blocking" in severities

    def test_empty_edge_fields_violate_relation(self):
        unit = CognitiveFractalUnit.make("test")
        unit.R.edges = [{"from": "", "type": "rel", "to": "X"}]
        result = self.checker.check(unit)
        laws = [v.law for v in result.violations]
        assert "relation" in laws

    def test_high_epistemic_without_evidence_violates_evidence_law(self):
        unit = CognitiveFractalUnit.make("test")
        unit.C.epistemic_certainty = 0.80
        unit.E.evidence_state = "missing"
        result = self.checker.check(unit)
        laws = [v.law for v in result.violations]
        assert "evidence" in laws

    def test_emphasis_plus_high_certainty_no_evidence_violates_certainty(self):
        unit = CognitiveFractalUnit.make("test")
        unit.C.linguistic_force = "emphasis"
        unit.C.epistemic_certainty = 0.80
        unit.E.evidence_state = "missing"
        result = self.checker.check(unit)
        laws = [v.law for v in result.violations]
        assert "certainty" in laws or "evidence" in laws

    def test_claim_without_trace_violates_trace(self):
        unit = CognitiveFractalUnit.make("test")
        unit.N.level = "claim"
        unit.T.reverse_path = []
        result = self.checker.check(unit)
        laws = [v.law for v in result.violations]
        assert "trace" in laws

    def test_conservation_score_decreases_with_violations(self):
        unit1 = CognitiveFractalUnit.make("good")
        unit1.T.reverse_path = ["x"]

        unit2 = CognitiveFractalUnit.make("bad")
        unit2.unit_id = ""

        r1 = self.checker.check(unit1)
        r2 = self.checker.check(unit2)
        assert r2.conservation_score < r1.conservation_score

    def test_conservation_score_bounded(self):
        unit = CognitiveFractalUnit.make("test")
        result = self.checker.check(unit)
        assert 0.0 <= result.conservation_score <= 1.0

    def test_to_dict_structure(self):
        unit = CognitiveFractalUnit.make("test")
        result = self.checker.check(unit)
        d = result.to_dict()
        assert "unit_id" in d
        assert "passed" in d
        assert "violations" in d
        assert "conservation_score" in d


# ---------------------------------------------------------------------------
# ProofObjectBuilder tests
# ---------------------------------------------------------------------------

class TestProofObjectBuilder:
    def setup_method(self):
        self.kernel = FractalKernel()
        self.checker = ConservationLawChecker()
        self.builder = ProofObjectBuilder()

    def _build(self, text, evidence_refs=None, claimed_certainty=None):
        evidence_refs = evidence_refs or []
        s, a, e = _make_projections(text, evidence_refs, claimed_certainty)
        kr = self.kernel.apply(text, s, a, e)
        conservation = [self.checker.check(u.unit) for u in (s, a, e)]
        return self.builder.build(kr, conservation)

    def test_returns_proof_object(self):
        proof = self._build("زيد كاتب")
        assert isinstance(proof, ProofObject)

    def test_proof_id_prefix(self):
        proof = self._build("test")
        assert proof.proof_id.startswith("PO-")

    def test_no_evidence_is_not_certificate(self):
        proof = self._build("إن هذا لحق")
        assert proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_with_evidence_high_confidence_can_be_certificate(self):
        proof = self._build("النار حارة", evidence_refs=["e1", "e2"], claimed_certainty="near_certainty")
        assert proof.judgment == JudgmentStatus.CERTIFICATE.value

    def test_learning_signal_mapped(self):
        proof = self._build("زيد كاتب")
        assert proof.learning_signal in ("reinforce", "correct", "suspend", "ignore")

    def test_reverse_trace_non_empty(self):
        proof = self._build("النار حارة")
        assert len(proof.reverse_trace) > 0

    def test_to_dict_keys(self):
        proof = self._build("test")
        d = proof.to_dict()
        for key in ("proof_id", "text", "judgment", "statistical_confidence",
                    "linguistic_force", "epistemic_certainty", "evidence_state",
                    "conservation", "cognitive_residual", "residual_type",
                    "learning_signal", "reverse_trace"):
            assert key in d

    def test_blocking_violation_forces_zero(self):
        """A blocking conservation violation should force judgment=zero."""
        from mcd.cfk.conservation_law import ConservationCheckResult, ConservationViolation
        s, a, e = _make_projections("test")
        kr = self.kernel.apply("test", s, a, e)

        blocking_result = ConservationCheckResult(
            unit_id="bad",
            passed=False,
            violations=[
                ConservationViolation(law="unit", description="test", severity="blocking")
            ],
            conservation_score=0.0,
        )
        proof = self.builder.build(kr, [blocking_result])
        assert proof.judgment == JudgmentStatus.ZERO.value
        assert proof.learning_signal == "ignore"
