"""PrepositionResolver — resolves Arabic prepositions and their senses."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_schema import (
    CertaintyEffect,
    LogicalFunction,
    MabniType,
    PragmaticFunction,
)


@dataclass
class PrepositionResolutionResult:
    surface: str
    sense: str
    relation_type: str
    operator: MabniOperator
    confidence: float
    certainty_effect: str = "none"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "sense": self.sense,
            "relation_type": self.relation_type,
            "operator": self.operator.to_dict(),
            "confidence": round(self.confidence, 4),
            "certainty_effect": self.certainty_effect,
            "warnings": self.warnings,
        }


def _make_prep_op(surface: str, operator_id: str) -> MabniOperator:
    return MabniOperator(
        operator_id=operator_id,
        surface=surface,
        normalized=surface,
        mabni_type=MabniType.preposition,
        logical_function=LogicalFunction.relation,
        pragmatic_function=PragmaticFunction.assertion,
        affects_evidence=False,
        affects_certainty=False,
        creates_evidence=False,
        certainty_effect=CertaintyEffect.none,
        trace_ids=[],
        examples=[],
    )


# Preposition sense rules: (keyword_hints, sense, relation_type, confidence)
_PREP_SENSES: dict[str, list[tuple[list[str], str, str, float]]] = {
    "ب": [
        (["بسبب", "لأن", "بسبب"], "causation", "causal_relation", 0.82),
        (["كتب", "استخدم", "قاتل", "ضرب"], "instrument", "instrumental_relation", 0.85),
        (["مررت", "جلست", "قمت"], "accompaniment", "comitative_relation", 0.75),
        ([], "instrument", "instrumental_relation", 0.6),
    ],
    "في": [
        (["يبحث", "يختص", "مجال", "علم", "دراسة"], "domain", "domain_relation", 0.82),
        (["البيت", "المسجد", "المدرسة", "الغرفة", "المكان"], "place", "locative_relation", 0.88),
        (["الصباح", "المساء", "الليل", "اليوم", "الشهر"], "time", "temporal_relation", 0.85),
        ([], "place", "locative_relation", 0.6),
    ],
    "من": [
        (["جاء", "خرج", "أتى", "وصل", "قدم"], "source", "source_relation", 0.88),
        (["أخذ", "أعطى", "نال", "حصل"], "partitive", "partitive_relation", 0.80),
        (["أعلى", "أكبر", "أفضل", "أكثر"], "comparison", "comparative_relation", 0.85),
        ([], "partitive", "partitive_relation", 0.6),
    ],
    "إلى": [
        (["ذهب", "سافر", "وصل", "انتهى"], "destination", "goal_relation", 0.88),
        (["بالنسبة", "نظراً"], "perspective", "perspective_relation", 0.75),
        ([], "destination", "goal_relation", 0.65),
    ],
    "على": [
        (["واجب", "فرض", "يجب", "لازم"], "obligation", "deontic_relation", 0.85),
        (["الطاولة", "الأرض", "السرير", "السطح"], "surface", "surface_relation", 0.88),
        (["ثقة", "اتفاق", "عهد"], "basis", "ground_relation", 0.78),
        ([], "surface", "surface_relation", 0.65),
    ],
    "عن": [
        (["تحدث", "قال", "كتب", "أخبر", "سأل"], "topic", "topical_relation", 0.88),
        (["ابتعد", "انصرف", "تركه"], "separation", "separation_relation", 0.82),
        ([], "topic", "topical_relation", 0.65),
    ],
    "ل": [
        (["لأن", "بسبب"], "reason", "causal_relation", 0.82),
        (["زيد", "أحمد", "المدرسة", "الطالب"], "ownership", "possessive_relation", 0.80),
        (["يذهب", "يعمل", "جاء", "أتى"], "purpose", "purpose_relation", 0.78),
        ([], "ownership", "possessive_relation", 0.6),
    ],
    "ك": [
        ([], "comparison", "comparative_relation", 0.75),
    ],
    "حتى": [
        (["الآن", "اليوم", "انتهى"], "limit", "limit_relation", 0.80),
        ([], "purpose", "purpose_relation", 0.65),
    ],
    "منذ": [
        ([], "time_start", "temporal_start_relation", 0.85),
    ],
    "مذ": [
        ([], "time_start", "temporal_start_relation", 0.85),
    ],
    "رب": [
        ([], "probability", "probabilistic_relation", 0.75),
    ],
}


class PrepositionResolver:
    """Resolves Arabic prepositions to their contextual senses.
    Prepositions create relations, not evidence — certainty_effect is always none.
    """

    def resolve(self, prep: str, context: str = "") -> PrepositionResolutionResult:
        warnings: list[str] = []
        senses = _PREP_SENSES.get(prep)

        if senses is None:
            warnings.append(f"unknown preposition '{prep}'; defaulting to generic relation")
            op = _make_prep_op(prep, f"PREP_UNK_{prep}")
            return PrepositionResolutionResult(
                surface=prep, sense="relation", relation_type="generic_relation",
                operator=op, confidence=0.4, certainty_effect="none", warnings=warnings
            )

        ctx_tokens = set(context.split())
        for keywords, sense, relation_type, conf in senses:
            if not keywords or ctx_tokens.intersection(keywords):
                op = _make_prep_op(prep, f"PREP_{prep}_{sense.upper()}")
                return PrepositionResolutionResult(
                    surface=prep, sense=sense, relation_type=relation_type,
                    operator=op, confidence=conf, certainty_effect="none", warnings=warnings
                )

        # Fallback
        op = _make_prep_op(prep, f"PREP_{prep}_DEFAULT")
        warnings.append(f"no context match for '{prep}'; using default sense")
        return PrepositionResolutionResult(
            surface=prep, sense="relation", relation_type="generic_relation",
            operator=op, confidence=0.5, certainty_effect="none", warnings=warnings
        )

    def resolve_all(self, text: str) -> list[PrepositionResolutionResult]:
        """Resolve all prepositions found in the text."""
        tokens = text.split()
        results: list[PrepositionResolutionResult] = []
        for tok in tokens:
            clean = _strip_diacritics(tok)
            if clean in _PREP_SENSES:
                results.append(self.resolve(clean, context=text))
        return results


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
