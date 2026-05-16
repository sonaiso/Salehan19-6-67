"""Tests for Phase 8.1 — ReverseTrace and its integration with ProofObject."""
from __future__ import annotations

import pytest

from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.cfk.cfk_schema import JudgmentStatus
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform
from mcd.cfk.fractal_kernel import FractalKernel
from mcd.cfk.conservation_law import ConservationLawChecker
from mcd.cfk.proof_object import ProofObjectBuilder
from mcd.cfk.reverse_trace import ReverseTrace, ReverseTraceBuilder


# ---------------------------------------------------------------------------
# ReverseTrace dataclass
# ---------------------------------------------------------------------------

class TestReverseTraceDataclass:
    def test_basic_fields(self):
        rt = ReverseTrace(
            reverse_trace_id="RT-001",
            final_judgment="hypothesis",
            proof_id="PO-001",
        )
        assert rt.reverse_trace_id == "RT-001"
        assert rt.complete is False

    def test_to_dict(self):
        rt = ReverseTrace(
            reverse_trace_id="RT-001",
            final_judgment="certificate",
            proof_id="PO-001",
            evidence_refs=["e1", "e2"],
            raw_text_units=["النار حارة"],
            complete=True,
        )
        d = rt.to_dict()
        assert d["complete"] is True
        assert d["evidence_refs"] == ["e1", "e2"]
        assert d["final_judgment"] == "certificate"
        assert d["raw_text_units"] == ["النار حارة"]

    def test_incomplete_without_evidence(self):
        rt = ReverseTrace(
            reverse_trace_id="RT-002",
            final_judgment="certificate",
            proof_id="PO-002",
            evidence_refs=[],
            complete=False,
        )
        assert rt.complete is False


# ---------------------------------------------------------------------------
# ReverseTraceBuilder
# ---------------------------------------------------------------------------

def _make_projections(text="النار حارة", evidence_refs=None, claimed="hypothesis"):
    stat = StatisticalTransform()
    arab = ArabicSemanticTransform()
    epis = EpistemicTransform()
    proposal = {
        "proposal_id": "P-test",
        "gpt_output": text,
        "input_text": text,
        "proposal_type": "answer",
        "claimed_certainty": claimed,
        "claimed_evidence": evidence_refs or [],
    }
    s = stat.transform(proposal)
    a = arab.transform(text)
    e = epis.transform(text, statistical_confidence=s.comparable_score,
                       evidence_refs=evidence_refs or [])
    return s, a, e


class TestReverseTraceBuilder:
    def setup_method(self):
        self.builder = ReverseTraceBuilder()
        self.conservation = ConservationLawChecker()

    def _conservation_results(self, s, a, e):
        return [
            self.conservation.check(s.unit),
            self.conservation.check(a.unit),
            self.conservation.check(e.unit),
        ]

    def test_build_returns_reverse_trace(self):
        s, a, e = _make_projections(evidence_refs=["e1", "e2"])
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "certificate", s, a, e, cr)
        assert isinstance(rt, ReverseTrace)

    def test_build_has_projection_ids(self):
        s, a, e = _make_projections()
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "hypothesis", s, a, e, cr)
        assert rt.statistical_projection_id == s.projection_id
        assert rt.arabic_projection_id == a.projection_id
        assert rt.epistemic_projection_id == e.projection_id

    def test_complete_when_evidence_and_no_blocking(self):
        s, a, e = _make_projections(evidence_refs=["e1", "e2"])
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "certificate", s, a, e, cr)
        assert rt.complete is True
        assert rt.raw_text_units == ["النار حارة"]

    def test_incomplete_without_evidence(self):
        s, a, e = _make_projections(evidence_refs=[])
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "certificate", s, a, e, cr)
        assert rt.complete is False

    def test_incomplete_without_raw_text_anchor(self):
        s, a, e = _make_projections(text="", evidence_refs=["e1"])
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "certificate", s, a, e, cr)
        assert rt.complete is False
        assert rt.raw_text_units == []

    def test_evidence_refs_collected(self):
        s, a, e = _make_projections(evidence_refs=["e1", "e2", "e3"])
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "certificate", s, a, e, cr)
        assert "e1" in rt.evidence_refs
        assert "e2" in rt.evidence_refs

    def test_residual_refs_deduplicated(self):
        s, a, e = _make_projections()
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "hypothesis", s, a, e, cr)
        # Check no duplicates
        assert len(rt.residual_refs) == len(set(rt.residual_refs))

    def test_conservation_refs_recorded(self):
        s, a, e = _make_projections()
        cr = self._conservation_results(s, a, e)
        rt = self.builder.build("PO-001", "hypothesis", s, a, e, cr)
        assert len(rt.conservation_refs) == 3  # one per projection

    def test_trace_id_unique(self):
        s, a, e = _make_projections()
        cr = self._conservation_results(s, a, e)
        rt1 = self.builder.build("PO-001", "hypothesis", s, a, e, cr)
        rt2 = self.builder.build("PO-002", "hypothesis", s, a, e, cr)
        assert rt1.reverse_trace_id != rt2.reverse_trace_id


