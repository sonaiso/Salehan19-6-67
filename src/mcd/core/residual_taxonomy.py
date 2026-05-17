"""Typed residual taxonomy for governed observability and certificate gating."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class ResidualSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    SUSPENDER = "suspender"
    BLOCKER = "blocker"


class ResidualFamily(str, Enum):
    SOUND = "sound"
    SYLLABLE = "syllable"
    GATE = "gate"
    ROOT = "root"
    AUGMENTATION = "augmentation"
    JAMID = "jamid"
    WAZN = "wazn"
    SEMANTIC_TRANSFER = "semantic_transfer"
    CONTEXT = "context"
    WITNESS = "witness"
    REVERSE_TRACE = "reverse_trace"
    GOVERNANCE = "governance"
    CERTIFICATE = "certificate"
    TRANSITION = "transition"
    SERIALIZATION = "serialization"
    PROMPT_UNDERSTANDING = "prompt_understanding"
    FRACTAL_OPERATOR = "fractal_operator"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ResidualSpec:
    code: str
    family: ResidualFamily
    severity: ResidualSeverity
    blocks_certificate: bool
    default_message: str
    remediation_hint: str | None = None


_RESIDUAL_REGISTRY: dict[str, ResidualSpec] = {
    "transition_condition_unknown": ResidualSpec(
        code="transition_condition_unknown",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.SUSPENDER,
        blocks_certificate=True,
        default_message="Transition condition could not be determined.",
        remediation_hint="Provide explicit transition markers or fallback rule.",
    ),
    "transition_condition_failed": ResidualSpec(
        code="transition_condition_failed",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Transition condition evaluated to failed.",
        remediation_hint="Re-examine Φ path constraints for this transition.",
    ),
    "phi_transition_condition_unknown": ResidualSpec(
        code="phi_transition_condition_unknown",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.SUSPENDER,
        blocks_certificate=True,
        default_message="Φ transition condition could not be determined.",
        remediation_hint="Provide explicit Φ transition markers or fallback rule.",
    ),
    "phi_transition_condition_failed": ResidualSpec(
        code="phi_transition_condition_failed",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Φ transition condition evaluated to failed.",
        remediation_hint="Re-examine Φ path constraints for this transition.",
    ),
    "certificate_without_reverse_trace": ResidualSpec(
        code="certificate_without_reverse_trace",
        family=ResidualFamily.REVERSE_TRACE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Certificate lacks Ω reverse trace.",
        remediation_hint="Anchor certificate to raw_text_units via reverse trace.",
    ),
    "reverse_trace_missing": ResidualSpec(
        code="reverse_trace_missing",
        family=ResidualFamily.REVERSE_TRACE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Reverse trace is absent.",
        remediation_hint="Generate reverse_trace from Ω to raw_text_units.",
    ),
    "reverse_trace_missing_raw_text": ResidualSpec(
        code="reverse_trace_missing_raw_text",
        family=ResidualFamily.REVERSE_TRACE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Reverse trace not anchored to raw_text_units.",
        remediation_hint="Ensure Ω nodes link to verifiable raw_text_units.",
    ),
    "certificate_without_proof_object": ResidualSpec(
        code="certificate_without_proof_object",
        family=ResidualFamily.CERTIFICATE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Certificate issued without ProofObject.",
        remediation_hint="Attach ProofObject before certificate emission.",
    ),
    "certificate_without_governance_gate": ResidualSpec(
        code="certificate_without_governance_gate",
        family=ResidualFamily.GOVERNANCE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Certificate bypassed GovernanceGate.",
        remediation_hint="Run GovernanceGate and record pass/fail explicitly.",
    ),
    "certificate_with_blocking_residuals": ResidualSpec(
        code="certificate_with_blocking_residuals",
        family=ResidualFamily.CERTIFICATE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Blocking residuals remain unresolved.",
        remediation_hint="Resolve blocker-level residuals before certification.",
    ),
    "silent_level_skip": ResidualSpec(
        code="silent_level_skip",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.SUSPENDER,
        blocks_certificate=True,
        default_message="A level was silently skipped without justification.",
        remediation_hint="Document skip rationale or fill the missing level.",
    ),
    "forbidden_transition_marker": ResidualSpec(
        code="forbidden_transition_marker",
        family=ResidualFamily.TRANSITION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Transition contains a forbidden marker.",
        remediation_hint="Use an allowed governed transition path.",
    ),
    "certificate_blocked": ResidualSpec(
        code="certificate_blocked",
        family=ResidualFamily.CERTIFICATE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Certificate explicitly blocked by policy.",
        remediation_hint="Review policy rule triggering the block.",
    ),
    "missing_phi_reverse_edge": ResidualSpec(
        code="missing_phi_reverse_edge",
        family=ResidualFamily.GOVERNANCE,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Φ path lacks reverse edge for traceability.",
        remediation_hint="Add reverse edge in Φ executable contract.",
    ),
    "internal_suspension_collapsed": ResidualSpec(
        code="internal_suspension_collapsed",
        family=ResidualFamily.GOVERNANCE,
        severity=ResidualSeverity.SUSPENDER,
        blocks_certificate=True,
        default_message="Internal suspension was collapsed to public hypothesis.",
        remediation_hint="Inspect internal_state suspension source and supporting evidence.",
    ),
    "unsupported_schema_version": ResidualSpec(
        code="unsupported_schema_version",
        family=ResidualFamily.SERIALIZATION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Payload schema version is unsupported.",
        remediation_hint="Migrate payload to a supported schema version.",
    ),
    "missing_schema_version": ResidualSpec(
        code="missing_schema_version",
        family=ResidualFamily.SERIALIZATION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Payload schema version is missing.",
        remediation_hint="Emit schema_version in governed payloads before serialization.",
    ),
    "serialization_missing_raw_text_units": ResidualSpec(
        code="serialization_missing_raw_text_units",
        family=ResidualFamily.SERIALIZATION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Serialized certificate payload lost raw_text_units anchor.",
        remediation_hint="Preserve reverse_trace_obj.raw_text_units during round-trip.",
    ),
    "serialization_payload_invalid": ResidualSpec(
        code="serialization_payload_invalid",
        family=ResidualFamily.SERIALIZATION,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Serialized payload is invalid.",
        remediation_hint="Serialize and deserialize only governed payload dictionaries.",
    ),
    "certificate_allowed": ResidualSpec(
        code="certificate_allowed",
        family=ResidualFamily.CERTIFICATE,
        severity=ResidualSeverity.INFO,
        blocks_certificate=False,
        default_message="Certificate gates passed.",
        remediation_hint=None,
    ),
    "missing_prompt_understanding_schema_version": ResidualSpec(
        code="missing_prompt_understanding_schema_version",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt understanding payload is missing schema version.",
        remediation_hint="Add prompt_understanding_schema_version.",
    ),
    "unsupported_prompt_understanding_schema_version": ResidualSpec(
        code="unsupported_prompt_understanding_schema_version",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt understanding payload uses an unsupported schema version.",
        remediation_hint="Use a supported prompt_understanding_schema_version.",
    ),
    "prompt_missing_raw_text": ResidualSpec(
        code="prompt_missing_raw_text",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt understanding payload is missing raw prompt text.",
        remediation_hint="Provide raw_prompt before ranking understanding.",
    ),
    "prompt_missing_trace_anchors": ResidualSpec(
        code="prompt_missing_trace_anchors",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt understanding payload has no trace anchors.",
        remediation_hint="Anchor understanding outputs to raw prompt spans.",
    ),
    "prompt_intent_ambiguous": ResidualSpec(
        code="prompt_intent_ambiguous",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.WARNING,
        blocks_certificate=False,
        default_message="Prompt intent is ambiguous.",
        remediation_hint="Add context or clarify the user objective.",
    ),
    "prompt_task_type_missing": ResidualSpec(
        code="prompt_task_type_missing",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt task type could not be determined.",
        remediation_hint="Provide a supported task cue or explicit task_type.",
    ),
    "prompt_domain_ambiguous": ResidualSpec(
        code="prompt_domain_ambiguous",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.WARNING,
        blocks_certificate=False,
        default_message="Prompt domain is ambiguous.",
        remediation_hint="Provide explicit domain context when needed.",
    ),
    "prompt_understanding_payload_invalid": ResidualSpec(
        code="prompt_understanding_payload_invalid",
        family=ResidualFamily.PROMPT_UNDERSTANDING,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Prompt understanding payload structure is invalid.",
        remediation_hint="Validate required fields and field types.",
    ),
    "operator_missing_layer_mapping": ResidualSpec(
        code="operator_missing_layer_mapping",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Operator is missing layer_from or layer_to mapping.",
        remediation_hint="Declare exactly one typed transition Lᵢ → Lᵢ₊₁.",
    ),
    "operator_missing_gate": ResidualSpec(
        code="operator_missing_gate",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Operator contract is missing required gates.",
        remediation_hint="Declare missing_gate and non-empty gates.",
    ),
    "operator_forbidden_output": ResidualSpec(
        code="operator_forbidden_output",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Operator emits forbidden output for its local layer.",
        remediation_hint="Restrict output_type to the declared local transition.",
    ),
    "operator_missing_reverse_trace": ResidualSpec(
        code="operator_missing_reverse_trace",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Certificate-capable operator lacks reverse trace requirement.",
        remediation_hint="Set reverse_trace_required=True for certificate-capable operators.",
    ),
    "operator_multi_transition_forbidden": ResidualSpec(
        code="operator_multi_transition_forbidden",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Operator attempts to span multiple transitions.",
        remediation_hint="Bind operator to a single transition only.",
    ),
    "operator_contract_invalid": ResidualSpec(
        code="operator_contract_invalid",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Operator contract failed typed governance validation.",
        remediation_hint="Provide required typed fields and valid rank.",
    ),
    "transition_repair_missing_evidence": ResidualSpec(
        code="transition_repair_missing_evidence",
        family=ResidualFamily.FRACTAL_OPERATOR,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Transition repair candidate lacks evidence requirements.",
        remediation_hint="Declare concrete evidence requirements for the operator.",
    ),
    "unknown_residual": ResidualSpec(
        code="unknown_residual",
        family=ResidualFamily.UNKNOWN,
        severity=ResidualSeverity.BLOCKER,
        blocks_certificate=True,
        default_message="Unclassified residual encountered.",
        remediation_hint="Add residual to taxonomy or escalate to governance.",
    ),
}


def classify_residual(code: str) -> ResidualSpec:
    normalized = str(code or "").strip()
    if not normalized:
        return _RESIDUAL_REGISTRY["unknown_residual"]
    return _RESIDUAL_REGISTRY.get(
        normalized,
        ResidualSpec(
            code=normalized,
            family=ResidualFamily.UNKNOWN,
            severity=ResidualSeverity.BLOCKER,
            blocks_certificate=True,
            default_message=f"Unknown residual: {normalized}",
            remediation_hint="Classify this residual or treat it as blocker by default.",
        ),
    )


def classify_residuals(codes: Sequence[str]) -> list[ResidualSpec]:
    return [classify_residual(code) for code in codes]


def has_blocking_residuals(codes: Sequence[str]) -> bool:
    return any(spec.blocks_certificate for spec in classify_residuals(codes))


def blocking_residuals(codes: Sequence[str]) -> list[ResidualSpec]:
    return [spec for spec in classify_residuals(codes) if spec.blocks_certificate]
