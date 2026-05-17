"""Governed payload serialization helpers with schema-version safeguards."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from mcd.core.public_judgment import enforce_governed_output_contract
from mcd.core.public_schema import (
    FIELD_AUDIT_SCHEMA_VERSION,
    FIELD_CONTRACT_VERSION,
    FIELD_GOVERNANCE_AUDIT,
    FIELD_JUDGMENT,
    FIELD_RAW_TEXT_UNITS,
    FIELD_RESIDUALS,
    FIELD_RESIDUAL_TAXONOMY_VERSION,
    FIELD_REVERSE_TRACE_OBJ,
    FIELD_SCHEMA_VERSION,
    GOVERNANCE_AUDIT_SCHEMA_VERSION,
    GOVERNED_PAYLOAD_SCHEMA_VERSION,
    JUDGMENT_CERTIFICATE,
    RESIDUAL_TAXONOMY_SCHEMA_VERSION,
)

_SUPPORTED_SCHEMA_VERSIONS = frozenset({GOVERNED_PAYLOAD_SCHEMA_VERSION})


def serialize_governed_payload(payload: dict) -> dict:
    """Return a governed payload with explicit serialization versions."""
    serialized = deepcopy(payload)
    serialized.setdefault(FIELD_SCHEMA_VERSION, GOVERNED_PAYLOAD_SCHEMA_VERSION)
    serialized.setdefault(FIELD_CONTRACT_VERSION, GOVERNED_PAYLOAD_SCHEMA_VERSION)
    audit = serialized.get(FIELD_GOVERNANCE_AUDIT)
    if isinstance(audit, dict):
        audit.setdefault(FIELD_AUDIT_SCHEMA_VERSION, GOVERNANCE_AUDIT_SCHEMA_VERSION)
        audit.setdefault(FIELD_RESIDUAL_TAXONOMY_VERSION, RESIDUAL_TAXONOMY_SCHEMA_VERSION)
    return serialized


def validate_governed_payload_schema(payload: dict) -> list[str]:
    """Validate version/certificate anchors for governed payload deserialization."""
    if not isinstance(payload, dict):
        return ["serialization_payload_invalid"]
    residuals: list[str] = []
    schema_version = payload.get(FIELD_SCHEMA_VERSION)
    if not isinstance(schema_version, str) or not schema_version.strip():
        residuals.append("missing_schema_version")
    elif schema_version.strip() not in _SUPPORTED_SCHEMA_VERSIONS:
        residuals.append("unsupported_schema_version")

    if str(payload.get(FIELD_JUDGMENT, "")).strip().lower() == JUDGMENT_CERTIFICATE:
        reverse_trace_obj = payload.get(FIELD_REVERSE_TRACE_OBJ)
        if isinstance(reverse_trace_obj, dict) and not bool(reverse_trace_obj.get(FIELD_RAW_TEXT_UNITS)):
            residuals.append("serialization_missing_raw_text_units")
    return residuals


def deserialize_governed_payload(payload: dict) -> dict:
    """Deserialize a governed payload while preventing unsafe judgment upgrades."""
    if not isinstance(payload, dict):
        return {
            FIELD_JUDGMENT: "zero",
            FIELD_RESIDUALS: ["serialization_payload_invalid"],
            FIELD_SCHEMA_VERSION: GOVERNED_PAYLOAD_SCHEMA_VERSION,
            FIELD_CONTRACT_VERSION: GOVERNED_PAYLOAD_SCHEMA_VERSION,
        }
    deserialized = deepcopy(payload)
    schema_residuals = validate_governed_payload_schema(deserialized)
    existing_residuals = deserialized.get(FIELD_RESIDUALS)
    if isinstance(existing_residuals, list):
        normalized_residuals = [code for item in existing_residuals if (code := str(item).strip())]
    else:
        normalized_residuals = []
    for code in schema_residuals:
        if code not in normalized_residuals:
            normalized_residuals.append(code)
    deserialized[FIELD_RESIDUALS] = normalized_residuals
    governed = enforce_governed_output_contract(deserialized, include_audit=False)
    governed.setdefault(FIELD_CONTRACT_VERSION, GOVERNED_PAYLOAD_SCHEMA_VERSION)
    audit = governed.get(FIELD_GOVERNANCE_AUDIT)
    if isinstance(audit, dict):
        audit.setdefault(FIELD_AUDIT_SCHEMA_VERSION, GOVERNANCE_AUDIT_SCHEMA_VERSION)
        audit.setdefault(FIELD_RESIDUAL_TAXONOMY_VERSION, RESIDUAL_TAXONOMY_SCHEMA_VERSION)
    return governed
