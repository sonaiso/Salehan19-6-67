"""Adapters for llm_proposer governed/public payload conversions."""
from __future__ import annotations

from typing import Any

from mcd.core.public_judgment import enforce_governed_output_contract
from mcd.core.public_schema import (
    FIELD_GOVERNANCE_GATE_PASSED,
    FIELD_JUDGMENT,
    FIELD_PROOF_OBJECT_REF,
    FIELD_RESIDUALS,
    FIELD_REVERSE_TRACE_OBJ,
)
from mcd.llm_proposer.types import GovernedAnswer, Proposal
from mcd.llm_proposer.verdict_mapping import public_judgment_to_verdict, verdict_to_public_judgment


def to_governed_payload(
    answer: GovernedAnswer,
    *,
    governance_gate_passed: bool,
    proof_object_ref: str,
    reverse_trace_obj: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        FIELD_JUDGMENT: verdict_to_public_judgment(answer.verdict),
        "verdict": answer.verdict,
        "evidence": list(answer.evidence),
        "reverse_trace": list(answer.reverse_trace),
        FIELD_RESIDUALS: list(answer.violated_rules),
        FIELD_PROOF_OBJECT_REF: proof_object_ref,
        FIELD_GOVERNANCE_GATE_PASSED: governance_gate_passed,
        "proposal": {
            "prompt": answer.proposal.prompt,
            "raw_text": answer.proposal.raw_text,
            "provider": answer.proposal.provider,
            "model": answer.proposal.model,
            "metadata": dict(answer.proposal.metadata),
        },
    }
    if reverse_trace_obj is not None:
        payload[FIELD_REVERSE_TRACE_OBJ] = reverse_trace_obj
    return enforce_governed_output_contract(payload)


def from_governed_payload(payload: dict[str, Any], *, proposal: Proposal) -> GovernedAnswer:
    judgment = str(payload.get(FIELD_JUDGMENT, ""))
    verdict = public_judgment_to_verdict(judgment)
    evidence = list(payload.get("evidence", []))
    reverse_trace = [str(item) for item in list(payload.get("reverse_trace", []))]
    residuals = [str(item) for item in list(payload.get(FIELD_RESIDUALS, []))]
    return GovernedAnswer(
        proposal=proposal,
        verdict=verdict,  # type: ignore[arg-type]
        evidence=evidence,
        reverse_trace=reverse_trace,
        violated_rules=residuals,
    )
