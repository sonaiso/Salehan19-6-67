"""MaResolver — disambiguates the Arabic particle ما."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_registry import MabniRegistry
from mcd.mabni.mabni_schema import (
    CertaintyEffect,
    LogicalFunction,
    MabniType,
    PragmaticFunction,
)


@dataclass
class MaResolutionResult:
    surface: str
    resolved_type: str
    operator: MabniOperator
    confidence: float
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "resolved_type": self.resolved_type,
            "operator": self.operator.to_dict(),
            "confidence": round(self.confidence, 4),
            "warnings": self.warnings,
        }


_REGISTRY = MabniRegistry()

# Negation verb patterns (words that follow negation ما)
_NEG_VERB_STARTERS = {
    "جاء", "حضر", "قال", "كان", "أراد", "فعل", "ذهب", "وجد", "رأى", "علم",
    "أكل", "شرب", "نام", "قام", "جلس", "كتب", "قرأ", "سمع", "أخذ", "ترك",
    "يجيء", "يحضر", "يقول", "يكون", "يريد", "يفعل"
}

_QUESTION_MARKERS = {"؟", "هذا", "هذه", "ذلك", "هو", "هي", "هم", "الأمر", "اسمك", "اسمه"}
_INNAMA_PREFIX = "إنما"


def _make_ma_operator(mabni_type: MabniType, logical_function: LogicalFunction,
                      pragmatic_function: PragmaticFunction,
                      affects_evidence: bool, affects_certainty: bool,
                      certainty_effect: CertaintyEffect,
                      operator_id: str) -> MabniOperator:
    return MabniOperator(
        operator_id=operator_id,
        surface="ما",
        normalized="ما",
        mabni_type=mabni_type,
        logical_function=logical_function,
        pragmatic_function=pragmatic_function,
        affects_evidence=affects_evidence,
        affects_certainty=affects_certainty,
        creates_evidence=False,
        certainty_effect=certainty_effect,
        trace_ids=[],
        examples=[],
    )


class MaResolver:
    """Disambiguates ما into: negation, interrogative, relative, masdariyya,
    conditional, kaffa, ta'ajjub, mubhama."""

    def resolve(self, text: str, context: str = "") -> MaResolutionResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        # إنما → qasr/restriction (handled before general ما)
        if _INNAMA_PREFIX in text_stripped:
            op = _make_ma_operator(
                MabniType.restriction, LogicalFunction.qasr, PragmaticFunction.assertion,
                True, True, CertaintyEffect.scope_limit, "MA_INNAMA_QSR"
            )
            return MaResolutionResult("إنما", "innama_qasr", op, 0.95)

        # Locate ما token
        ma_index = None
        for i, t in enumerate(tokens):
            if t in ("ما", "مَا"):
                ma_index = i
                break

        if ma_index is None:
            # Fallback: text doesn't contain ما directly
            warnings.append("ما not found in text; defaulting to relative")
            op = _make_ma_operator(
                MabniType.relative, LogicalFunction.reference, PragmaticFunction.assertion,
                False, False, CertaintyEffect.none, "MA_REL_003"
            )
            return MaResolutionResult("ما", "relative", op, 0.4, warnings)

        next_token = tokens[ma_index + 1] if ma_index + 1 < len(tokens) else ""
        # Remove diacritics from next_token for matching
        next_clean = _strip_diacritics(next_token)

        # Rule: question mark or "هذا" after ما → interrogative
        if "؟" in text_stripped or next_clean in _QUESTION_MARKERS:
            op = _make_ma_operator(
                MabniType.interrogative, LogicalFunction.speech_act, PragmaticFunction.question,
                False, True, CertaintyEffect.suspend, "MA_INT_002"
            )
            return MaResolutionResult("ما", "interrogative", op, 0.9)

        # Rule: next word is a verb negation pattern → negation
        if next_clean in _NEG_VERB_STARTERS:
            op = _make_ma_operator(
                MabniType.negation, LogicalFunction.negation, PragmaticFunction.assertion,
                True, True, CertaintyEffect.lower, "MA_NEG_001"
            )
            return MaResolutionResult("ما", "negation", op, 0.88)

        # Rule: masdariyya — ما followed by مضارع (يفعل pattern)
        if next_clean.startswith("ي") or next_clean.startswith("ت") or next_clean.startswith("ن") or next_clean.startswith("أ"):
            # Could be masdariyya or relative; check context
            if "يسرني" in text_stripped or "أريد" in text_stripped or "أعجبني" in text_stripped:
                op = _make_ma_operator(
                    MabniType.particle, LogicalFunction.relation, PragmaticFunction.assertion,
                    False, False, CertaintyEffect.none, "MA_MAS_004"
                )
                return MaResolutionResult("ما", "masdariyya", op, 0.75)

        # Rule: conditional — ما at start of condition clause
        if ma_index == 0 and (context.startswith("شرط") or "تفعل" in text_stripped):
            op = _make_ma_operator(
                MabniType.conditional, LogicalFunction.condition, PragmaticFunction.assertion,
                False, True, CertaintyEffect.suspend, "MA_CON_005"
            )
            return MaResolutionResult("ما", "conditional", op, 0.7)

        # Rule: kaffa — in compound رُبَّما, طالما, etc.
        prev_token = tokens[ma_index - 1] if ma_index > 0 else ""
        if prev_token in ("ربّ", "ربَّ", "طال", "قلّ", "كثُر"):
            op = _make_ma_operator(
                MabniType.particle, LogicalFunction.suspension, PragmaticFunction.assertion,
                False, False, CertaintyEffect.none, "MA_KAF_005"
            )
            return MaResolutionResult("ما", "kaffa", op, 0.85)

        # Default: relative
        op = _make_ma_operator(
            MabniType.relative, LogicalFunction.reference, PragmaticFunction.assertion,
            False, False, CertaintyEffect.none, "MA_REL_003"
        )
        warnings.append("defaulting to relative; consider providing more context")
        return MaResolutionResult("ما", "relative", op, 0.6, warnings)


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics (harakat) from text."""
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
