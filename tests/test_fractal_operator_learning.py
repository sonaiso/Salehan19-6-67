from __future__ import annotations

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS
from mcd.core.residual_taxonomy import ResidualFamily, ResidualSeverity, classify_residual
from mcd.fractal_learning import (
    FractalOperatorRegistry,
    OperatorContract,
    TypedOperatorCandidate,
    locate_broken_transition,
)


def _base_contract(**overrides):
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


def test_failure_locator_emits_typed_prompt_to_quantity_transition():
    failure = locate_broken_transition(
        residual_codes=["missing_quantitative_operator"],
        evidence=["prompt_span: \"٢٨ كم خلال ١٠ دقائق\""],
    )
    assert failure.layer_from == "PromptUnderstanding"
    assert failure.layer_to == "QuantityExtraction"
    assert failure.missing_gate == "quantity_extraction_gate"
    assert failure.residual_type == "missing_quantitative_operator"


def test_free_rule_solve_airport_problem_is_rejected():
    registry = FractalOperatorRegistry()
    candidate = TypedOperatorCandidate(contract=_base_contract(operator_id="solve_airport_problem"))

    result = registry.register(candidate)

    assert result.accepted is False
    assert "operator_contract_invalid" in result.residuals


def test_prompt_to_judgment_operator_is_rejected():
    contract = _base_contract(
        layer_from="PromptTextSpan",
        layer_to="TaskClassification",
        output_type="Judgment",
    )
    residuals = contract.validate()
    assert "operator_forbidden_output" in residuals


def test_multi_transition_operator_is_rejected():
    contract = _base_contract(layer_from="PromptTextSpan->QuantityMention")
    residuals = contract.validate()
    assert "operator_multi_transition_forbidden" in residuals


def test_missing_layer_mapping_is_rejected():
    contract = _base_contract(layer_from="")
    residuals = contract.validate()
    assert "operator_missing_layer_mapping" in residuals


def test_missing_gates_are_rejected():
    contract = _base_contract(gates=[])
    residuals = contract.validate()
    assert "operator_missing_gate" in residuals


def test_forbidden_output_is_rejected():
    contract = _base_contract(layer_to="QuantityMention", output_type="Certificate")
    residuals = contract.validate()
    assert "operator_forbidden_output" in residuals


def test_valid_local_operator_is_accepted():
    registry = FractalOperatorRegistry()
    candidate = TypedOperatorCandidate(contract=_base_contract())
    result = registry.register(candidate)

    assert result.accepted is True
    assert result.residuals == []


def test_candidate_residuals_are_non_erasing():
    candidate = TypedOperatorCandidate(
        contract=_base_contract(gates=[]),
        residuals=["operator_contract_invalid"],
    )
    residuals = candidate.validate()

    assert "operator_contract_invalid" in residuals
    assert "operator_missing_gate" in residuals


def test_certificate_capable_operator_requires_reverse_trace():
    contract = _base_contract(rank=JUDGMENT_CERTIFICATE, reverse_trace_required=False)
    residuals = contract.validate()

    assert "operator_missing_reverse_trace" in residuals


def test_quantitative_sample_operator_stays_local_and_not_final_judgment():
    registry = FractalOperatorRegistry()
    contract = _base_contract(
        operator_id="quantity.extract.arabic_distance_expression",
        layer_from="PromptTextSpan",
        layer_to="QuantityMention",
        output_type="QuantityMention",
    )

    result = registry.register(TypedOperatorCandidate(contract=contract))

    assert result.accepted is True
    assert contract.output_type == "QuantityMention"
    assert contract.output_type.lower() not in {"zero", "hypothesis", "certificate", "answer"}


def test_new_operator_residual_codes_are_governed_blockers():
    for code in [
        "operator_missing_layer_mapping",
        "operator_missing_gate",
        "operator_forbidden_output",
        "operator_missing_reverse_trace",
        "operator_multi_transition_forbidden",
        "operator_contract_invalid",
        "transition_repair_missing_evidence",
    ]:
        spec = classify_residual(code)
        assert spec.family is ResidualFamily.FRACTAL_OPERATOR
        assert spec.severity is ResidualSeverity.BLOCKER
        assert spec.blocks_certificate is True
