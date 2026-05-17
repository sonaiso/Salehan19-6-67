"""Tests for Phase 3B-1 — governed Arabic quantity mention extraction."""
from __future__ import annotations

import pytest

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO
from mcd.core.residual_taxonomy import (
    ResidualFamily,
    ResidualSeverity,
    classify_residual,
)
from mcd.fractal_learning import (
    FractalOperatorRegistry,
    OperatorChainCandidate,
    OperatorCompositionContract,
    OperatorContract,
    TypedOperatorCandidate,
    validate_operator_chain,
)
from mcd.quantity_extraction import (
    QUANTITY_EXTRACTION_OPERATOR_ID,
    QuantityMention,
    build_quantity_extraction_operator_contract,
    build_quantity_extraction_payload,
    deserialize_quantity_extraction_payload,
    extract_quantity_mentions,
    serialize_quantity_extraction_payload,
    validate_quantity_extraction_payload,
)


# ---------------------------------------------------------------------------
# Extraction behaviour
# ---------------------------------------------------------------------------

def _find(mentions, *, normalized_value=None, unit_normalized=None) -> QuantityMention:
    for mention in mentions:
        if normalized_value is not None and mention.normalized_value != normalized_value:
            continue
        if unit_normalized is not None and mention.unit_normalized != unit_normalized:
            continue
        return mention
    raise AssertionError(
        f"No mention with normalized_value={normalized_value}, unit={unit_normalized}: {mentions}"
    )


def test_extracts_arabic_indic_distance():
    mentions = extract_quantity_mentions("المسافة ٢٨ كيلو فقط")
    mention = _find(mentions, normalized_value=28.0, unit_normalized="km")
    assert mention.value == 28
    assert mention.unit_raw == "كيلو"
    assert mention.unit_normalized == "km"
    assert "٢٨" in mention.raw_text
    assert "كيلو" in mention.raw_text


def test_extracts_arabic_number_word_minutes():
    mentions = extract_quantity_mentions("لدينا عشرة دقائق فقط")
    mention = _find(mentions, normalized_value=10.0, unit_normalized="minute")
    assert mention.value == 10
    assert mention.unit_raw == "دقائق"
    assert mention.raw_text == "عشرة دقائق"


def test_extracts_compound_speed_unit():
    mentions = extract_quantity_mentions("الحد ٦٠ كم بالساعة هنا")
    mention = _find(mentions, normalized_value=60.0, unit_normalized="km_per_hour")
    assert mention.unit_normalized == "km_per_hour"
    assert mention.unit_raw == "كم بالساعة"
    assert mention.raw_text == "٦٠ كم بالساعة"


def test_extracts_slash_compound_speed_unit():
    mentions = extract_quantity_mentions("سرعتك ١٦٨ كم/ساعة")
    mention = _find(mentions, normalized_value=168.0, unit_normalized="km_per_hour")
    assert mention.unit_normalized == "km_per_hour"


def test_preserves_raw_spans_for_each_quantity():
    prompt = "٢٨ كم خلال ١٠ دقائق"
    mentions = extract_quantity_mentions(prompt)
    assert len(mentions) >= 2
    for mention in mentions:
        assert prompt[mention.span_start:mention.span_end] == mention.raw_text
        assert mention.trace_anchor["start"] == mention.span_start
        assert mention.trace_anchor["end"] == mention.span_end
        assert mention.trace_anchor["text"] == mention.raw_text
        assert mention.trace_anchor["label"] == "quantity_mention_span"


def test_airport_scale_prompt_only_yields_mentions_no_judgment():
    prompt = "أريد قطع ٢٨ كم في عشرة دقائق والحد ٦٠ كم بالساعة"
    mentions = extract_quantity_mentions(prompt)

    # Three mentions must be present.
    _find(mentions, normalized_value=28.0, unit_normalized="km")
    _find(mentions, normalized_value=10.0, unit_normalized="minute")
    _find(mentions, normalized_value=60.0, unit_normalized="km_per_hour")

    # And every mention must remain a non-final hypothesis-level artifact.
    for mention in mentions:
        assert mention.rank == JUDGMENT_HYPOTHESIS
        as_dict = mention.to_dict()
        for forbidden in {"judgment", "certificate", "final_answer", "feasibility"}:
            assert forbidden not in {str(k).lower() for k in as_dict.keys()}


