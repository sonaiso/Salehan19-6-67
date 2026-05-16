from __future__ import annotations

from mcd.core.public_judgment import enforce_governed_output_contract


def _base_certificate_payload() -> dict[str, object]:
    return {
        "proof_id": "PO-audit",
        "judgment": "certificate",
        "governance_gate_passed": True,
        "reverse_trace_obj": {
            "reverse_trace_id": "RT-audit",
            "complete": True,
            "raw_text_units": ["النار حارة"],
        },
        "residuals": [],
    }


def test_certificate_allowed_emits_certificate_allowed_reason_code():
    payload = enforce_governed_output_contract(_base_certificate_payload(), include_audit=True)

    assert payload["judgment"] == "certificate"
    audit = payload["_governance_audit"]
    assert audit["decision"] == "allowed"
    assert audit["reason_codes"] == ["certificate_allowed"]


def test_missing_raw_text_units_emits_reverse_trace_missing_raw_text():
    payload = _base_certificate_payload()
    payload["reverse_trace_obj"] = {"reverse_trace_id": "RT-missing-raw", "complete": True, "raw_text_units": []}

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "reverse_trace_missing_raw_text" in governed["_governance_audit"]["reason_codes"]


def test_incomplete_reverse_trace_emits_certificate_without_reverse_trace():
    payload = _base_certificate_payload()
    payload["reverse_trace_obj"] = {
        "reverse_trace_id": "RT-incomplete",
        "complete": False,
        "raw_text_units": ["النار حارة"],
    }

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "certificate_without_reverse_trace" in governed["_governance_audit"]["reason_codes"]


def test_missing_proof_object_emits_certificate_without_proof_object():
    payload = _base_certificate_payload()
    payload["proof_id"] = ""

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "certificate_without_proof_object" in governed["_governance_audit"]["reason_codes"]


def test_missing_governance_gate_emits_certificate_without_governance_gate():
    payload = _base_certificate_payload()
    payload["governance_gate_passed"] = False

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "certificate_without_governance_gate" in governed["_governance_audit"]["reason_codes"]


def test_blocking_residual_emits_certificate_with_blocking_residuals():
    payload = _base_certificate_payload()
    payload["residuals"] = ["baseline_residual"]

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "certificate_with_blocking_residuals" in governed["_governance_audit"]["reason_codes"]


def test_silent_level_skip_emits_silent_level_skip():
    payload = _base_certificate_payload()
    payload["transition_tags"] = ["silent_level_skip"]

    governed = enforce_governed_output_contract(payload, include_audit=True)

    assert governed["judgment"] == "hypothesis"
    assert "silent_level_skip" in governed["_governance_audit"]["reason_codes"]


def test_include_audit_false_preserves_existing_behavior():
    payload = enforce_governed_output_contract(_base_certificate_payload())

    assert payload["judgment"] == "certificate"
    assert "_governance_audit" not in payload


def test_include_audit_true_adds_metadata_without_weakening_governance():
    payload = _base_certificate_payload()
    payload["proof_id"] = ""

    without_audit = enforce_governed_output_contract(payload)
    with_audit = enforce_governed_output_contract(payload, include_audit=True)

    assert without_audit["judgment"] == with_audit["judgment"] == "hypothesis"
    assert "_governance_audit" in with_audit
    assert "reason_codes" in with_audit["_governance_audit"]
    assert with_audit["_governance_audit"]["reason_codes"]


def test_transition_condition_reason_codes_normalize_to_phi_transition_codes():
    payload = enforce_governed_output_contract(
        {
            "judgment": "hypothesis",
            "residuals": ["transition_condition_failed"],
        },
        include_audit=True,
    )

    assert payload["_governance_audit"]["reason_codes"] == ["phi_transition_condition_failed"]
