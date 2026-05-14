"""Governed answer-birth contract and evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS, collapse_to_public_judgment
from mcd.thinking.forbidden_transitions import find_forbidden_transitions
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod, evidence_rank_sufficient
from mcd.thinking.styles import ThinkingStyle, style_belongs_to_method
from mcd.thinking.trace import ThoughtBirthTrace


@dataclass
class AnswerBirthContract:
    contract_id: str
    user_intent: UserIntentFrame | None
    consciousness_frame: ControlledConsciousnessFrame | None
    mentality_frame: MentalityFrame | None
    thinking_method: ThinkingMethod | None
    thinking_style: ThinkingStyle | None
    thinking_means: ThinkingMeans | None
    thought_trace: ThoughtBirthTrace | None
    public_judgment: str = "hypothesis"
    blockers: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)


@dataclass
class AnswerBirthEvaluationResult:
    contract_id: str
    public_judgment: str
    blockers: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    trace_complete: bool = False


def evaluate_answer_birth_contract(contract: AnswerBirthContract) -> AnswerBirthEvaluationResult:
    """Evaluate governed answer birth and emit only zero/hypothesis/certificate.

    The decision is based on blocker presence, thought-trace completeness,
    governed intent state, and evidence-rank sufficiency.
    """
    blockers = _collect_blockers(contract)
    residuals = _collect_residuals(contract)

    trace_complete = bool(contract.thought_trace and contract.thought_trace.complete)
    if contract.thought_trace:
        contract.thought_trace.assess_completeness()
        trace_complete = contract.thought_trace.complete

    fatal = bool(blockers)
    if fatal:
        return AnswerBirthEvaluationResult(
            contract_id=contract.contract_id,
            public_judgment="zero",
            blockers=blockers,
            residuals=_merge_unique(residuals, blockers),
            trace_complete=trace_complete,
        )

    intent = contract.user_intent
    evidence_refs = contract.thought_trace.evidence_refs if contract.thought_trace else []
    method = contract.thinking_method

    if not intent or intent.intent_status in {"missing"}:
        return _zero(contract.contract_id, ["answer_without_intent_understanding"], residuals, trace_complete)

    if not trace_complete:
        return AnswerBirthEvaluationResult(
            contract_id=contract.contract_id,
            public_judgment="hypothesis",
            blockers=[],
            residuals=_merge_unique(residuals, ["answer_without_birth_trace"]),
            trace_complete=False,
        )

    if intent.intent_status in {"ambiguous", "inferred"} and intent.uncertainty_preserved:
        return AnswerBirthEvaluationResult(
            contract_id=contract.contract_id,
            public_judgment="hypothesis",
            blockers=[],
            residuals=_merge_unique(residuals, ["intent_not_fully_explicit"]),
            trace_complete=True,
        )

    if method and not evidence_rank_sufficient(method.required_evidence_rank, evidence_refs):
        return AnswerBirthEvaluationResult(
            contract_id=contract.contract_id,
            public_judgment="hypothesis",
            blockers=[],
            residuals=_merge_unique(residuals, ["incomplete_evidence_rank"]),
            trace_complete=True,
        )

    requested = collapse_to_public_judgment(contract.public_judgment)
    if requested not in PUBLIC_FINAL_JUDGMENTS:
        requested = "zero"

    if requested == "zero":
        return AnswerBirthEvaluationResult(
            contract_id=contract.contract_id,
            public_judgment="zero",
            blockers=[],
            residuals=residuals,
            trace_complete=True,
        )

    return AnswerBirthEvaluationResult(
        contract_id=contract.contract_id,
        public_judgment="certificate",
        blockers=[],
        residuals=residuals,
        trace_complete=True,
    )


def _collect_blockers(contract: AnswerBirthContract) -> list[str]:
    blockers = _merge_unique([], find_forbidden_transitions(contract.blockers))
    blockers = _merge_unique(blockers, contract.blockers)

    intent = contract.user_intent
    method = contract.thinking_method
    style = contract.thinking_style
    means = contract.thinking_means
    trace = contract.thought_trace
    mentality = contract.mentality_frame

    if not intent or not intent.has_intent():
        blockers.append("answer_without_intent_understanding")
    elif intent.intent_status in {"ambiguous", "inferred"} and not intent.uncertainty_preserved:
        blockers.append("uncertainty_erasure")

    if method is None:
        blockers.append("thought_without_method")

    if style and method is None:
        blockers.append("style_without_method")
    elif style and method and not style_belongs_to_method(style, method):
        blockers.append("style_without_method")

    if means is None:
        blockers.append("means_as_method")

    if means and means.can_issue_judgment:
        blockers.append("means_as_judgment")

    if means and means.means_type == "llm" and trace and not trace.evidence_refs:
        blockers.append("tool_output_as_evidence_without_governance")

    if trace is None:
        blockers.append("answer_without_birth_trace")
    else:
        trace.assess_completeness()
        if not trace.complete:
            if not any([trace.intent_ref, trace.method_ref, trace.style_ref, trace.means_ref]):
                blockers.append("answer_without_birth_trace")

    if trace and trace.language_ref and not trace.evidence_refs:
        blockers.append("fluent_language_as_proof")

    if method and method.method_type == "scientific":
        if _targets_worldview(mentality, method):
            blockers.append("scientific_method_as_worldview")
        if _targets_normative(mentality, method):
            blockers.append("scientific_method_as_normative_judgment")

    if _targets_normative(mentality, method) and not _has_normative_evidence(trace):
        blockers.append("normative_judgment_without_normative_evidence")

    return list(dict.fromkeys(b for b in blockers if b))


def _collect_residuals(contract: AnswerBirthContract) -> list[str]:
    residuals = list(contract.residuals)
    if contract.user_intent:
        residuals.extend(contract.user_intent.residuals)
    if contract.consciousness_frame:
        residuals.extend(contract.consciousness_frame.residuals)
    if contract.mentality_frame:
        residuals.extend(contract.mentality_frame.residuals)
    if contract.thought_trace:
        residuals.extend(contract.thought_trace.residuals)
    return list(dict.fromkeys((r or "").strip().lower() for r in residuals if (r or "").strip()))


def _target_text(mentality: MentalityFrame | None, method: ThinkingMethod | None) -> str:
    if mentality is None:
        return ""
    hay = [mentality.base_orientation, mentality.domain, *mentality.worldview_assumptions]
    hay.extend(method.allowed_outputs if method else [])
    hay.extend(method.forbidden_outputs if method else [])
    return " ".join((x or "").strip().lower() for x in hay)


def _targets_worldview(mentality: MentalityFrame | None, method: ThinkingMethod | None) -> bool:
    text = _target_text(mentality, method)
    return "worldview" in text


def _targets_normative(mentality: MentalityFrame | None, method: ThinkingMethod | None) -> bool:
    text = _target_text(mentality, method)
    return any(token in text for token in ("normative", "moral", "legal", "shari"))


def _has_normative_evidence(trace: ThoughtBirthTrace | None) -> bool:
    if trace is None:
        return False
    return any("normative::" in (ref or "").strip().lower() for ref in trace.evidence_refs)


def _merge_unique(base: list[str], extra: list[str]) -> list[str]:
    out = list(base)
    for item in extra:
        if item not in out:
            out.append(item)
    return out


def _zero(contract_id: str, blockers: list[str], residuals: list[str], trace_complete: bool) -> AnswerBirthEvaluationResult:
    return AnswerBirthEvaluationResult(
        contract_id=contract_id,
        public_judgment="zero",
        blockers=list(dict.fromkeys(blockers)),
        residuals=_merge_unique(residuals, blockers),
        trace_complete=trace_complete,
    )
