from __future__ import annotations

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS
from mcd.core.residual_taxonomy import ResidualFamily, ResidualSeverity, classify_residual
from mcd.fractal_learning import (
    OperatorChainCandidate,
    OperatorCompositionContract,
    OperatorContract,
    validate_operator_chain,
)


def _operator(**overrides) -> OperatorContract:
    payload = {
        "operator_id": "quantity.extract.arabic_distance_expression",
        "layer_from": "PromptTextSpan",
        "layer_to": "QuantityMention",
        "input_type": "ArabicSpan",
        "output_type": "QuantityMention",
        "missing_gate": "quantity_extraction_gate",
        "gates": ["numeric_or_number_word_present", "unit_expression_present"],
        "evidence_requirements": ["span_trace_required"],
        "residual_policy": ["operator_missing_gate", "transition_repair_missing_evidence"],
        "forbidden_outputs": ["feasibility_judgment", "certificate", "final_answer"],
        "rank": JUDGMENT_HYPOTHESIS,
        "reverse_trace_required": True,
        "tests_required": ["positive", "negative"],
    }
    payload.update(overrides)
    return OperatorContract(**payload)


def _chain(operators: list[OperatorContract], **overrides) -> OperatorCompositionContract:
    payload = {
        "chain_id": "quantity-chain",
        "operators": operators,
        "layer_sequence": [operators[0].layer_from, operators[-1].layer_to],
        "input_type": operators[0].input_type,
        "output_type": operators[-1].output_type,
    }
    payload.update(overrides)
    return OperatorCompositionContract(**payload)


def test_valid_two_step_chain_is_accepted():
    step_1 = _operator()
    step_2 = _operator(
        operator_id="quantity.normalize.dimensioned_distance",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
    )
    chain = _chain(operators=[step_1, step_2], layer_sequence=["PromptTextSpan", "QuantityMention", "DimensionedQuantity"])
    result = validate_operator_chain(OperatorChainCandidate(contract=chain, composed_trace=["span->mention->dimension"]))
    assert result.accepted is True


def test_chain_with_layer_mismatch_is_rejected():
    step_1 = _operator(layer_to="QuantityMention")
    step_2 = _operator(layer_from="PhysicalRole", input_type="QuantityMention", output_type="DimensionedQuantity")
    result = validate_operator_chain(OperatorChainCandidate(contract=_chain([step_1, step_2]), composed_trace=["trace"]))
    assert result.accepted is False
    assert "operator_chain_layer_mismatch" in result.residuals


def test_chain_with_type_mismatch_is_rejected():
    step_1 = _operator(output_type="QuantityMention")
    step_2 = _operator(layer_from="QuantityMention", input_type="DimensionedQuantity", output_type="DimensionedQuantity")
    result = validate_operator_chain(OperatorChainCandidate(contract=_chain([step_1, step_2]), composed_trace=["trace"]))
    assert result.accepted is False
    assert "operator_chain_type_mismatch" in result.residuals


def test_prompt_to_judgment_chain_is_rejected():
    direct = _operator(
        operator_id="quantity.direct.to_judgment",
        layer_to="TaskClassification",
        output_type="Judgment",
    )
    result = validate_operator_chain(
        OperatorChainCandidate(contract=_chain([direct], output_type="Judgment"), composed_trace=["trace"])
    )
    assert result.accepted is False
    assert "operator_chain_forbidden_final_output" in result.residuals


def test_chain_to_final_answer_is_rejected_without_licensed_final_layer():
    final_answer = _operator(
        operator_id="quantity.to.final_answer",
        layer_to="ConstraintEvaluation",
        input_type="ArabicSpan",
        output_type="FinalAnswer",
    )
    result = validate_operator_chain(
        OperatorChainCandidate(contract=_chain([final_answer], output_type="FinalAnswer"), composed_trace=["trace"])
    )
    assert result.accepted is False
    assert "operator_chain_forbidden_final_output" in result.residuals


def test_chain_rank_is_min_of_operator_ranks():
    step_1 = _operator(rank=JUDGMENT_CERTIFICATE)
    step_2 = _operator(
        operator_id="quantity.normalize.dimensioned_distance",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
        rank=JUDGMENT_HYPOTHESIS,
    )
    result = validate_operator_chain(
        OperatorChainCandidate(
            contract=_chain([step_1, step_2], layer_sequence=["PromptTextSpan", "QuantityMention", "DimensionedQuantity"]),
            composed_trace=["trace"],
        )
    )
    assert result.accepted is True
    assert result.rank == JUDGMENT_HYPOTHESIS


def test_chain_residuals_are_non_erasing_union():
    step_1 = _operator(residual_policy=["operator_missing_gate"])
    step_2 = _operator(
        operator_id="quantity.normalize.dimensioned_distance",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
        residual_policy=["transition_repair_missing_evidence"],
    )
    result = validate_operator_chain(
        OperatorChainCandidate(
            contract=_chain([step_1, step_2], layer_sequence=["PromptTextSpan", "QuantityMention", "DimensionedQuantity"]),
            emitted_residuals=["operator_chain_invalid"],
            composed_trace=["trace"],
        )
    )
    assert "operator_missing_gate" in result.chain_residuals
    assert "transition_repair_missing_evidence" in result.chain_residuals
    assert "operator_chain_invalid" in result.chain_residuals


def test_missing_trace_composition_blocks_certificate_capable_chain():
    step_1 = _operator(rank=JUDGMENT_CERTIFICATE)
    result = validate_operator_chain(OperatorChainCandidate(contract=_chain([step_1])))
    assert result.accepted is False
    assert "operator_chain_missing_trace_composition" in result.residuals


def test_chain_cannot_hide_earlier_operator_residuals():
    step_1 = _operator(residual_policy=["operator_missing_gate"])
    step_2 = _operator(
        operator_id="quantity.normalize.dimensioned_distance",
        layer_from="QuantityMention",
        layer_to="DimensionedQuantity",
        input_type="QuantityMention",
        output_type="DimensionedQuantity",
        residual_policy=["transition_repair_missing_evidence"],
    )
    result = validate_operator_chain(
        OperatorChainCandidate(
            contract=_chain([step_1, step_2], layer_sequence=["PromptTextSpan", "QuantityMention", "DimensionedQuantity"]),
            composed_trace=["trace"],
            chain_residuals=["operator_missing_gate"],
        )
    )
    assert result.accepted is False
    assert "operator_chain_residual_erasure" in result.residuals


def test_local_sample_operator_cannot_produce_feasibility_judgment():
    sample = _operator(output_type="QuantityMention")
    result = validate_operator_chain(OperatorChainCandidate(contract=_chain([sample]), composed_trace=["trace"]))
    assert result.accepted is True
    assert result.output_type == "QuantityMention"
    assert result.output_type.lower() not in {"judgment", "certificate", "finalanswer", "projectconclusion"}


def test_new_operator_chain_residual_codes_are_governed_blockers():
    for code in [
        "operator_chain_type_mismatch",
        "operator_chain_layer_mismatch",
        "operator_chain_forbidden_final_output",
        "operator_chain_missing_trace_composition",
        "operator_chain_rank_overclaim",
        "operator_chain_residual_erasure",
        "operator_chain_invalid",
    ]:
        spec = classify_residual(code)
        assert spec.family is ResidualFamily.FRACTAL_OPERATOR
        assert spec.severity is ResidualSeverity.BLOCKER
        assert spec.blocks_certificate is True
