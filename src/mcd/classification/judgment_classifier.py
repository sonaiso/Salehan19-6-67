"""JudgmentClassifier — classifies the type of judgment a prompt requests.

Key rule: ضار ≠ حرام, نافع ≠ واجب, مفيد ≠ جائز
"""
from __future__ import annotations

from mcd.classification.taxonomy import JudgmentType

# ---------------------------------------------------------------------------
# Keyword triggers
# ---------------------------------------------------------------------------

_SHARI_TRIGGERS = frozenset({
    "حرام", "واجب", "مكروه", "مندوب", "مباح", "فريضه", "فريضة",
    "يحرم", "يجب", "ثواب", "عقاب", "حكم شرعي", "الشرع", "الفقه",
    "الاسلام", "الشريعه", "الشريعة", "حلال",
})

_TECHNICAL_TRIGGERS = frozenset({
    "api", "كود", "برمجه", "برمجة", "ابن", "انشئ", "اكتب", "نفذ",
    "ديكودر", "سيستم", "قاعده", "قاعدة", "بيانات", "خوارزميه",
    "خوارزمية", "تطبيق", "موقع", "سيرفر", "endpoint", "test", "tests",
})

_PRACTICAL_TRIGGERS = frozenset({
    "خطوات", "خطه", "خطة", "ماذا نفعل", "كيف نبني", "كيف نعمل",
    "كيف ننشئ", "ما الخطه", "ما الخطوات", "آليه", "آلية",
})

_VALUE_TRIGGERS = frozenset({
    "ضار", "ضاره", "ضارة", "نافع", "نافعه", "نافعة", "مفيد",
    "مفيده", "مفيدة", "جيد", "سيئ", "حسن", "قبيح", "يستحسن",
    "يقبح", "يصلح", "يضر", "يفيد", "خير", "شر",
})

_EPISTEMIC_TRIGGERS = frozenset({
    "ما هو", "ما هي", "هل", "لماذا", "ما الدليل", "كيف نعرف",
    "درجه يقين", "درجة يقين", "معلومات سابقه", "معلومات سابقة",
    "يسبب", "يدل", "يتضمن", "صحيح", "خاطئ", "معرفه", "معرفة",
    "منهج", "مقياس", "واقع",
})

# New judgment type triggers

_LINGUISTIC_TRIGGERS = frozenset({
    "ما معنى", "معنى", "مدلول", "دلالة", "دلاله", "لغة", "لغه",
    "كلمة", "كلمه", "مصطلح", "اشتقاق", "جذر", "نحو", "صرف",
    "بلاغة", "بلاغه", "لفظ", "ألفاظ", "سيمانتيك", "تعريف لغوي",
    "ما دلالة", "ما اللفظ", "ما الكلمة",
})

_ANALOGY_TRIGGERS = frozenset({
    "مثل", "كمثل", "إذن له نفس الحكم", "له نفس الحكم", "بالمثل",
    "قياسًا", "قياسا", "على القياس", "شبيه", "مشابه", "يشبه",
    "كذلك", "كما أن", "نظير", "مقارنة", "مقاربة",
})

_METAPHOR_TRIGGERS = frozenset({
    "مجاز", "مجازًا", "مجازا", "استعارة", "تشبيه", "كناية",
    "رمز", "رمزي", "رمزية", "مجازية", "غير حرفي", "لا يقصد حرفيًا",
    "يرمز", "يدل مجازًا", "في المعنى المجازي",
})

_USULI_TRIGGERS = frozenset({
    "أصول الفقه", "اصول الفقه", "قاعدة أصولية", "قاعدة اصولية",
    "الدليل الشرعي", "العلة", "المناط", "التعليل", "الاستنباط",
    "الاجتهاد", "الإجماع", "القياس الفقهي", "الأصولي",
    "استدلال أصولي", "منهج أصولي", "طريقة الاستدلال الشرعي",
})

_AMBIGUOUS_TRIGGERS = frozenset({
    "غير واضح", "غامض", "ملتبس", "محتمل", "يحتمل أكثر من",
    "له أكثر من معنى", "تعدد المعاني", "لا أعرف المقصود",
})


