"""Tests for JudgmentClassifier."""
import pytest

from mcd.classification.judgment_classifier import JudgmentClassifier
from mcd.classification.taxonomy import JudgmentType


def test_haraam_is_shari():
    clf = JudgmentClassifier()
    result = clf.classify("هل الكذب حرام؟")
    assert result.get(JudgmentType.SHARI, 0.0) >= 0.80


def test_daar_is_value_not_shari_primary():
    """'ضار' must not be classified as shari primary."""
    clf = JudgmentClassifier()
    result = clf.classify("هل الكذب ضار؟")
    shari = result.get(JudgmentType.SHARI, 0.0)
    value = result.get(JudgmentType.VALUE, 0.0)
    assert shari < 0.70, "ضار should not trigger shari >= 0.70"
    assert value > shari or value >= 0.30, "value should be present"


def test_api_is_technical():
    clf = JudgmentClassifier()
    result = clf.classify("كيف نبني API للديكودر؟")
    assert result.get(JudgmentType.TECHNICAL, 0.0) >= 0.55


def test_api_also_practical():
    clf = JudgmentClassifier()
    result = clf.classify("ما خطوات بناء API؟")
    practical = result.get(JudgmentType.PRACTICAL, 0.0)
    technical = result.get(JudgmentType.TECHNICAL, 0.0)
    assert practical >= 0.30 or technical >= 0.30


def test_epistemic_question():
    clf = JudgmentClassifier()
    result = clf.classify("هل النار تحرق فعلًا؟")
    assert result.get(JudgmentType.EPISTEMIC, 0.0) >= 0.30


def test_waajib_is_shari():
    clf = JudgmentClassifier()
    result = clf.classify("هل الصلاة واجبة؟")
    assert result.get(JudgmentType.SHARI, 0.0) >= 0.80


def test_multi_label_result():
    """Classifier may return multiple labels simultaneously."""
    clf = JudgmentClassifier()
    result = clf.classify("كيف نبني API للديكودر؟")
    assert len(result) >= 1


def test_scores_in_range():
    clf = JudgmentClassifier()
    result = clf.classify("ما هو العقل؟")
    for score in result.values():
        assert 0.0 <= score <= 1.0


def test_empty_text_returns_default():
    clf = JudgmentClassifier()
    result = clf.classify("")
    assert len(result) >= 1


def test_value_and_epistemic_not_shari_for_nar():
    clf = JudgmentClassifier()
    result = clf.classify("النار تحرق")
    shari = result.get(JudgmentType.SHARI, 0.0)
    assert shari < 0.70


# ─── New judgment type tests (Phase 3) ───────────────────────────────────────

def test_linguistic_question_is_linguistic():
    clf = JudgmentClassifier()
    result = clf.classify("ما معنى كلمة العقل؟")
    assert result.get(JudgmentType.LINGUISTIC, 0.0) >= 0.35


def test_analogy_detection():
    clf = JudgmentClassifier()
    result = clf.classify("هذا مثل ذاك إذن له نفس الحكم")
    assert result.get(JudgmentType.ANALOGY, 0.0) >= 0.35


def test_analogy_without_illah_boosts_ambiguous():
    clf = JudgmentClassifier()
    result = clf.classify("هذا مثل ذاك إذن له نفس الحكم")
    analogy = result.get(JudgmentType.ANALOGY, 0.0)
    ambiguous = result.get(JudgmentType.AMBIGUOUS, 0.0)
    assert analogy >= 0.35
    assert ambiguous >= 0.30


def test_metaphor_detection():
    clf = JudgmentClassifier()
    result = clf.classify("العلم نور لا يطفأ — هذا مجاز واضح")
    assert result.get(JudgmentType.METAPHOR, 0.0) >= 0.35


def test_usuli_reasoning_detection():
    clf = JudgmentClassifier()
    result = clf.classify("ما ضوابط الاجتهاد في أصول الفقه؟")
    assert result.get(JudgmentType.USULI, 0.0) >= 0.35


def test_new_types_are_str_subclass():
    """New JudgmentType members must be str subclass for JSON compatibility."""
    assert isinstance(JudgmentType.AMBIGUOUS, str)
    assert isinstance(JudgmentType.LINGUISTIC, str)
    assert isinstance(JudgmentType.ANALOGY, str)
    assert isinstance(JudgmentType.METAPHOR, str)
    assert isinstance(JudgmentType.USULI, str)


def test_new_types_have_correct_values():
    assert JudgmentType.AMBIGUOUS.value == "ambiguous"
    assert JudgmentType.LINGUISTIC.value == "linguistic"
    assert JudgmentType.ANALOGY.value == "analogy"
    assert JudgmentType.METAPHOR.value == "metaphor"
    assert JudgmentType.USULI.value == "usuli_reasoning"
