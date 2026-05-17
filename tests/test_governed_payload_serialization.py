from __future__ import annotations

from mcd.core import (
    FIELD_AUDIT_SCHEMA_VERSION,
    FIELD_CONTRACT_VERSION,
    FIELD_GOVERNANCE_AUDIT,
    FIELD_GOVERNANCE_GATE_PASSED,
    FIELD_JUDGMENT,
    FIELD_PROOF_ID,
    FIELD_RAW_TEXT_UNITS,
    FIELD_RESIDUALS,
    FIELD_RESIDUAL_TAXONOMY_VERSION,
    FIELD_REVERSE_TRACE_OBJ,
    FIELD_SCHEMA_VERSION,
    GOVERNANCE_AUDIT_SCHEMA_VERSION,
    GOVERNED_PAYLOAD_SCHEMA_VERSION,
    JUDGMENT_CERTIFICATE,
    JUDGMENT_HYPOTHESIS,
    PUBLIC_FINAL_JUDGMENTS,
    RESIDUAL_TAXONOMY_SCHEMA_VERSION,
    deserialize_governed_payload,
    enforce_governed_output_contract,
    serialize_governed_payload,
    validate_governed_payload_schema,
)


def _certificate_payload() -> dict[str, object]:
    return {
        FIELD_PROOF_ID: "PO-ser",
        FIELD_JUDGMENT: JUDGMENT_CERTIFICATE,
        FIELD_GOVERNANCE_GATE_PASSED: True,
        FIELD_REVERSE_TRACE_OBJ: {
            "reverse_trace_id": "RT-ser",
            "complete": True,
            FIELD_RAW_TEXT_UNITS: ["النار حارة"],
        },
        FIELD_RESIDUALS: [],
    }


def test_valid_payload_round_trip_preserves_judgment_and_anchor():
    governed = enforce_governed_output_contract(_certificate_payload(), include_audit=True)
    serialized = serialize_governed_payload(governed)
    roundtrip = deserialize_governed_payload(serialized)

    assert roundtrip[FIELD_JUDGMENT] == JUDGMENT_CERTIFICATE
    assert roundtrip[FIELD_REVERSE_TRACE_OBJ][FIELD_RAW_TEXT_UNITS] == ["النار حارة"]
    assert roundtrip[FIELD_SCHEMA_VERSION] == GOVERNED_PAYLOAD_SCHEMA_VERSION
    assert roundtrip[FIELD_CONTRACT_VERSION] == GOVERNED_PAYLOAD_SCHEMA_VERSION


def test_certificate_payload_with_raw_text_units_stays_certificate_after_round_trip():
    roundtrip = deserialize_governed_payload(serialize_governed_payload(_certificate_payload()))
    assert roundtrip[FIELD_JUDGMENT] == JUDGMENT_CERTIFICATE


def test_missing_raw_text_units_after_deserialization_downgrades_certificate():
    payload = serialize_governed_payload(_certificate_payload())
    payload[FIELD_REVERSE_TRACE_OBJ][FIELD_RAW_TEXT_UNITS] = []
    roundtrip = deserialize_governed_payload(payload)

    assert roundtrip[FIELD_JUDGMENT] == JUDGMENT_HYPOTHESIS
    assert "serialization_missing_raw_text_units" in roundtrip[FIELD_RESIDUALS]


def test_governance_audit_is_preserved_with_versions_when_present():
    governed = enforce_governed_output_contract(_certificate_payload(), include_audit=True)
    serialized = serialize_governed_payload(governed)
    roundtrip = deserialize_governed_payload(serialized)

    assert FIELD_GOVERNANCE_AUDIT in roundtrip
    assert roundtrip[FIELD_GOVERNANCE_AUDIT][FIELD_AUDIT_SCHEMA_VERSION] == GOVERNANCE_AUDIT_SCHEMA_VERSION
    assert (
        roundtrip[FIELD_GOVERNANCE_AUDIT][FIELD_RESIDUAL_TAXONOMY_VERSION]
        == RESIDUAL_TAXONOMY_SCHEMA_VERSION
    )


def test_residual_taxonomy_metadata_is_preserved_when_present():
    payload = enforce_governed_output_contract(_certificate_payload(), include_audit=True)
    payload[FIELD_GOVERNANCE_AUDIT][FIELD_RESIDUAL_TAXONOMY_VERSION] = RESIDUAL_TAXONOMY_SCHEMA_VERSION

    roundtrip = deserialize_governed_payload(serialize_governed_payload(payload))
    assert (
        roundtrip[FIELD_GOVERNANCE_AUDIT][FIELD_RESIDUAL_TAXONOMY_VERSION]
        == RESIDUAL_TAXONOMY_SCHEMA_VERSION
    )


def test_unsupported_schema_version_blocks_certificate():
    payload = serialize_governed_payload(_certificate_payload())
    payload[FIELD_SCHEMA_VERSION] = "9.9"
    roundtrip = deserialize_governed_payload(payload)

    assert roundtrip[FIELD_JUDGMENT] == JUDGMENT_HYPOTHESIS
    assert "unsupported_schema_version" in roundtrip[FIELD_RESIDUALS]


def test_missing_schema_version_emits_validation_residual():
    payload = _certificate_payload()
    validation = validate_governed_payload_schema(payload)
    roundtrip = deserialize_governed_payload(payload)

    assert "missing_schema_version" in validation
    assert "missing_schema_version" in roundtrip[FIELD_RESIDUALS]


def test_final_judgment_triad_remains_unchanged():
    assert PUBLIC_FINAL_JUDGMENTS == ("zero", "hypothesis", "certificate")


def test_include_audit_false_remains_compatible():
    payload = deserialize_governed_payload(serialize_governed_payload(_certificate_payload()))
    assert FIELD_GOVERNANCE_AUDIT not in payload


def test_raw_text_units_remains_mandatory_for_certificate():
    payload = serialize_governed_payload(_certificate_payload())
    payload[FIELD_REVERSE_TRACE_OBJ] = {"reverse_trace_id": "RT-ser-missing", "complete": True, FIELD_RAW_TEXT_UNITS: []}

    roundtrip = deserialize_governed_payload(payload)
    assert roundtrip[FIELD_JUDGMENT] == JUDGMENT_HYPOTHESIS