def _score_text(text: str, trigger_set: frozenset[str], weight: float = 0.35) -> float:
    """Scan text for triggers; return normalised hit fraction."""
    text_lower = text.lower()
    hits = sum(1 for t in trigger_set if t in text_lower)
    return min(1.0, hits * weight)


class JudgmentClassifier:
    """Classify the judgment type(s) present in a prompt."""

    def classify(self, text: str, concept_judgment_hints: dict[str, float] | None = None) -> dict[str, float]:
        """Return a dict of JudgmentType → score (multi-label, not exclusive)."""
        scores: dict[str, float] = {
            JudgmentType.SHARI: 0.0,
            JudgmentType.TECHNICAL: 0.0,
            JudgmentType.PRACTICAL: 0.0,
            JudgmentType.VALUE: 0.0,
            JudgmentType.EPISTEMIC: 0.0,
            JudgmentType.AMBIGUOUS: 0.0,
            JudgmentType.LINGUISTIC: 0.0,
            JudgmentType.ANALOGY: 0.0,
            JudgmentType.METAPHOR: 0.0,
            JudgmentType.USULI: 0.0,
        }

        # Text-level triggers
        # Shari triggers are high-weight: a single "حرام" or "واجب" → 0.90
        scores[JudgmentType.SHARI] = max(
            scores[JudgmentType.SHARI], _score_text(text, _SHARI_TRIGGERS, weight=0.90)
        )
        scores[JudgmentType.TECHNICAL] = max(
            scores[JudgmentType.TECHNICAL], _score_text(text, _TECHNICAL_TRIGGERS)
        )
        scores[JudgmentType.PRACTICAL] = max(
            scores[JudgmentType.PRACTICAL], _score_text(text, _PRACTICAL_TRIGGERS)
        )
        scores[JudgmentType.VALUE] = max(
            scores[JudgmentType.VALUE], _score_text(text, _VALUE_TRIGGERS)
        )
        scores[JudgmentType.EPISTEMIC] = max(
            scores[JudgmentType.EPISTEMIC], _score_text(text, _EPISTEMIC_TRIGGERS)
        )
        scores[JudgmentType.LINGUISTIC] = max(
            scores[JudgmentType.LINGUISTIC], _score_text(text, _LINGUISTIC_TRIGGERS, weight=0.50)
        )
        scores[JudgmentType.ANALOGY] = max(
            scores[JudgmentType.ANALOGY], _score_text(text, _ANALOGY_TRIGGERS, weight=0.50)
        )
        scores[JudgmentType.METAPHOR] = max(
            scores[JudgmentType.METAPHOR], _score_text(text, _METAPHOR_TRIGGERS, weight=0.50)
        )
        scores[JudgmentType.USULI] = max(
            scores[JudgmentType.USULI], _score_text(text, _USULI_TRIGGERS, weight=0.50)
        )
        scores[JudgmentType.AMBIGUOUS] = max(
            scores[JudgmentType.AMBIGUOUS], _score_text(text, _AMBIGUOUS_TRIGGERS, weight=0.50)
        )

        # Boost from concept hints
        if concept_judgment_hints:
            for label, hint_score in concept_judgment_hints.items():
                if label in scores:
                    scores[label] = max(scores[label], hint_score)

        # If shari is dominant and score is high, ensure VALUE ≠ SHARI
        # (ضار is not سرعي even if both have scores)
        if scores[JudgmentType.SHARI] >= 0.70:
            # VALUE stays independent — do not reduce it
            pass

        # Analogy without explicit illah (علة) → flag ambiguous unless illah is stated
        if scores[JudgmentType.ANALOGY] >= 0.35:
            illah_markers = {"العلة", "لأن", "بسبب", "للعلة", "المناط"}
            text_lower = text.lower()
            if not any(m in text_lower for m in illah_markers):
                # Analogy with no stated illah → boost ambiguous slightly
                scores[JudgmentType.AMBIGUOUS] = max(
                    scores[JudgmentType.AMBIGUOUS], 0.35
                )

        # Ensure at least one category is non-zero
        if all(v == 0.0 for v in scores.values()):
            scores[JudgmentType.EPISTEMIC] = 0.35

        # Normalise — do NOT force sum=1, keep multi-label semantics
        scores = {k: round(v, 4) for k, v in scores.items() if v > 0.0}
        return scores
