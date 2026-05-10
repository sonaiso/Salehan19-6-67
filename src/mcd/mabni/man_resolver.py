"""ManResolver — disambiguates the Arabic particle من."""
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
class ManResolutionResult:
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


def _make_man_op(mabni_type: MabniType, logical_function: LogicalFunction,
                 pragmatic_function: PragmaticFunction,
                 affects_evidence: bool, affects_certainty: bool,
                 certainty_effect: CertaintyEffect, operator_id: str) -> MabniOperator:
    return MabniOperator(
        operator_id=operator_id,
        surface="من",
        normalized="من",
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


class ManResolver:
    """Disambiguates من into: interrogative, relative, conditional, partitive,
    explanatory, inceptive."""

    def resolve(self, text: str, context: str = "") -> ManResolutionResult:
        text_stripped = text.strip()
        warnings: list[str] = []

        # Interrogative — followed by question mark or clearly asking about person
        if "؟" in text_stripped or text_stripped.startswith("من ") and len(text_stripped.split()) <= 3:
            op = _make_man_op(
                MabniType.interrogative, LogicalFunction.speech_act, PragmaticFunction.question,
                False, True, CertaintyEffect.suspend, "MAN_INT_001"
            )
            return ManResolutionResult("من", "interrogative", op, 0.9)

        # Conditional — من يفعل شيئاً pattern (generic person → habitual)
        tokens = text_stripped.split()
        man_idx = next((i for i, t in enumerate(tokens) if t == "من"), None)
        if man_idx is not None:
            next_tok = tokens[man_idx + 1] if man_idx + 1 < len(tokens) else ""
            # Conditional: من يجتهد ينجح
            if next_tok.startswith("ي") or next_tok.startswith("ت"):
                # Check for apodosis (second verb)
                remaining = tokens[man_idx + 2:]
                if remaining:
                    op = _make_man_op(
                        MabniType.conditional, LogicalFunction.condition, PragmaticFunction.assertion,
                        False, True, CertaintyEffect.suspend, "MAN_CON_004"
                    )
                    return ManResolutionResult("من", "conditional", op, 0.8)

        # Preposition — preceded by verb of motion, coming from
        motion_verbs = {"جاء", "خرج", "أتى", "وصل", "قدم", "أخذ", "أتى"}
        if man_idx and man_idx > 0 and tokens[man_idx - 1] in motion_verbs:
            op = _make_man_op(
                MabniType.preposition, LogicalFunction.relation, PragmaticFunction.assertion,
                False, False, CertaintyEffect.none, "MAN_PREP_003"
            )
            return ManResolutionResult("من", "partitive", op, 0.85)

        # Partitive preposition — من + noun (no verb context)
        if man_idx is not None and man_idx + 1 < len(tokens):
            op = _make_man_op(
                MabniType.preposition, LogicalFunction.relation, PragmaticFunction.assertion,
                False, False, CertaintyEffect.none, "MAN_PREP_003"
            )
            return ManResolutionResult("من", "partitive", op, 0.7)

        # Relative — default
        warnings.append("defaulting to relative من; context may refine")
        op = _make_man_op(
            MabniType.relative, LogicalFunction.reference, PragmaticFunction.assertion,
            False, False, CertaintyEffect.none, "MAN_REL_002"
        )
        return ManResolutionResult("من", "relative", op, 0.5, warnings)
