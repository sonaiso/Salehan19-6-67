from __future__ import annotations

from mcd.thinking.answer_birth import AnswerBirthContract, evaluate_answer_birth_contract
from mcd.thinking.core import PUBLIC_FINAL_JUDGMENTS
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace


def _complete_contract() -> AnswerBirthContract:
    return AnswerBirthContract(
        contract_id="ABC-1",
        user_intent=UserIntentFrame(
            intent_id="I-1",
            raw_request="explain x",
            normalized_request="explain x",
            inferred_intent="explain x",
            intent_status="explicit",
            uncertainty_preserved=True,
        ),
        consciousness_frame=ControlledConsciousnessFrame(
            frame_id="CF-1",
            source_request_ref="I-1",
            awareness_object="x",
            attention_state="focused",
            distinction_state="clear",
            reality_refs=["r-1"],
            prior_information_refs=["p-1"],
        ),
        mentality_frame=MentalityFrame(
            mentality_id="M-1",
            base_orientation="analytic",
            worldview_assumptions=["bounded"],
            domain="technical",
            allowed_methods=["rational"],
        ),
        thinking_method=ThinkingMethod(
            method_id="TM-1",
            method_type="rational",
            required_inputs=["intent", "evidence"],
            allowed_outputs=["explanation"],
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
            can_create_evidence=False,
            can_issue_judgment=False,
            constraints=["bounded"],
        ),
        thought_trace=ThoughtBirthTrace(
            trace_id="TR-1",
            intent_ref="I-1",
            consciousness_ref="CF-1",
            mentality_ref="M-1",
            method_ref="TM-1",
            style_ref="TS-1",
            means_ref="ME-1",
            language_ref="L-1",
            evidence_refs=["rank:high::source"],
            residuals=["trace_residual"],
            complete=True,
        ),
        public_judgment="certificate",
        blockers=[],
        residuals=["base_residual"],
    )


def test_public_judgment_triad_is_preserved():
    assert set(PUBLIC_FINAL_JUDGMENTS) == {"zero", "hypothesis", "certificate"}


def test_complete_governed_contract_can_certificate():
    result = evaluate_answer_birth_contract(_complete_contract())
    assert result.public_judgment == "certificate"
    assert result.trace_complete is True


def test_result_judgment_is_always_public_triad():
    contract = _complete_contract()
    contract.public_judgment = "non-public"
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment in {"zero", "hypothesis", "certificate"}