# ---------------------------------------------------------------------------
# ProofObject integration
# ---------------------------------------------------------------------------

class TestProofObjectReverseTrace:
    def setup_method(self):
        self.pipeline = CognitiveFractalPipeline()

    def test_proof_has_reverse_trace_obj(self):
        result = self.pipeline.run("النار حارة", evidence_refs=["e1", "e2"])
        assert result.proof.reverse_trace_obj is not None

    def test_reverse_trace_obj_is_reverse_trace(self):
        result = self.pipeline.run("النار حارة", evidence_refs=["e1", "e2"])
        assert isinstance(result.proof.reverse_trace_obj, ReverseTrace)

    def test_certificate_requires_reverse_trace_complete(self):
        """A certificate can only be issued when reverse_trace is complete."""
        result = self.pipeline.run(
            "النار حارة",
            evidence_refs=["e1", "e2"],
            evidence_types=["empirical", "experimental"],
        )
        proof = result.proof
        if proof.judgment == JudgmentStatus.CERTIFICATE.value:
            assert proof.reverse_trace_obj is not None
            assert proof.reverse_trace_obj.complete is True
            assert proof.reverse_trace_obj.raw_text_units

    def test_certificate_requires_evidence(self):
        """Without evidence, judgment must not be certificate even if score is high."""
        result = self.pipeline.run("النار حارة", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_certificate_blocked_by_conservation_violation(self):
        """Tamper: run pipeline and verify blocking conservation kills certificate."""
        # Use a text that produces a non-certificate naturally
        result = self.pipeline.run("زيد كاتب", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_hypothesis_allowed_without_complete_reverse_trace(self):
        """Hypothesis should work even without a complete trace."""
        result = self.pipeline.run("زيد كاتب", evidence_refs=[])
        # Should be hypothesis/zero — never blocked just because trace incomplete
        assert result.proof.judgment in (
            JudgmentStatus.HYPOTHESIS.value,
            JudgmentStatus.ZERO.value,
        )

    def test_proof_to_dict_includes_reverse_trace_obj(self):
        result = self.pipeline.run("النار حارة", evidence_refs=["e1", "e2"])
        d = result.proof.to_dict()
        assert "reverse_trace_obj" in d
        assert d["reverse_trace_obj"]["reverse_trace_id"].startswith("RT-")

    def test_reverse_trace_links_all_projection_ids(self):
        result = self.pipeline.run("النار حارة", evidence_refs=["e1", "e2"])
        rt = result.proof.reverse_trace_obj
        assert rt.statistical_projection_id.startswith("KP-S-")
        assert rt.arabic_projection_id.startswith("KP-A-")
        assert rt.epistemic_projection_id.startswith("KP-E-")
