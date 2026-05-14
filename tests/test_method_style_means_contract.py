from __future__ import annotations

from mcd.thinking.answer_birth import AnswerBirthContract, evaluate_answer_birth_contract
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace


def _contract() -> AnswerBirthContract:
    return AnswerBirthContract(
        contract_id="MSC-1",
        user_intent=UserIntentFrame(
            intent_id="I-1",
            raw_request="x",
            normalized_request="x",
            inferred_intent="x",
            intent_status="explicit",
            uncertainty_preserved=True,
        ),
        consciousness_frame=ControlledConsciousnessFrame(frame_id="C-1", source_request_ref="I-1"),
        mentality_frame=MentalityFrame(mentality_id="M-1", base_orientation="analytic"),
        thinking_method=ThinkingMethod(
            method_id="TM-1",
            method_type="rational",
            required_inputs=["intent"],
            allowed_outputs=["answer"],
            forbidden_outputs=[],
            required_evidence_rank="low",
        ),
        thinking_style=ThinkingStyle(
            style_id="TS-1",
            method_id="TM-1",
            style_type="analysis",
            required_method_type="rational",
        ),
        thinking_means=ThinkingMeans(means_id="ME-1", means_type="llm", can_issue_judgment=False),
        thought_trace=ThoughtBirthTrace(
            trace_id="T-1",
            intent_ref="I-1",
            consciousness_ref="C-1",
            mentality_ref="M-1",
            method_ref="TM-1",
            style_ref="TS-1",
            means_ref="ME-1",
            language_ref="L-1",
            evidence_refs=["rank:high::e1"],
            complete=True,
        ),
        public_judgment="certificate",
    )


def test_missing_method_blocks_certificate():
    contract = _contract()
    contract.thinking_method = None
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"


def test_style_without_method_is_forbidden():
    contract = _contract()
    contract.thinking_style.required_method_type = "scientific"
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
    assert "style_without_method" in result.blockers


def test_means_as_method_is_forbidden():
    contract = _contract()
    contract.blockers = ["means_as_method"]
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"


def test_means_as_judgment_is_forbidden():
    contract = _contract()
    contract.thinking_means.can_issue_judgment = True
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"


def test_llm_output_alone_cannot_be_evidence():
    contract = _contract()
    contract.thought_trace.evidence_refs = []
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
