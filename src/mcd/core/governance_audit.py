"""Governed audit-event model for Phase 1 observability."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal
from uuid import uuid4

from mcd.core.public_schema import (
    FIELD_GOVERNANCE_GATE_PASSED,
    FIELD_JUDGMENT,
    FIELD_PROOF_ID,
    FIELD_PROOF_OBJECT_REF,
    FIELD_RAW_TEXT_UNITS,
    FIELD_RESIDUALS,
    FIELD_REVERSE_TRACE_OBJ,
    FIELD_REVERSE_TRACE_REF,
    JUDGMENT_CERTIFICATE,
    JUDGMENT_HYPOTHESIS,
    JUDGMENT_ZERO,
)
from mcd.core.residual_taxonomy import classify_residuals, has_blocking_residuals

GovernanceDecision = Literal["allowed", "downgraded", "blocked", "suspended"]
GovernanceGate = Literal["phi", "omega", "proof_object", "governance_gate", "residuals", "certificate"]
_PUBLIC_FINAL_JUDGMENTS = frozenset({JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE})

REASON_CODE_ALIASES: dict[str, str] = {
    "transition_condition_unknown": "phi_transition_condition_unknown",
    "transition_condition_failed": "phi_transition_condition_failed",
}

KNOWN_REASON_CODES = frozenset(
    {
        "certificate_without_reverse_trace",
        "reverse_trace_missing_raw_text",
        "certificate_without_proof_object",
        "certificate_without_governance_gate",
        "certificate_with_blocking_residuals",
        "silent_level_skip",
        "forbidden_transition_marker",
        "phi_transition_condition_unknown",
        "phi_transition_condition_failed",
        "certificate_allowed",
    }
)

FORBIDDEN_TRANSITION_MARKERS = frozenset(
    {
        "root_or_pattern_as_factual_proof",
        "derivative_as_proof",
        "irab_as_factual_certainty",
        "emphasis_as_evidence",
        "metaphor_as_literal_certificate",
        "memory_as_external_evidence",
        "model_output_as_evidence",
        "tool_output_as_certificate_without_governance",
        "residual_erasure",
        "silent_level_skip",
        "certificate_without_proof_object",
        "certificate_without_governance_gate",
        "certificate_without_reverse_trace",
        "definition_as_judgment",
        "interpretation_as_evidence",
        "relation_as_inference",
        "dalala_without_gate",
        "invalid_semantic_transition",
    }
)


@dataclass(frozen=True)
class GovernanceAuditEvent:
    event_id: str
    proof_id: str | None
    input_judgment: str | None
    output_judgment: str
    decision: GovernanceDecision
    gate: GovernanceGate
    reason_codes: list[str]
    residuals: list[str]
    has_raw_text_anchor: bool
    has_reverse_trace: bool
    has_proof_object: bool
    governance_gate_passed: bool
    blocking_residuals_present: bool
    residual_families: list[str]
    residual_severities: list[str]
    blocking_residuals: list[str]
    remediation_hints: list[str]
    silent_level_skip_present: bool
    timestamp: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def normalize_reason_codes(reason_codes: list[str]) -> list[str]:
    normalized: list[str] = []
    saw_forbidden = False
    for reason in reason_codes:
        code = REASON_CODE_ALIASES.get(reason, reason)
        if code in FORBIDDEN_TRANSITION_MARKERS:
            saw_forbidden = True
        if code not in normalized:
            normalized.append(code)
    if saw_forbidden and "forbidden_transition_marker" not in normalized:
        normalized.append("forbidden_transition_marker")
    return normalized


def build_governance_audit_event(
    *,
    input_payload: dict[str, object],
    output_payload: dict[str, object],
    certificate_reason_codes: list[str],
    internal_suspension_applied: bool,
) -> GovernanceAuditEvent:
    proof_ref = _as_non_empty(input_payload.get(FIELD_PROOF_ID)) or _as_non_empty(input_payload.get(FIELD_PROOF_OBJECT_REF))
    input_judgment_raw = input_payload.get(FIELD_JUDGMENT)
    input_judgment = (
        _collapse_to_public_judgment(str(input_judgment_raw)) if isinstance(input_judgment_raw, str) else None
    )
    output_judgment = _collapse_to_public_judgment(str(output_payload.get(FIELD_JUDGMENT, "")))

    transition_tags = input_payload.get("transition_tags")
    silent_level_skip_present = isinstance(transition_tags, list) and any(
        str(tag).strip().lower() == "silent_level_skip" for tag in transition_tags
    )

    reverse_trace_obj = input_payload.get(FIELD_REVERSE_TRACE_OBJ)
    reverse_trace = input_payload.get("reverse_trace")
    reverse_trace_ref = input_payload.get(FIELD_REVERSE_TRACE_REF)
    has_raw_text_anchor = isinstance(reverse_trace_obj, dict) and bool(reverse_trace_obj.get(FIELD_RAW_TEXT_UNITS))
    has_reverse_trace = bool(reverse_trace_ref)
    if isinstance(reverse_trace_obj, dict):
        has_reverse_trace = has_reverse_trace or bool(reverse_trace_obj.get("complete", False))
    if isinstance(reverse_trace, list):
        has_reverse_trace = has_reverse_trace or bool(reverse_trace)

    has_proof_object = bool(proof_ref)
    governance_gate_passed = _governance_gate_passed(input_payload)

    existing_residuals = _normalize_residuals(input_payload.get(FIELD_RESIDUALS))
    blocking_residuals_present = has_blocking_residuals(existing_residuals)

    reason_codes = normalize_reason_codes(
        list(dict.fromkeys([*certificate_reason_codes, *existing_residuals]))
    )
    if output_judgment == JUDGMENT_CERTIFICATE and not reason_codes:
        reason_codes = ["certificate_allowed"]
    residual_specs = classify_residuals(reason_codes)

    decision = _derive_decision(
        input_judgment=input_judgment,
        output_judgment=output_judgment,
        reason_codes=reason_codes,
        internal_suspension_applied=internal_suspension_applied,
    )
    gate = _derive_gate(reason_codes)

    return GovernanceAuditEvent(
        event_id=f"GAE-{uuid4()}",
        proof_id=proof_ref,
        input_judgment=input_judgment,
        output_judgment=output_judgment,
        decision=decision,
        gate=gate,
        reason_codes=reason_codes,
        residuals=_normalize_residuals(output_payload.get(FIELD_RESIDUALS)),
        has_raw_text_anchor=has_raw_text_anchor,
        has_reverse_trace=has_reverse_trace,
        has_proof_object=has_proof_object,
        governance_gate_passed=governance_gate_passed,
        blocking_residuals_present=blocking_residuals_present,
        residual_families=[spec.family.value for spec in residual_specs],
        residual_severities=[spec.severity.value for spec in residual_specs],
        blocking_residuals=[spec.code for spec in residual_specs if spec.blocks_certificate],
        remediation_hints=list(
            dict.fromkeys(spec.remediation_hint for spec in residual_specs if spec.remediation_hint)
        ),
        silent_level_skip_present=silent_level_skip_present,
        timestamp=None,
    )


def _derive_decision(
    *,
    input_judgment: str | None,
    output_judgment: str,
    reason_codes: list[str],
    internal_suspension_applied: bool,
) -> GovernanceDecision:
    if internal_suspension_applied or "phi_transition_condition_unknown" in reason_codes:
        return "suspended"
    if input_judgment == JUDGMENT_CERTIFICATE and output_judgment != JUDGMENT_CERTIFICATE:
        return "downgraded"
    if output_judgment == JUDGMENT_ZERO or "phi_transition_condition_failed" in reason_codes:
        return "blocked"
    return "allowed"


def _derive_gate(reason_codes: list[str]) -> GovernanceGate:
    if any(code.startswith("phi_transition_") for code in reason_codes):
        return "phi"
    if any(
        code in {"certificate_without_reverse_trace", "reverse_trace_missing_raw_text"}
        for code in reason_codes
    ):
        return "omega"
    if "certificate_without_proof_object" in reason_codes:
        return "proof_object"
    if "certificate_without_governance_gate" in reason_codes:
        return "governance_gate"
    if "certificate_with_blocking_residuals" in reason_codes:
        return "residuals"
    return "certificate"


def _governance_gate_passed(payload: dict[str, object]) -> bool:
    if FIELD_GOVERNANCE_GATE_PASSED in payload:
        return bool(payload.get(FIELD_GOVERNANCE_GATE_PASSED))
    conservation = payload.get("conservation")
    if isinstance(conservation, dict):
        return bool(conservation.get("passed", False))
    return False


def _as_non_empty(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalize_residuals(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [code for item in raw if (code := str(item).strip())]


def _collapse_to_public_judgment(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized in _PUBLIC_FINAL_JUDGMENTS:
        return normalized
    if normalized in {"suspend", "suspended"}:
        return JUDGMENT_HYPOTHESIS
    return JUDGMENT_ZERO
