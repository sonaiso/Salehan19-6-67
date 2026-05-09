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

        # Ensure at least one category is non-zero
        if all(v == 0.0 for v in scores.values()):
            scores[JudgmentType.EPISTEMIC] = 0.35

        # Normalise — do NOT force sum=1, keep multi-label semantics
        scores = {k: round(v, 4) for k, v in scores.items() if v > 0.0}
        return scores
