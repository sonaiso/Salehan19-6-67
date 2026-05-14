from __future__ import annotations

from mcd.thinking.answer_birth import AnswerBirthContract, evaluate_answer_birth_contract
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace
from mcd.thinking.intent import UserIntentFrame


def _base_contract(intent: UserIntentFrame | None) -> AnswerBirthContract:
    return AnswerBirthContract(
        contract_id="INT-1",
        user_intent=intent,
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


def test_missing_intent_blocks_certificate_to_zero():
    result = evaluate_answer_birth_contract(_base_contract(None))
    assert result.public_judgment == "zero"


def test_ambiguous_intent_with_uncertainty_returns_hypothesis():
    intent = UserIntentFrame(
        intent_id="I-2",
        raw_request="do it",
        normalized_request="do it",
        inferred_intent="possible-intent",
        intent_status="ambiguous",
        uncertainty_preserved=True,
    )
    result = evaluate_answer_birth_contract(_base_contract(intent))
    assert result.public_judgment == "hypothesis"
    assert result.public_judgment != "certificate"