def test_extractor_emits_no_feasibility_or_final_judgment():
    payload = build_quantity_extraction_payload("٢٨ كم في ١٠ دقائق والحد ٦٠ كم بالساعة")
    assert payload["rank"] == JUDGMENT_HYPOTHESIS
    for forbidden_key in (
        "feasibility",
        "judgment",
        "certificate",
        "final_answer",
        "answer",
    ):
        assert forbidden_key not in payload


def test_extractor_does_not_emit_zero_or_certificate_for_airport_problem():
    payload = build_quantity_extraction_payload("أريد قطع ٢٨ كم في ١٠ دقائق")
    assert payload["rank"] not in {JUDGMENT_ZERO, JUDGMENT_CERTIFICATE}


# ---------------------------------------------------------------------------
# Residual emission
# ---------------------------------------------------------------------------

def test_emits_residual_for_number_without_unit():
    mentions = extract_quantity_mentions("الرقم ١٢٣ فقط")
    mention = _find(mentions, normalized_value=123.0)
    assert mention.unit_normalized is None
    assert "quantity_number_without_unit" in mention.residuals


def test_emits_residual_for_unit_without_number():
    mentions = extract_quantity_mentions("هذه دقائق فقط بلا رقم")
    mention = _find(mentions, unit_normalized="minute")
    assert mention.value is None
    assert "quantity_unit_without_number" in mention.residuals


def test_ambiguous_unit_emits_residual():
    mentions = extract_quantity_mentions("اشترِ ٢٨ كيلو")
    mention = _find(mentions, normalized_value=28.0, unit_normalized="km")
    assert "quantity_unit_ambiguous" in mention.residuals


def test_residuals_are_non_erasing_in_payload():
    payload = build_quantity_extraction_payload("الرقم ١٢٣ فقط")
    assert "quantity_number_without_unit" in payload["residuals"]


# ---------------------------------------------------------------------------
# Governance — operator contract registration & forbidden outputs
# ---------------------------------------------------------------------------

def test_extractor_registers_as_prompt_text_span_to_quantity_mention():
    contract = build_quantity_extraction_operator_contract()
    assert contract.layer_from == "PromptTextSpan"
    assert contract.layer_to == "QuantityMention"
    assert contract.input_type == "ArabicSpan"
    assert contract.output_type == "QuantityMention"

    registry = FractalOperatorRegistry()
    result = registry.register(TypedOperatorCandidate(contract=contract))
    assert result.accepted is True
    assert result.residuals == []
    assert registry.get(contract.operator_id) is contract


def test_extractor_contract_rejects_judgment_output():
    contract = OperatorContract(
        operator_id=QUANTITY_EXTRACTION_OPERATOR_ID,
        layer_from="PromptTextSpan",
        layer_to="QuantityMention",
        input_type="ArabicSpan",
        output_type="Judgment",
        missing_gate="quantity_extraction_gate",
        gates=["numeric_or_number_word_present"],
        evidence_requirements=["span_trace_required"],
        residual_policy=["quantity_number_without_unit"],
        forbidden_outputs=["Judgment", "Certificate", "FinalAnswer"],
    )
    residuals = contract.validate()
    assert "operator_forbidden_output" in residuals


def test_extractor_contract_refuses_certificate_rank_promotion():
    contract = build_quantity_extraction_operator_contract(rank=JUDGMENT_CERTIFICATE)
    # Phase 3B-1 must remain hypothesis-only.
    assert contract.rank == JUDGMENT_HYPOTHESIS


# ---------------------------------------------------------------------------
# Composition — accepted only as the first step.
# ---------------------------------------------------------------------------

