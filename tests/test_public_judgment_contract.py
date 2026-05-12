from __future__ import annotations

import json

from mcd.api.serializers import safe_serialize
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.cfk.serializers import cfk_result_to_json, proof_to_json


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

