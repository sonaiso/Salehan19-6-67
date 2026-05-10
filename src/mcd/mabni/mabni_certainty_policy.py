"""MabniCertaintyPolicy — evaluates certainty policy for a MabniOperator."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction


@dataclass
class CertaintyPolicyResult:
    certainty_policy: str
    evidence_need: str
    decision_effect: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "certainty_policy": self.certainty_policy,
            "evidence_need": self.evidence_need,
            "decision_effect": self.decision_effect,
            "warnings": self.warnings,
        }


class MabniCertaintyPolicy:
    """Evaluates the certainty policy effect of a Mabni operator.

    Rules:
    - interrogative → request_evidence / suspend
    - conditional → conditional_certainty (judgment suspended)
    - negation → requires grounding / lower certainty
    - emphasis → no certainty increase without evidence
    - qasr → scope_restriction (not evidence)
    - preposition → creates relation, not evidence
    - answer → context_dependent
    - exception → scope_modification
    """

    def evaluate(self, operator: MabniOperator, context: dict | None = None) -> CertaintyPolicyResult:
        ctx = context or {}
        warnings: list[str] = []
        mt = operator.mabni_type
        lf = operator.logical_function
        pf = operator.pragmatic_function
        ce = operator.certainty_effect

        # Interrogative — suspends judgment, requests evidence
        if mt == MabniType.interrogative or pf == PragmaticFunction.question:
            warnings.append("question_not_assertion: interrogative suspends judgment and requests evidence")
            return CertaintyPolicyResult(
                certainty_policy="request_evidence",
                evidence_need="required_to_answer",
                decision_effect="suspend_judgment",
                warnings=warnings,
            )

        # Conditional — judgment conditionally suspended
        if mt == MabniType.conditional or lf == LogicalFunction.condition:
            warnings.append(
                "conditional_not_assertion: conditional does not assert the result; "
                "judgment suspended until condition verified"
            )
            return CertaintyPolicyResult(
                certainty_policy="conditional_certainty",
                evidence_need="condition_verification_required",
                decision_effect="suspend_until_condition_met",
                warnings=warnings,
            )

        # Negation — requires grounding
        if mt == MabniType.negation or lf == LogicalFunction.negation:
            warnings.append("negation_requires_grounding: negation lowers certainty; external grounding needed")
            return CertaintyPolicyResult(
                certainty_policy="lower_certainty",
                evidence_need="grounding_required",
                decision_effect="reduce_certainty_score",
                warnings=warnings,
            )

        # Emphasis — no certainty increase
        if mt == MabniType.emphasis or lf == LogicalFunction.emphasis or ce == CertaintyEffect.emphasis_only:
            warnings.append(
                "emphasis_not_evidence: emphasis increases discourse force only, "
                "not evidence strength or certainty"
            )
            return CertaintyPolicyResult(
                certainty_policy="emphasis_only",
                evidence_need="external_evidence_required_for_certainty",
                decision_effect="no_certainty_change",
                warnings=warnings,
            )

        # Qasr — scope restriction
        if mt == MabniType.restriction or lf == LogicalFunction.qasr:
            return CertaintyPolicyResult(
                certainty_policy="scope_restriction",
                evidence_need="none_within_scope",
                decision_effect="restrict_scope_of_predication",
                warnings=warnings,
            )

        # Exception — scope modification
        if mt == MabniType.exception or lf == LogicalFunction.exception:
            return CertaintyPolicyResult(
                certainty_policy="scope_modification",
                evidence_need="none",
                decision_effect="modify_scope",
                warnings=warnings,
            )

        # Preposition — relation only
        if mt == MabniType.preposition or lf == LogicalFunction.relation:
            return CertaintyPolicyResult(
                certainty_policy="standard",
                evidence_need="none",
                decision_effect="establish_relation_only",
                warnings=warnings,
            )

        # Prohibition / command
        if pf in (PragmaticFunction.prohibition, PragmaticFunction.command):
            return CertaintyPolicyResult(
                certainty_policy="directive",
                evidence_need="none",
                decision_effect="directive_speech_act",
                warnings=warnings,
            )

        # Answer particle
        if mt == MabniType.answer or lf == LogicalFunction.answer:
            if not ctx.get("previous_question"):
                warnings.append("discourse_context_required: answer particle needs prior question")
            return CertaintyPolicyResult(
                certainty_policy="context_dependent",
                evidence_need="discourse_context",
                decision_effect="confirm_or_deny_prior_claim",
                warnings=warnings,
            )

        # Demonstrative / relative reference
        if mt in (MabniType.demonstrative, MabniType.relative, MabniType.pronoun):
            return CertaintyPolicyResult(
                certainty_policy="standard",
                evidence_need="referent_resolution",
                decision_effect="establish_reference",
                warnings=warnings,
            )

        # Default standard policy
        return CertaintyPolicyResult(
            certainty_policy="standard",
            evidence_need="none",
            decision_effect="no_special_effect",
            warnings=warnings,
        )
