from __future__ import annotations

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO
from mcd.prompt_understanding.payload import (
    PROMPT_UNDERSTANDING_SCHEMA_VERSION,
    build_prompt_understanding_payload,
    deserialize_prompt_understanding_payload,
    enforce_prompt_understanding_contract,
    serialize_prompt_understanding_payload,
)


def test_clear_arabic_request_builds_governed_understanding_payload() -> None:
    payload = build_prompt_understanding_payload("اشرح الفكرة الأساسية")
    assert payload["raw_prompt"] == "اشرح الفكرة الأساسية"
    assert payload["inferred_intent"] == "explain_request"
    assert payload["task_type"] == "explanation"
    assert payload["understanding_rank"] in {JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE}


def test_continuation_request_maps_task_type() -> None:
    payload = build_prompt_understanding_payload("اكمل")
    assert payload["task_type"] == "continuation"
    assert payload["inferred_intent"] == "continuation_request"


def test_ambiguous_prompt_downgrades_to_hypothesis() -> None:
    payload = build_prompt_understanding_payload("شيء ما")
    assert "prompt_intent_ambiguous" in payload["residuals"]
    assert payload["understanding_rank"] == JUDGMENT_HYPOTHESIS


def test_missing_raw_prompt_blocks_certificate() -> None:
    payload = enforce_prompt_understanding_contract(
        {
            "prompt_understanding_schema_version": PROMPT_UNDERSTANDING_SCHEMA_VERSION,
            "prompt_understanding_contract_version": "1.0.0",
            "raw_prompt": "",
            "normalized_prompt": "",
            "reverse_trace": {"anchors": []},
            "residuals": [],
            "understanding_rank": JUDGMENT_CERTIFICATE,
        }
    )
    assert payload["understanding_rank"] != JUDGMENT_CERTIFICATE
    assert "prompt_missing_raw_text" in payload["residuals"]


def test_missing_trace_anchors_blocks_certificate() -> None:
    payload = enforce_prompt_understanding_contract(
        {
            "prompt_understanding_schema_version": PROMPT_UNDERSTANDING_SCHEMA_VERSION,
            "prompt_understanding_contract_version": "1.0.0",
            "raw_prompt": "اشرح",
            "normalized_prompt": "اشرح",
            "inferred_intent": "explain_request",
            "task_type": "explanation",
            "reverse_trace": {"anchors": []},
            "residuals": [],
            "understanding_rank": JUDGMENT_CERTIFICATE,
        }
    )
    assert payload["understanding_rank"] != JUDGMENT_CERTIFICATE
    assert "prompt_missing_trace_anchors" in payload["residuals"]


def test_missing_task_type_blocks_certificate() -> None:
    payload = enforce_prompt_understanding_contract(
        {
            "prompt_understanding_schema_version": PROMPT_UNDERSTANDING_SCHEMA_VERSION,
            "prompt_understanding_contract_version": "1.0.0",
            "raw_prompt": "اختبر",
            "normalized_prompt": "اختبر",
            "inferred_intent": "generic_request",
            "task_type": "",
            "reverse_trace": {"anchors": [{"start": 0, "end": 4, "text": "اختبر"}]},
            "residuals": [],
            "understanding_rank": JUDGMENT_CERTIFICATE,
        }
    )
    assert payload["understanding_rank"] != JUDGMENT_CERTIFICATE
    assert "prompt_task_type_missing" in payload["residuals"]


def test_unsupported_schema_version_blocks_certificate() -> None:
    payload = enforce_prompt_understanding_contract(
        {
            "prompt_understanding_schema_version": "9.9.9",
            "prompt_understanding_contract_version": "1.0.0",
            "raw_prompt": "اشرح",
            "normalized_prompt": "اشرح",
            "inferred_intent": "explain_request",
            "task_type": "explanation",
            "reverse_trace": {"anchors": [{"start": 0, "end": 4, "text": "اشرح"}]},
            "residuals": [],
            "understanding_rank": JUDGMENT_CERTIFICATE,
        }
    )
    assert payload["understanding_rank"] != JUDGMENT_CERTIFICATE
    assert "unsupported_prompt_understanding_schema_version" in payload["residuals"]


def test_deserialize_cannot_upgrade_hypothesis_to_certificate() -> None:
    raw = build_prompt_understanding_payload("اشرح بإيجاز")
    raw["understanding_rank"] = JUDGMENT_HYPOTHESIS
    raw["inferred_intent"] = "explain_request"
    raw["task_type"] = "explanation"
    roundtripped = deserialize_prompt_understanding_payload(raw)
    assert roundtripped["understanding_rank"] in {JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS}


def test_serialization_roundtrip_preserves_or_downgrades_rank_only() -> None:
    payload = build_prompt_understanding_payload("اشرح المثال")
    serialized = serialize_prompt_understanding_payload(payload)
    deserialized = deserialize_prompt_understanding_payload(serialized)
    order = {JUDGMENT_ZERO: 0, JUDGMENT_HYPOTHESIS: 1, JUDGMENT_CERTIFICATE: 2}
    assert order[deserialized["understanding_rank"]] <= order[payload["understanding_rank"]]


def test_residuals_are_non_erasing() -> None:
    payload = build_prompt_understanding_payload("اشرح")
    payload["residuals"] = ["prompt_domain_ambiguous"]
    enforced = enforce_prompt_understanding_contract(payload)
    assert "prompt_domain_ambiguous" in enforced["residuals"]


def test_non_governed_dict_shape_is_unchanged_by_prompt_serializer() -> None:
    payload = {"hello": "world"}
    serialized = serialize_prompt_understanding_payload(payload)
    assert serialized == payload
    assert "prompt_understanding_schema_version" not in serialized

