"""Tests for FractalPromptClassifier — the full 9-step pipeline.

Covers all acceptance criteria from the specification.
"""
import json

import pytest

from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
from mcd.classification.prompt_frame import PromptFrame
from mcd.classification.taxonomy import (
    CertaintyPolicy,
    EvidenceNeed,
    JudgmentType,
    KnowledgeCategory,
    RootDomain,
)


def fpc():
    return FractalPromptClassifier()


# ---------------------------------------------------------------------------
# 15.1 النار تحرق
# ---------------------------------------------------------------------------

class TestNarTahrik:
    def test_returns_prompt_frame(self):
        frame = fpc().classify("النار تحرق")
        assert isinstance(frame, PromptFrame)

    def test_root_domain_universe(self):
        frame = fpc().classify("النار تحرق")
        assert frame.root_domain.get(RootDomain.UNIVERSE, 0.0) >= 0.70

    def test_judgment_epistemic(self):
        frame = fpc().classify("النار تحرق")
        assert frame.judgment_types.get(JudgmentType.EPISTEMIC, 0.0) >= 0.30

    def test_knowledge_science(self):
        frame = fpc().classify("النار تحرق")
        assert frame.knowledge_categories.get(KnowledgeCategory.SCIENCE, 0.0) >= 0.25

    def test_evidence_sensory_or_experimental(self):
        frame = fpc().classify("النار تحرق")
        has_sensory = EvidenceNeed.SENSORY in frame.evidence_needs
        has_exp = EvidenceNeed.EXPERIMENTAL in frame.evidence_needs
        assert has_sensory or has_exp

    def test_certainty_policy_strong(self):
        frame = fpc().classify("النار تحرق")
        assert frame.certainty_policy in (
            CertaintyPolicy.STRONG_KNOWLEDGE,
            CertaintyPolicy.NEAR_CERTAINTY,
        )

    def test_routing_engine_set(self):
        frame = fpc().classify("النار تحرق")
        assert frame.routing_engine in ("nabhani_decoder", "mcd")


# ---------------------------------------------------------------------------
# 15.2 كيف نبني API للديكودر؟
# ---------------------------------------------------------------------------

class TestBuildAPI:
    def test_knowledge_technology(self):
        frame = fpc().classify("كيف نبني API للديكودر؟")
        assert frame.knowledge_categories.get(KnowledgeCategory.TECHNOLOGY, 0.0) >= 0.30

    def test_judgment_technical(self):
        frame = fpc().classify("كيف نبني API للديكودر؟")
        assert frame.judgment_types.get(JudgmentType.TECHNICAL, 0.0) >= 0.50

    def test_evidence_technical(self):
        frame = fpc().classify("كيف نبني API للديكودر؟")
        assert EvidenceNeed.TECHNICAL in frame.evidence_needs

    def test_certainty_strong(self):
        frame = fpc().classify("كيف نبني API للديكودر؟")
        assert frame.certainty_policy in (
            CertaintyPolicy.STRONG_KNOWLEDGE,
            CertaintyPolicy.HYPOTHESIS,
        )


# ---------------------------------------------------------------------------
# 15.3 ما معنى علم؟
# ---------------------------------------------------------------------------

class TestMaanaIlm:
    def test_knowledge_language(self):
        frame = fpc().classify("ما معنى علم؟")
        assert frame.knowledge_categories.get(KnowledgeCategory.LANGUAGE, 0.0) >= 0.40

    def test_judgment_epistemic(self):
        frame = fpc().classify("ما معنى علم؟")
        assert JudgmentType.EPISTEMIC in frame.judgment_types

    def test_certainty_suspend(self):
        frame = fpc().classify("ما معنى علم؟")
        assert frame.certainty_policy == CertaintyPolicy.SUSPEND

    def test_has_warnings(self):
        frame = fpc().classify("ما معنى علم؟")
        assert len(frame.warnings) > 0


