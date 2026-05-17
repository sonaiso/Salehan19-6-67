from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from mcd.core.public_schema import JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO


@dataclass(frozen=True)
class TransitionFailure:
    layer_from: str
    layer_to: str
    missing_gate: str
    residual_type: str
    evidence: list[str] = field(default_factory=list)
    rank: str = JUDGMENT_HYPOTHESIS


def locate_broken_transition(
    *,
    residual_codes: Sequence[str],
    evidence: Sequence[str] | None = None,
    context: dict[str, Any] | None = None,
) -> TransitionFailure:
    codes = {str(code).strip() for code in residual_codes if str(code).strip()}
    ev = [str(item).strip() for item in (evidence or []) if str(item).strip()]
    ctx = dict(context or {})

    if "missing_quantitative_operator" in codes or "no_quantity_extractor" in codes:
        return TransitionFailure(
            layer_from="PromptUnderstanding",
            layer_to="QuantityExtraction",
            missing_gate="quantity_extraction_gate",
            residual_type="missing_quantitative_operator",
            evidence=ev,
            rank=JUDGMENT_HYPOTHESIS,
        )

    layer_from = str(ctx.get("layer_from") or "PromptUnderstanding").strip()
    layer_to = str(ctx.get("layer_to") or "TaskClassification").strip()
    missing_gate = str(ctx.get("missing_gate") or "transition_gate_missing").strip()
    residual_type = str(ctx.get("residual_type") or "operator_contract_invalid").strip()

    return TransitionFailure(
        layer_from=layer_from,
        layer_to=layer_to,
        missing_gate=missing_gate,
        residual_type=residual_type,
        evidence=ev,
        rank=JUDGMENT_ZERO if not ev else JUDGMENT_HYPOTHESIS,
    )
