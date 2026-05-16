"""Canonical public final-judgment contract utilities."""
from __future__ import annotations

from copy import deepcopy
from typing import Any
from collections.abc import Iterator

from mcd.core.governance_audit import build_governance_audit_event

PUBLIC_FINAL_JUDGMENTS: tuple[str, ...] = ("zero", "hypothesis", "certificate")
INTERNAL_SUSPEND = "suspend"
INTERNAL_SUSPENDED = "suspended"
_JUDGMENT_KEYS = frozenset({"judgment", "kernel_judgment", "final_judgment", "proof_status"})
_GOVERNANCE_CONTEXT_KEYS = frozenset(
    {
        "proof_id",
        "proof_object_ref",
        "governance_gate_passed",
        "conservation",
        "reverse_trace_ref",
        "reverse_trace_obj",
        "reverse_trace",
        "transition_tags",
    }
)
_BLOCKING_TRANSITIONS = frozenset(
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


def collapse_to_public_judgment(status: str) -> str:
    """Collapse internal/intermediate status to public triad."""
    normalized = (status or "").strip().lower()
    if normalized in PUBLIC_FINAL_JUDGMENTS:
        return normalized
    if normalized in {INTERNAL_SUSPEND, INTERNAL_SUSPENDED}:
        return "hypothesis"
    return "zero"


def is_public_final_judgment(status: str) -> bool:
    """Return True iff status is one of the canonical public judgments."""
    return (status or "").strip().lower() in PUBLIC_FINAL_JUDGMENTS


def normalize_public_judgment_fields(payload: Any) -> Any:
    """Recursively normalize all judgment fields across nested payload structures.

    Traverses dict/list/tuple containers and canonicalizes values of
    judgment keys (judgment/kernel_judgment/final_judgment/proof_status)
    into the public triad.
    """
    if isinstance(payload, dict):
        out: dict[Any, Any] = {}
        for key, value in payload.items():
            normalized_value = normalize_public_judgment_fields(value)
            if key in _JUDGMENT_KEYS and isinstance(normalized_value, str):
                out[key] = collapse_to_public_judgment(normalized_value)
            else:
                out[key] = normalized_value
        return out
    if isinstance(payload, list):
        return [normalize_public_judgment_fields(v) for v in payload]
    if isinstance(payload, tuple):
        return tuple(normalize_public_judgment_fields(v) for v in payload)
    return payload


def enforce_governed_output_contract(
    payload: dict[str, Any], *, include_audit: bool = False
) -> dict[str, Any]:
    """Enforce AFJG public-output rules on governed payloads.

    Rules applied to every nested dict node:
    - Normalize judgment fields into the canonical public triad
      (zero/hypothesis/certificate).
    - Collapse internal suspend/suspended state to public hypothesis.
    - Downgrade certificate when proof object, governance gate, or reverse trace
      requirements are missing.
    - Preserve existing residuals and append governance residual markers.
    """
    input_payload = deepcopy(payload)
    normalized = normalize_public_judgment_fields(deepcopy(payload))
    internal_suspension_applied = _enforce_internal_state_rule(normalized)
    certificate_reason_codes = _enforce_certificate_gate(normalized)
    for node in _iter_child_dict_nodes(normalized):
        _enforce_internal_state_rule(node)
        _enforce_certificate_gate(node)
    if include_audit:
        normalized["_governance_audit"] = build_governance_audit_event(
            input_payload=input_payload,
            output_payload=normalized,
            certificate_reason_codes=certificate_reason_codes,
            internal_suspension_applied=internal_suspension_applied,
        ).to_dict()
    return normalized


def _iter_dict_nodes(payload: Any) -> Iterator[dict[str, Any]]:
    """Yield every dict node inside nested dict/list payload structures."""
    if isinstance(payload, dict):
        yield payload
        for value in payload.values():
            yield from _iter_dict_nodes(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from _iter_dict_nodes(value)


def _iter_child_dict_nodes(payload: Any) -> Iterator[dict[str, Any]]:
    if not isinstance(payload, dict):
        return
    for value in payload.values():
        yield from _iter_dict_nodes(value)


def _enforce_internal_state_rule(payload: dict[str, Any]) -> bool:
    """Mutate payload in place: suspend/suspended internal state => hypothesis."""
    internal_state = str(payload.get("internal_state", "")).strip().lower()
    if internal_state not in {INTERNAL_SUSPEND, INTERNAL_SUSPENDED}:
        return False
    for key in ("judgment", "final_judgment", "proof_status"):
        if key in payload:
            payload[key] = "hypothesis"
    _append_residual(payload, "internal_suspension_collapsed")
    return True


def _enforce_certificate_gate(payload: dict[str, Any]) -> list[str]:
    if _is_reverse_trace_payload(payload):
        return []
    if not _has_governance_context(payload):
        return []
    keys_to_check = [
        key
        for key in ("judgment", "final_judgment", "proof_status")
        if isinstance(payload.get(key), str) and collapse_to_public_judgment(payload[key]) == "certificate"
    ]
    if not keys_to_check:
        return []
    blocked_reasons = _certificate_block_reasons(payload)
    for reason in dict.fromkeys(blocked_reasons):
        _append_residual(payload, reason)
    if blocked_reasons:
        for key in keys_to_check:
            payload[key] = "hypothesis"
    return blocked_reasons


def _has_governance_context(payload: dict[str, Any]) -> bool:
    return bool(payload.keys() & _GOVERNANCE_CONTEXT_KEYS)


def _is_reverse_trace_payload(payload: dict[str, Any]) -> bool:
    """Detect embedded reverse-trace snapshots that are not governed outputs.

    ReverseTrace payloads may carry `final_judgment` for trace bookkeeping, but
    they do not represent top-level governed certificate claims and should not
    be certificate-gated independently.
    """
    return (
        "reverse_trace_id" in payload
        and "complete" in payload
        and "governance_gate_passed" not in payload
        and "conservation" not in payload
        and "reverse_trace_ref" not in payload
    )


def _certificate_block_reasons(payload: dict[str, Any]) -> list[str]:
    blocked_reasons: list[str] = []

    proof_ref = payload.get("proof_id") or payload.get("proof_object_ref")
    if not proof_ref:
        blocked_reasons.append("certificate_without_proof_object")

    if "governance_gate_passed" in payload:
        if not bool(payload.get("governance_gate_passed")):
            blocked_reasons.append("certificate_without_governance_gate")
    else:
        conservation = payload.get("conservation")
        if isinstance(conservation, dict):
            if not bool(conservation.get("passed", False)):
                blocked_reasons.append("certificate_without_governance_gate")

    reverse_trace_ref = payload.get("reverse_trace_ref")
    reverse_trace_obj = payload.get("reverse_trace_obj")
    reverse_trace = payload.get("reverse_trace")
    has_reverse_trace = bool(reverse_trace_ref)
    if isinstance(reverse_trace_obj, dict):
        trace_complete = bool(reverse_trace_obj.get("complete", False))
        has_reverse_trace = has_reverse_trace or trace_complete
        if not trace_complete:
            blocked_reasons.append("certificate_without_reverse_trace")
        elif not bool(reverse_trace_obj.get("raw_text_units")):
            blocked_reasons.append("reverse_trace_missing_raw_text")
    if isinstance(reverse_trace, list):
        has_reverse_trace = has_reverse_trace or bool(reverse_trace)
    if not has_reverse_trace:
        blocked_reasons.append("certificate_without_reverse_trace")

    existing_residuals = payload.get("residuals")
    if isinstance(existing_residuals, list) and any(str(item).strip() for item in existing_residuals):
        blocked_reasons.append("certificate_with_blocking_residuals")

    transition_tags = payload.get("transition_tags")
    if isinstance(transition_tags, list):
        for tag in transition_tags:
            tag_normalized = str(tag).strip().lower()
            if tag_normalized in _BLOCKING_TRANSITIONS:
                blocked_reasons.append(tag_normalized)

    return blocked_reasons


def _append_residual(payload: dict[str, Any], residual: str) -> None:
    """Mutate payload by appending a non-empty residual marker once."""
    existing = payload.get("residuals")
    residuals: list[str]
    if isinstance(existing, list):
        residuals = [str(item) for item in existing if str(item).strip()]
    else:
        residuals = []
    if residual not in residuals:
        residuals.append(residual)
    payload["residuals"] = residuals
