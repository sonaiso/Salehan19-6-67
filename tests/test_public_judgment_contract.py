from __future__ import annotations

import json

from mcd.api.serializers import safe_serialize
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.cfk.serializers import cfk_result_to_json, proof_to_json
from mcd.core.public_judgment import enforce_governed_output_contract


def test_cfk_json_serializers_do_not_emit_suspend_publicly():
    result = CognitiveFractalPipeline().run("كل الشركات تستخدم هذه التقنية")
    payload = json.loads(cfk_result_to_json(result))
    assert payload["proof"]["judgment"] in {"zero", "hypothesis", "certificate"}
    assert payload["kernel"]["kernel_judgment"] in {"zero", "hypothesis", "certificate"}


def test_proof_serializer_collapses_suspend_to_hypothesis():
    result = CognitiveFractalPipeline().run("كل الشركات تستخدم هذه التقنية")
    payload = json.loads(proof_to_json(result.proof))
    assert payload["judgment"] in {"zero", "hypothesis", "certificate"}


def test_api_safe_serialize_collapses_judgment_fields():
    data = safe_serialize({"judgment": "suspend", "nested": {"final_judgment": "suspend"}})
    assert data["judgment"] == "hypothesis"
    assert data["nested"]["final_judgment"] == "hypothesis"


def test_internal_suspended_state_forces_public_hypothesis():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-1",
            "judgment": "certificate",
            "internal_state": "suspended",
            "conservation": {"passed": True},
            "reverse_trace_obj": {"complete": True},
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "internal_suspension_collapsed" in payload["residuals"]


def test_internal_suspended_state_collapses_even_when_gates_fail():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "",
            "judgment": "certificate",
            "internal_state": "suspended",
            "conservation": {"passed": False},
            "reverse_trace_obj": {"complete": False},
            "residuals": [],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "internal_suspension_collapsed" in payload["residuals"]


def test_certificate_without_gate_requirements_downgrades_and_preserves_residuals():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "",
            "judgment": "certificate",
            "conservation": {"passed": False},
            "reverse_trace_obj": {"complete": False},
            "residuals": ["baseline_residual"],
        }
    )
    assert payload["judgment"] == "hypothesis"
    assert "baseline_residual" in payload["residuals"]
    assert "certificate_without_proof_object" in payload["residuals"]
    assert "certificate_without_governance_gate" in payload["residuals"]
    assert "certificate_without_reverse_trace" in payload["residuals"]


def test_nested_reverse_trace_preserves_certificate():
    payload = enforce_governed_output_contract(
        {
            "proof_id": "PO-1",
            "judgment": "certificate",
            "conservation": {"passed": True},
            "reverse_trace_obj": {
                "final_judgment": "certificate",
                "reverse_trace_id": "RT-1",
                "complete": True,
            },
            "residuals": [],
        }
    )
    assert payload["judgment"] == "certificate"
    assert payload["reverse_trace_obj"]["final_judgment"] == "certificate"
    assert "residuals" not in payload["reverse_trace_obj"]