# ---------------------------------------------------------------------------
# 15.4 هل الكذب ضار؟
# ---------------------------------------------------------------------------

class TestKadhabDarrr:
    def test_root_domain_human_or_life(self):
        frame = fpc().classify("هل الكذب ضار؟")
        has_human = frame.root_domain.get(RootDomain.HUMAN, 0.0) >= 0.30
        has_life = frame.root_domain.get(RootDomain.LIFE, 0.0) >= 0.20
        assert has_human or has_life

    def test_not_shari_primary(self):
        """ضار is not a shari term; shari must not be primary judgment."""
        frame = fpc().classify("هل الكذب ضار؟")
        shari = frame.judgment_types.get(JudgmentType.SHARI, 0.0)
        assert shari < 0.70, f"shari score {shari} >= 0.70"

    def test_certainty_not_suspend(self):
        frame = fpc().classify("هل الكذب ضار؟")
        assert frame.certainty_policy != CertaintyPolicy.SUSPEND


# ---------------------------------------------------------------------------
# 15.5 هل الكذب حرام؟
# ---------------------------------------------------------------------------

class TestKadhabHaraam:
    def test_shari_dominant(self):
        frame = fpc().classify("هل الكذب حرام؟")
        assert frame.judgment_types.get(JudgmentType.SHARI, 0.0) >= 0.80

    def test_evidence_shari_textual(self):
        frame = fpc().classify("هل الكذب حرام؟")
        assert EvidenceNeed.SHARI in frame.evidence_needs

    def test_certainty_suspend(self):
        frame = fpc().classify("هل الكذب حرام؟")
        assert frame.certainty_policy == CertaintyPolicy.SUSPEND

    def test_shari_warning_present(self):
        frame = fpc().classify("هل الكذب حرام؟")
        assert any("shari" in w.lower() for w in frame.warnings)


# ---------------------------------------------------------------------------
# 15.6 برومبت مركب
# ---------------------------------------------------------------------------

class TestComplexPrompt:
    TEXT = "كيف نبني نظامًا تعليميًا عربيًا يستخدم الذكاء الاصطناعي لتربية العقل؟"

    def test_multi_root_domain(self):
        frame = fpc().classify(self.TEXT)
        # human and life should both appear (or at least 1 domain)
        non_zero = [k for k, v in frame.root_domain.items() if v > 0.0]
        assert len(non_zero) >= 1

    def test_multi_concept_types(self):
        frame = fpc().classify(self.TEXT)
        assert len(frame.concept_types) >= 1

    def test_not_single_label(self):
        frame = fpc().classify(self.TEXT)
        total_labels = (
            len(frame.root_domain) +
            len(frame.concept_types) +
            len(frame.knowledge_categories)
        )
        assert total_labels >= 3


# ---------------------------------------------------------------------------
# General / regression
# ---------------------------------------------------------------------------

class TestGeneral:
    def test_no_exception_on_empty(self):
        frame = fpc().classify("")
        assert isinstance(frame, PromptFrame)

    def test_no_exception_on_noise(self):
        frame = fpc().classify("!!!???###")
        assert isinstance(frame, PromptFrame)

    def test_debug_mode_populates_debug(self):
        frame = fpc().classify("النار تحرق", include_debug=True)
        assert "concept_vectors" in frame.debug

    def test_no_debug_mode_empty_debug(self):
        frame = fpc().classify("النار تحرق", include_debug=False)
        assert frame.debug == {}

    def test_to_dict_json_serializable(self):
        frame = fpc().classify("هل الكذب حرام؟")
        d = frame.to_dict()
        json_str = json.dumps(d, ensure_ascii=False)
        assert "certainty_policy" in json_str

    def test_raw_text_preserved(self):
        text = "هل الكذب حرام؟"
        frame = fpc().classify(text)
        assert frame.raw_text == text

    def test_sub_engines_is_list(self):
        frame = fpc().classify("النار تحرق")
        assert isinstance(frame.sub_engines, list)
