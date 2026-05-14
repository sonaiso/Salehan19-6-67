from __future__ import annotations

from mcd.thinking.answer_birth import AnswerBirthContract, evaluate_answer_birth_contract
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace


def _complete_contract() -> AnswerBirthContract:
    return AnswerBirthContract(
        contract_id="ABG-1",
        user_intent=UserIntentFrame(
            intent_id="I-1",
            raw_request="answer",
            normalized_request="answer",
            inferred_intent="answer",
            intent_status="explicit",
            uncertainty_preserved=True,
            residuals=["intent_residual"],
        ),
        consciousness_frame=ControlledConsciousnessFrame(
            frame_id="C-1",
            source_request_ref="I-1",
            residuals=["conscious_residual"],
        ),
        mentality_frame=MentalityFrame(
            mentality_id="M-1",
            base_orientation="analytic",
            worldview_assumptions=["bounded"],
            domain="technical",
            residuals=["mentality_residual"],
        ),
        thinking_method=ThinkingMethod(
            method_id="TM-1",
            method_type="rational",
            required_inputs=["intent", "evidence"],
            allowed_outputs=["answer"],
            forbidden_outputs=[],
            required_evidence_rank="medium",
        ),
        thinking_style=ThinkingStyle(
            style_id="TS-1",
            method_id="TM-1",
            style_type="analysis",
            required_method_type="rational",
        ),
        thinking_means=ThinkingMeans(
            means_id="ME-1",
            means_type="llm",
            can_issue_judgment=False,
        ),
        thought_trace=ThoughtBirthTrace(
            trace_id="T-1",
            intent_ref="I-1",
            consciousness_ref="C-1",
            mentality_ref="M-1",
            method_ref="TM-1",
            style_ref="TS-1",
            means_ref="ME-1",
            language_ref="L-1",
            evidence_refs=["rank:high::ev-1", "normative::ev-norm-1"],
            residuals=["trace_residual"],
            complete=True,
        ),
        public_judgment="certificate",
        residuals=["contract_residual"],
    )


def test_fluent_language_alone_is_not_proof():
    contract = _complete_contract()
    contract.thought_trace.evidence_refs = []
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
    assert "fluent_language_as_proof" in result.blockers


def test_scientific_method_cannot_directly_issue_normative_or_worldview_judgment():
    contract = _complete_contract()
    contract.thinking_method.method_type = "scientific"
    contract.mentality_frame.domain = "normative legal"
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
    assert "scientific_method_as_normative_judgment" in result.blockers


def test_normative_judgment_without_normative_evidence_is_blocked():
    contract = _complete_contract()
    contract.mentality_frame.domain = "normative"
    contract.thought_trace.evidence_refs = ["rank:high::e1"]
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
    assert "normative_judgment_without_normative_evidence" in result.blockers


def test_trace_completeness_is_required_for_certificate():
    contract = _complete_contract()
    contract.thought_trace.language_ref = ""
    contract.thought_trace.complete = False
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "hypothesis"
    assert result.trace_complete is False


def test_residuals_are_preserved_in_result():
    result = evaluate_answer_birth_contract(_complete_contract())
    assert result.public_judgment == "certificate"
    for expected in [
        "contract_residual",
        "intent_residual",
        "conscious_residual",
        "mentality_residual",
        "trace_residual",
    ]:
        assert expected in result.residuals
