from __future__ import annotations

from mcd.thinking.answer_birth import AnswerBirthContract, evaluate_answer_birth_contract
from mcd.thinking.forbidden_transitions import THINKING_FORBIDDEN_TRANSITIONS, find_forbidden_transitions
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace


def _contract() -> AnswerBirthContract:
    return AnswerBirthContract(
        contract_id="FT-1",
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


def test_forbidden_transition_registry_contains_required_items():
    required = {
        "answer_without_intent_understanding",
        "means_as_judgment",
        "scientific_method_as_normative_judgment",
        "residual_erasure",
        "silent_level_skip",
    }
    assert required.issubset(set(THINKING_FORBIDDEN_TRANSITIONS))


def test_find_forbidden_transitions_normalizes_and_deduplicates():
    found = find_forbidden_transitions(["MEANS_AS_JUDGMENT", "means_as_judgment", "ok"])
    assert found == ["means_as_judgment"]


def test_forbidden_transition_blocks_to_zero():
    contract = _contract()
    contract.blockers = ["fluent_language_as_proof"]
    result = evaluate_answer_birth_contract(contract)
    assert result.public_judgment == "zero"
