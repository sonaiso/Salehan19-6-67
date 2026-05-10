"""Tests for Phase 8.1 — No Silent Fallback in ArabicSemanticTransform."""
from __future__ import annotations

import pytest

from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.cfk.cfk_schema import JudgmentStatus


class TestArabicTransformFallbackRecording:
    """Verify that murab/mabni fallbacks are recorded in metadata and cap the score."""

    def setup_method(self):
        self.transform = ArabicSemanticTransform()

    def test_metadata_has_murab_fallback_key(self):
        """Transform always records murab_fallback in metadata."""
        proj = self.transform.transform("النار حارة")
        assert "murab_fallback" in proj.unit.metadata

    def test_metadata_has_mabni_fallback_key(self):
        """Transform always records mabni_fallback in metadata."""
        proj = self.transform.transform("النار حارة")
        assert "mabni_fallback" in proj.unit.metadata

    def test_murab_fallback_is_bool(self):
        proj = self.transform.transform("زيد كاتب")
        assert isinstance(proj.unit.metadata["murab_fallback"], bool)

    def test_mabni_fallback_is_bool(self):
        proj = self.transform.transform("زيد كاتب")
        assert isinstance(proj.unit.metadata["mabni_fallback"], bool)

    def test_arabic_transform_records_murab_fallback(self):
        """When murab is unavailable, murab_fallback=True must be recorded."""
        t = ArabicSemanticTransform()
        # If murab is not installed (common in CI), murab_fallback=True
        try:
            import mcd.murab.murab_analyzer as _m
            murab_available = True
        except Exception:
            murab_available = False

        proj = t.transform("النار حارة")
        if not murab_available:
            assert proj.unit.metadata["murab_fallback"] is True
        else:
            # murab is installed — fallback should be False
            assert isinstance(proj.unit.metadata["murab_fallback"], bool)

    def test_arabic_transform_records_mabni_fallback(self):
        """When mabni is unavailable, mabni_fallback=True must be recorded."""
        t = ArabicSemanticTransform()
        try:
            import mcd.mabni.mabni_unfolder as _m
            mabni_available = True
        except Exception:
            mabni_available = False

        proj = t.transform("إن هذا لصحيح")
        if not mabni_available:
            assert proj.unit.metadata["mabni_fallback"] is True
        else:
            assert isinstance(proj.unit.metadata["mabni_fallback"], bool)

    def test_arabic_fallback_caps_score(self):
        """When fallback is used, comparable_score must be capped at 0.55."""
        t = ArabicSemanticTransform()
        proj = t.transform("إن زيداً لكاتب")  # emphasis → natural score = 0.85

        murab_fb = proj.unit.metadata.get("murab_fallback", False)
        mabni_fb = proj.unit.metadata.get("mabni_fallback", False)

        if murab_fb or mabni_fb:
            assert proj.comparable_score <= 0.55, (
                f"Fallback active but comparable_score={proj.comparable_score} > 0.55"
            )

    def test_no_fallback_allows_full_score(self):
        """When both murab and mabni succeed, score is not artificially capped."""
        t = ArabicSemanticTransform()
        proj = t.transform("إن زيداً لكاتب")

        murab_fb = proj.unit.metadata.get("murab_fallback", False)
        mabni_fb = proj.unit.metadata.get("mabni_fallback", False)

        if not murab_fb and not mabni_fb:
            # emphasis score = 0.85 uncapped
            assert proj.comparable_score > 0.55

    def test_fallback_note_in_transform_notes_murab(self):
        """When murab fallback is used, notes must mention it."""
        t = ArabicSemanticTransform()
        proj = t.transform("النار حارة")

        murab_fb = proj.unit.metadata.get("murab_fallback", False)
        if murab_fb:
            assert any("murab_unavailable_fallback_used" in n for n in proj.transform_notes)

    def test_fallback_note_in_transform_notes_mabni(self):
        """When mabni fallback is used, notes must mention it."""
        t = ArabicSemanticTransform()
        proj = t.transform("النار حارة")

        mabni_fb = proj.unit.metadata.get("mabni_fallback", False)
        if mabni_fb:
            assert any("mabni_unavailable_fallback_used" in n for n in proj.transform_notes)

    def test_fallback_cap_note_in_transform_notes(self):
        """When either fallback is used, notes must mention score cap."""
        t = ArabicSemanticTransform()
        proj = t.transform("إن زيداً لكاتب")

        murab_fb = proj.unit.metadata.get("murab_fallback", False)
        mabni_fb = proj.unit.metadata.get("mabni_fallback", False)

        if murab_fb or mabni_fb:
            assert any("comparable_score_capped_at" in n for n in proj.transform_notes)

    def test_transform_notes_non_empty(self):
        """transform_notes must always be non-empty."""
        t = ArabicSemanticTransform()
        proj = t.transform("زيد كاتب")
        assert len(proj.transform_notes) >= 1


# ---------------------------------------------------------------------------
# Pipeline-level: statistical confidence alone must not produce certificate
# ---------------------------------------------------------------------------

class TestNoCertificateWithoutEvidence:
    def setup_method(self):
        self.pipeline = CognitiveFractalPipeline()

    def test_gpt_high_confidence_without_evidence_not_certificate(self):
        """High statistical confidence with no evidence → never certificate."""
        result = self.pipeline.run(
            "الأرض كروية",
            proposal_dict={
                "proposal_id": "P-high",
                "gpt_output": "الأرض كروية",
                "input_text": "الأرض كروية",
                "proposal_type": "answer",
                "claimed_certainty": "near_certainty",
                "claimed_evidence": [],
            },
            evidence_refs=[],
        )
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_emphasis_without_evidence_not_certificate(self):
        """Emphasis linguistic force alone + no evidence → never certificate."""
        result = self.pipeline.run("إن هذا لحق", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_universal_without_evidence_suspend(self):
        """Universal quantifier + no evidence → suspend or hypothesis, not certificate."""
        result = self.pipeline.run("كل الشركات تستخدم GraphRAG", evidence_refs=[])
        assert result.proof.judgment in (
            JudgmentStatus.SUSPEND.value,
            JudgmentStatus.HYPOTHESIS.value,
        )
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_murab_syntactic_certainty_not_factual_certainty(self):
        """Syntactic certainty from murab cannot produce a certificate."""
        # جاء الطالبُ has clear syntactic markers but no factual evidence
        result = self.pipeline.run("جاء الطالبُ", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_trace_completeness_not_truth(self):
        """Trace completeness alone cannot produce a certificate."""
        result = self.pipeline.run("النار حارة", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value
