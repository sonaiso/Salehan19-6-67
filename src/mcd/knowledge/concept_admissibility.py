"""Concept admissibility checks against qualified golden rules."""
from __future__ import annotations

from dataclasses import dataclass

from mcd.knowledge.golden_prior_registry import (
    GoldenRuleMaturityLevel,
    PriorRegistry,
    PriorRule,
    qualify_golden_rule,
)

_CERT_ASCENT = {"CERTIFICATE", "CERTIFICATE_CANDIDATE", "STRONG"}


@dataclass(frozen=True)
class NewConceptClaim:
    concept_id: str
    claim: str
    domain: str
    layer: str
    required_evidence: tuple[str, ...]
    proposed_decision_level: str
    residuals: tuple[str, ...]
    trace: dict[str, str]


@dataclass(frozen=True)
class ConceptAdmissibilityResult:
    concept_id: str
    matched_golden_rule_ids: tuple[str, ...]
    blocked_by_rules: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    residuals: tuple[str, ...]
    decision_level: str
    certificate_blocked: bool
    can_issue_certificate: bool


def _trace_complete_for_rule(claim: NewConceptClaim, rule: PriorRule) -> bool:
    if not rule.reverse_trace_requirements.required:
        return True
    for field in rule.reverse_trace_requirements.required_fields:
        value = claim.trace.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def _evidence_missing_for_rule(claim: NewConceptClaim, rule: PriorRule) -> set[str]:
    required = set(rule.required_evidence.required_items)
    supplied = set(claim.required_evidence)
    return required - supplied


def evaluate_concept_against_golden_rules(
    concept: NewConceptClaim,
    registry: PriorRegistry,
) -> ConceptAdmissibilityResult:
    domain_rules = registry.find_rules(domain=concept.domain, layer=concept.layer)
    if not domain_rules:
        domain_rules = registry.find_rules(domain=concept.domain)

    golden_rules: list[PriorRule] = []
    for rule in domain_rules:
        q = qualify_golden_rule(rule)
        if q.maturity_level in {
            GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE,
            GoldenRuleMaturityLevel.GOLDEN_RULE,
        } and q.can_measure_new_concepts:
            golden_rules.append(rule)

    missing_evidence: set[str] = set()
    blocked_by_rules: set[str] = set()
    residuals = set(concept.residuals)

    claim_blob = " ".join([concept.claim, concept.concept_id]).lower()
    concept_tokens = set(str(item) for item in concept.residuals)

    for rule in golden_rules:
        missing_evidence.update(_evidence_missing_for_rule(concept, rule))

        if not _trace_complete_for_rule(concept, rule):
            blocked_by_rules.add(f"{rule.rule_id}:reverse_trace_incomplete")

        for blocker in rule.certificate_blockers:
            if any(token in concept_tokens for token in blocker.match_any) or any(
                token.lower() in claim_blob for token in blocker.match_any
            ):
                blocked_by_rules.add(f"{rule.rule_id}:{blocker.blocker_id}")

    certificate_blocked = False
    if concept.proposed_decision_level == "CERTIFICATE":
        if not golden_rules:
            certificate_blocked = True
            residuals.add("golden_rule_coverage_gap")
            residuals.add("concept_missing_prior_support")
        if missing_evidence:
            certificate_blocked = True
            residuals.add("concept_missing_required_evidence")
        if blocked_by_rules:
            certificate_blocked = True
            residuals.add("concept_forbidden_certificate")

    if concept.proposed_decision_level in _CERT_ASCENT and concept.proposed_decision_level != "CERTIFICATE":
        residuals.add("concept_requires_certificate_obligations")

    proposed = concept.proposed_decision_level
    decision_level = "ZERO" if proposed == "ZERO" else "HYPOTHESIS"
    if proposed == "CERTIFICATE" and not certificate_blocked:
        decision_level = "CERTIFICATE"

    return ConceptAdmissibilityResult(
        concept_id=concept.concept_id,
        matched_golden_rule_ids=tuple(sorted(rule.rule_id for rule in golden_rules)),
        blocked_by_rules=tuple(sorted(blocked_by_rules)),
        missing_evidence=tuple(sorted(missing_evidence)),
        residuals=tuple(sorted(residuals)),
        decision_level=decision_level,
        certificate_blocked=certificate_blocked,
        can_issue_certificate=(decision_level == "CERTIFICATE"),
    )
