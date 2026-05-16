"""Stable public governance API schema constants."""
from __future__ import annotations

GOVERNED_PAYLOAD_SCHEMA_VERSION = "1.0"
GOVERNANCE_AUDIT_SCHEMA_VERSION = "1.0"
RESIDUAL_TAXONOMY_SCHEMA_VERSION = "1.0"

FIELD_PROOF_ID = "proof_id"
FIELD_JUDGMENT = "judgment"
FIELD_PROOF_OBJECT_REF = "proof_object_ref"
FIELD_GOVERNANCE_GATE_PASSED = "governance_gate_passed"
FIELD_REVERSE_TRACE_REF = "reverse_trace_ref"
FIELD_REVERSE_TRACE_OBJ = "reverse_trace_obj"
FIELD_RAW_TEXT_UNITS = "raw_text_units"
FIELD_RESIDUALS = "residuals"
FIELD_SCHEMA_VERSION = "schema_version"
FIELD_CONTRACT_VERSION = "contract_version"
FIELD_AUDIT_SCHEMA_VERSION = "audit_schema_version"
FIELD_RESIDUAL_TAXONOMY_VERSION = "residual_taxonomy_version"
FIELD_GOVERNANCE_AUDIT = "_governance_audit"

JUDGMENT_ZERO = "zero"
JUDGMENT_HYPOTHESIS = "hypothesis"
JUDGMENT_CERTIFICATE = "certificate"
