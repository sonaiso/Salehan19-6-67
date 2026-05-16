from __future__ import annotations

from mcd.core import GovernanceAuditEvent, classify_residuals, enforce_governed_output_contract
from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS
from mcd.core.public_schema import (
    FIELD_GOVERNANCE_AUDIT,
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


def _valid_certificate_payload() -> dict[str, object]:
    return {
        FIELD_PROOF_ID: "PO-api",
        FIELD_JUDGMENT: JUDGMENT_CERTIFICATE,
        FIELD_GOVERNANCE_GATE_PASSED: True,
        FIELD_REVERSE_TRACE_OBJ: {
            "reverse_trace_id": "RT-api",
            "complete": True,
            FIELD_RAW_TEXT_UNITS: ["النار حارة"],
        },
        FIELD_RESIDUALS: [],
    }


def test_include_audit_false_does_not_emit_governance_audit():
    payload = enforce_governed_output_contract(_valid_certificate_payload(), include_audit=False)
    assert FIELD_GOVERNANCE_AUDIT not in payload


def test_include_audit_true_emits_governance_audit():
    payload = enforce_governed_output_contract(_valid_certificate_payload(), include_audit=True)
    assert FIELD_GOVERNANCE_AUDIT in payload


def test_final_judgment_values_remain_public_triad_only():
    assert PUBLIC_FINAL_JUDGMENTS == (JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE)
    payload = enforce_governed_output_contract(
        {
            FIELD_JUDGMENT: "suspend",
            "kernel_judgment": "PASS",
            "final_judgment": "VALID",
            "proof_status": "UNKNOWN",
        }
    )
    assert payload[FIELD_JUDGMENT] in PUBLIC_FINAL_JUDGMENTS
    assert payload["kernel_judgment"] in PUBLIC_FINAL_JUDGMENTS
    assert payload["final_judgment"] in PUBLIC_FINAL_JUDGMENTS
    assert payload["proof_status"] in PUBLIC_FINAL_JUDGMENTS


def test_certificate_missing_raw_text_units_downgrades_to_hypothesis():
    payload = _valid_certificate_payload()
    payload[FIELD_REVERSE_TRACE_OBJ] = {"reverse_trace_id": "RT-missing", "complete": True, FIELD_RAW_TEXT_UNITS: []}
    governed = enforce_governed_output_contract(payload)
    assert governed[FIELD_JUDGMENT] == JUDGMENT_HYPOTHESIS


def test_certificate_with_unknown_residual_downgrades_to_hypothesis():
    payload = _valid_certificate_payload()
    payload[FIELD_RESIDUALS] = ["unknown_new_code"]
    governed = enforce_governed_output_contract(payload)
    assert governed[FIELD_JUDGMENT] == JUDGMENT_HYPOTHESIS


def test_valid_certificate_payload_remains_certificate():
    governed = enforce_governed_output_contract(_valid_certificate_payload())
    assert governed[FIELD_JUDGMENT] == JUDGMENT_CERTIFICATE


def test_governed_payload_preserves_stable_field_names():
    governed = enforce_governed_output_contract(
        {
            FIELD_PROOF_ID: "PO-stable",
            FIELD_PROOF_OBJECT_REF: "PO-REF-stable",
            FIELD_JUDGMENT: JUDGMENT_HYPOTHESIS,
            FIELD_GOVERNANCE_GATE_PASSED: True,
            FIELD_REVERSE_TRACE_REF: "RT-stable",
            FIELD_REVERSE_TRACE_OBJ: {"reverse_trace_id": "RT-stable", "complete": True, FIELD_RAW_TEXT_UNITS: ["x"]},
            FIELD_RESIDUALS: [],
        },
        include_audit=True,
    )
    assert FIELD_PROOF_ID in governed
    assert FIELD_PROOF_OBJECT_REF in governed
    assert FIELD_JUDGMENT in governed
    assert FIELD_GOVERNANCE_GATE_PASSED in governed
    assert FIELD_REVERSE_TRACE_REF in governed
    assert FIELD_REVERSE_TRACE_OBJ in governed
    assert FIELD_RESIDUALS in governed
    assert FIELD_GOVERNANCE_AUDIT in governed


def test_schema_constants_match_runtime_field_names():
    assert FIELD_PROOF_ID == "proof_id"
    assert FIELD_JUDGMENT == "judgment"
    assert FIELD_PROOF_OBJECT_REF == "proof_object_ref"
    assert FIELD_GOVERNANCE_GATE_PASSED == "governance_gate_passed"
    assert FIELD_REVERSE_TRACE_REF == "reverse_trace_ref"
    assert FIELD_REVERSE_TRACE_OBJ == "reverse_trace_obj"
    assert FIELD_RAW_TEXT_UNITS == "raw_text_units"
    assert FIELD_RESIDUALS == "residuals"
    assert FIELD_GOVERNANCE_AUDIT == "_governance_audit"


def test_classify_residuals_remains_importable_from_core_namespace():
    specs = classify_residuals(["certificate_allowed"])
    assert specs[0].code == "certificate_allowed"


def test_governance_audit_event_remains_importable_from_core_namespace():
    assert GovernanceAuditEvent.__name__ == "GovernanceAuditEvent"
