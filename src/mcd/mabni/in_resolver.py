"""InResolver — disambiguates إن / إنّ / إنما."""
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
class InResolutionResult:
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


def _make_in_op(surface: str, mabni_type: MabniType, logical_function: LogicalFunction,
                pragmatic_function: PragmaticFunction,
                affects_evidence: bool, affects_certainty: bool,
                certainty_effect: CertaintyEffect, operator_id: str) -> MabniOperator:
    return MabniOperator(
        operator_id=operator_id,
        surface=surface,
        normalized="إن",
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


class InResolver:
    """Disambiguates إن / إنّ / إنما into:
    in_conditional, in_negative, inna_emphasis, in_mukhaffafa, innama_qasr."""

    def resolve(self, text: str, context: str = "") -> InResolutionResult:
        text_stripped = text.strip()
        warnings: list[str] = []

        # إنما → qasr/restriction (highest priority)
        if text_stripped.startswith("إنما") or "إنما" in text_stripped:
            op = _make_in_op(
                "إنما", MabniType.restriction, LogicalFunction.qasr, PragmaticFunction.assertion,
                True, True, CertaintyEffect.scope_limit, "INNAMA_QSR_004"
            )
            return InResolutionResult("إنما", "innama_qasr", op, 0.95)

        # إنّ (with shadda) → emphasis — does NOT create evidence
        if "إنّ" in text_stripped or "إِنَّ" in text_stripped:
            op = _make_in_op(
                "إنّ", MabniType.emphasis, LogicalFunction.emphasis, PragmaticFunction.assertion,
                False, True, CertaintyEffect.emphasis_only, "INNA_EMP_003"
            )
            warnings.append("inna_emphasis_not_evidence: emphasis increases discourse force, not evidence strength")
            return InResolutionResult("إنّ", "inna_emphasis", op, 0.92, warnings)

        tokens = text_stripped.split()
        in_idx = next((i for i, t in enumerate(tokens) if t in ("إن", "إِن")), None)

        if in_idx is None:
            warnings.append("إن not found; defaulting to conditional")
            op = _make_in_op(
                "إن", MabniType.conditional, LogicalFunction.condition, PragmaticFunction.assertion,
                False, True, CertaintyEffect.suspend, "IN_CON_001"
            )
            return InResolutionResult("إن", "in_conditional", op, 0.4, warnings)

        next_tok = tokens[in_idx + 1] if in_idx + 1 < len(tokens) else ""

        # إن النافية — followed by إلا or negation context
        if "إلا" in text_stripped or next_tok in ("هذا", "هو", "هي", "هم") and "إلا" in text_stripped:
            op = _make_in_op(
                "إن", MabniType.negation, LogicalFunction.negation, PragmaticFunction.assertion,
                True, True, CertaintyEffect.lower, "IN_NEG_002"
            )
            return InResolutionResult("إن", "in_negative", op, 0.85)

        # إن المخففة — followed by لَ or negation context suggesting mukhaffafa
        if next_tok.startswith("ل") and len(next_tok) > 1:
            op = _make_in_op(
                "إن", MabniType.emphasis, LogicalFunction.emphasis, PragmaticFunction.assertion,
                False, True, CertaintyEffect.emphasis_only, "IN_MUKH_005"
            )
            return InResolutionResult("إن", "in_mukhaffafa", op, 0.75)

        # Default: إن الشرطية (conditional)
        op = _make_in_op(
            "إن", MabniType.conditional, LogicalFunction.condition, PragmaticFunction.assertion,
            False, True, CertaintyEffect.suspend, "IN_CON_001"
        )
        return InResolutionResult("إن", "in_conditional", op, 0.8)