def test_extractor_composes_as_first_step_only():
    step_1 = build_quantity_extraction_operator_contract()
    step_2 = OperatorContract(
        operator_id="quantity.normalize.dimensioned",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
        missing_gate="unit_normalization_gate",
        gates=["unit_resolution_complete"],
        evidence_requirements=["unit_table_present"],
        residual_policy=["quantity_unit_ambiguous"],
        forbidden_outputs=["Judgment", "Certificate", "FinalAnswer"],
    )
    chain = OperatorCompositionContract(
        chain_id="phase3b-quantity-chain-first-two-steps",
        operators=[step_1, step_2],
        layer_sequence=["PromptTextSpan", "QuantityMention", "DimensionedQuantity"],
        input_type="ArabicSpan",
        output_type="DimensionedQuantity",
    )
    result = validate_operator_chain(
        OperatorChainCandidate(contract=chain, composed_trace=["span->mention->dimensioned"])
    )
    assert result.accepted is True


def test_extractor_cannot_be_chained_after_dimensioned_quantity():
    extractor = build_quantity_extraction_operator_contract()
    prior = OperatorContract(
        operator_id="quantity.normalize.dimensioned",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
        missing_gate="unit_normalization_gate",
        gates=["unit_resolution_complete"],
        evidence_requirements=["unit_table_present"],
        residual_policy=["quantity_unit_ambiguous"],
        forbidden_outputs=["Judgment", "Certificate", "FinalAnswer"],
    )
    chain = OperatorCompositionContract(
        chain_id="invalid-chain-extractor-not-first",
        operators=[prior, extractor],
        layer_sequence=["QuantityMention", "DimensionedQuantity", "QuantityMention"],
        input_type="QuantityMention",
        output_type="QuantityMention",
    )
    result = validate_operator_chain(
        OperatorChainCandidate(contract=chain, composed_trace=["dim->mention"])
    )
    assert result.accepted is False
    assert any(
        code in result.residuals
        for code in ("operator_chain_layer_mismatch", "operator_chain_type_mismatch")
    )


# ---------------------------------------------------------------------------
# Roundtrip serialization
# ---------------------------------------------------------------------------

def test_payload_roundtrip_preserves_mentions_and_residuals():
    prompt = "أريد قطع ٢٨ كم في عشرة دقائق والحد ٦٠ كم بالساعة، والرقم ١٢٣ بلا وحدة"
    payload = build_quantity_extraction_payload(prompt)
    serialized = serialize_quantity_extraction_payload(payload)
    deserialized = deserialize_quantity_extraction_payload(serialized)

    assert deserialized["raw_prompt"] == prompt
    assert deserialized["rank"] == JUDGMENT_HYPOTHESIS
    assert deserialized["quantity_mentions"] == payload["quantity_mentions"]
    assert "quantity_number_without_unit" in deserialized["residuals"]


def test_deserialization_refuses_certificate_rank_in_payload():
    payload = build_quantity_extraction_payload("٢٨ كم")
    payload["rank"] = JUDGMENT_CERTIFICATE
    deserialized = deserialize_quantity_extraction_payload(payload)
    assert deserialized["rank"] == JUDGMENT_HYPOTHESIS


def test_payload_validator_flags_missing_span_trace():
    payload = build_quantity_extraction_payload("٢٨ كم")
    payload["quantity_mentions"][0]["trace_anchor"] = {}
    residuals = validate_quantity_extraction_payload(payload)
    assert "quantity_span_trace_missing" in residuals


# ---------------------------------------------------------------------------
# Residual taxonomy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "code",
    [
        "quantity_number_without_unit",
        "quantity_unit_without_number",
        "quantity_unit_ambiguous",
        "quantity_word_number_unresolved",
        "quantity_span_trace_missing",
        "quantity_extraction_payload_invalid",
    ],
)
def test_quantity_residual_codes_are_governed_blockers(code):
    spec = classify_residual(code)
    assert spec.family is ResidualFamily.FRACTAL_OPERATOR
    assert spec.severity is ResidualSeverity.BLOCKER
    assert spec.blocks_certificate is True
