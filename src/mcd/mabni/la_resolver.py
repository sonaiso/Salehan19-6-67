"""LaResolver — disambiguates لا into its functional types."""
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
class LaResolutionResult:
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


def _make_la_op(mabni_type: MabniType, logical_function: LogicalFunction,
                pragmatic_function: PragmaticFunction,
                affects_evidence: bool, affects_certainty: bool,
                certainty_effect: CertaintyEffect, operator_id: str) -> MabniOperator:
    return MabniOperator(
        operator_id=operator_id,
        surface="لا",
        normalized="لا",
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


class LaResolver:
    """Disambiguates لا into: negation, nahiya (prohibition), nafy_jins,
    atifa (contrastive), za'ida, jawabiyya."""

    def resolve(self, text: str, context: str = "") -> LaResolutionResult:
        text_stripped = text.strip()
        warnings: list[str] = []
        tokens = text_stripped.split()

        la_idx = next((i for i, t in enumerate(tokens) if t == "لا"), None)
        if la_idx is None:
            warnings.append("لا not found in text; defaulting to negation")
            op = _make_la_op(
                MabniType.negation, LogicalFunction.negation, PragmaticFunction.denial,
                True, True, CertaintyEffect.lower, "LA_NEG_001"
            )
            return LaResolutionResult("لا", "negation", op, 0.4, warnings)

        next_tok = tokens[la_idx + 1] if la_idx + 1 < len(tokens) else ""
        next_clean = _strip_diacritics(next_tok)

        # Nafy al-jins — لا + indefinite noun (no tanwin, accusative ending)
        # Pattern: لا رجلَ في الدار (negates the entire genus)
        if next_clean and not next_clean.startswith("ت") and not next_clean.startswith("ي"):
            # Check for nafy jins context: accusative noun + no verb
            remaining_after_la = tokens[la_idx + 1:]
            has_verb_after = any(
                t.startswith("ي") or t.startswith("ت") or t.startswith("ف") or t.startswith("ن")
                for t in remaining_after_la
            )
            if not has_verb_after and remaining_after_la:
                op = _make_la_op(
                    MabniType.negation, LogicalFunction.negation, PragmaticFunction.assertion,
                    True, True, CertaintyEffect.scope_limit, "LA_JNS_003"
                )
                return LaResolutionResult("لا", "nafy_jins", op, 0.78)

        # Nahiya (prohibition) — لا + jussive verb (second/third person imperative)
        if next_clean.startswith("ت") or next_clean.startswith("ي"):
            op = _make_la_op(
                MabniType.prohibition_marker, LogicalFunction.speech_act, PragmaticFunction.prohibition,
                False, False, CertaintyEffect.none, "LA_NAH_002"
            )
            return LaResolutionResult("لا", "nahiya", op, 0.85)

        # Jawabiyya (answer particle) — standalone لا or at utterance start
        if la_idx == 0 and len(tokens) <= 3:
            op = _make_la_op(
                MabniType.answer, LogicalFunction.answer, PragmaticFunction.denial,
                False, False, CertaintyEffect.none, "LA_JAW_004"
            )
            return LaResolutionResult("لا", "jawabiyya", op, 0.9)

        # Default: negation
        op = _make_la_op(
            MabniType.negation, LogicalFunction.negation, PragmaticFunction.denial,
            True, True, CertaintyEffect.lower, "LA_NEG_001"
        )
        return LaResolutionResult("لا", "negation", op, 0.7)


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
