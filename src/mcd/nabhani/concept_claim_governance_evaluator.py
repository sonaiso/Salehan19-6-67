"""ConceptClaim governance evaluator and certificate gating."""
from __future__ import annotations

from dataclasses import dataclass


_CERTIFICATE_LEVELS = {"certificate", "CERTIFICATE"}
_KNOWN_CERTAINTY_LEVELS = {
    "zero",
    "hypothesis",
    "certificate",
    "possibility",
    "weak_evidence",
    "strong_evidence",
    "ZERO",
    "HYPOTHESIS",
    "CERTIFICATE",
}

_TOPICS_BY_DOMAIN: dict[str, set[str]] = {
    "scientific_experimental": {"material", "human"},
    "rational_general": {"general", "material", "human", "society", "creed", "concept", "renaissance"},
    "shari": {"legislation", "creed"},
    "normative": {"legislation", "society"},
}

_THINKING_TYPES_BY_TOPIC: dict[str, set[str]] = {
    "material": {"deep"},
    "human": {"deep"},
    "society": {"enlightened"},
    "creed": {"deep"},
    "legislation": {"deep"},
    "renaissance": {"enlightened"},
    "concept": {"deep", "enlightened"},
    "general": {"surface", "deep", "enlightened"},
}

_MEASURES_BY_DOMAIN: dict[str, set[str]] = {
    "scientific_experimental": {"empirical", "experimental", "quantitative", "formal"},
    "rational_general": {"rational", "formal", "logical"},
    "shari": {"scriptural", "usuli", "fiqh"},
    "normative": {"normative", "legal", "scriptural"},
}


@dataclass(frozen=True)
class ConceptClaim:
    claim: str
    domain: str
    topic: str
    thinking_type: str
    reality_anchor: str | None
    sensation_path: str | None
    prior_information: list[str]
    governing_measure: str
    certainty_level: str
    evidence_refs: list[str]
    reverse_trace_ref: str | None = None


@dataclass(frozen=True)
class ConceptClaimDecision:
    status: str
    gates: dict[str, bool]
    residuals: list[str]
    can_issue_certificate: bool
    certainty_level: str


class ConceptClaimGovernanceEvaluator:
    """Evaluate ConceptClaim through explicit governance gates."""

    def evaluate(self, claim: ConceptClaim) -> ConceptClaimDecision:
        residuals: list[str] = []

        reality_ok = _has_text(claim.reality_anchor)
        if not reality_ok:
            residuals.append("missing_reality_anchor")

        sensation_ok = _has_text(claim.sensation_path)
        if not sensation_ok:
            residuals.append("missing_sensation_path")

        prior_ok = any(_has_text(item) for item in claim.prior_information)
        if not prior_ok:
            residuals.append("prior_information_gap")

        domain_topic_ok = _is_domain_topic_match(claim.domain, claim.topic)
        if not domain_topic_ok:
            residuals.append("domain_topic_mismatch")

        thinking_ok = _is_thinking_type_match(claim.topic, claim.thinking_type)
        if not thinking_ok:
            residuals.append("thinking_type_mismatch")

        measure_ok = _is_governing_measure_valid(claim.domain, claim.governing_measure)
        if not measure_ok:
            residuals.append("invalid_governing_measure")

        certainty_ok = _is_certainty_admissible(claim.certainty_level, claim.evidence_refs)
        if not certainty_ok:
            residuals.append("certainty_overclaim")

        certificate_requested = claim.certainty_level in _CERTIFICATE_LEVELS
        reverse_trace_ok = _has_text(claim.reverse_trace_ref)
        if certificate_requested and not reverse_trace_ok:
            residuals.append("reverse_trace_missing")

        can_issue_certificate = (
            certificate_requested
            and reality_ok
            and sensation_ok
            and prior_ok
            and domain_topic_ok
            and thinking_ok
            and measure_ok
            and certainty_ok
            and reverse_trace_ok
        )
        if certificate_requested and not can_issue_certificate:
            residuals.append("certificate_not_allowed")

        gates = {
            "reality_gate": reality_ok,
            "sensation_or_transmission_gate": sensation_ok,
            "prior_knowledge_gate": prior_ok,
            "domain_topic_gate": domain_topic_ok,
            "thinking_type_gate": thinking_ok,
            "governing_measure_gate": measure_ok,
            "certainty_gate": certainty_ok,
            "reverse_trace_gate": reverse_trace_ok,
        }

        status = _resolve_status(
            reality_ok=reality_ok,
            measure_ok=measure_ok,
            domain_topic_ok=domain_topic_ok,
            thinking_ok=thinking_ok,
            sensation_ok=sensation_ok,
            prior_ok=prior_ok,
            certainty_ok=certainty_ok,
            certificate_requested=certificate_requested,
            can_issue_certificate=can_issue_certificate,
        )

        return ConceptClaimDecision(
            status=status,
            gates=gates,
            residuals=_unique_in_order(residuals),
            can_issue_certificate=can_issue_certificate,
            certainty_level=claim.certainty_level,
        )


def _resolve_status(
    *,
    reality_ok: bool,
    measure_ok: bool,
    domain_topic_ok: bool,
    thinking_ok: bool,
    sensation_ok: bool,
    prior_ok: bool,
    certainty_ok: bool,
    certificate_requested: bool,
    can_issue_certificate: bool,
) -> str:
    if not reality_ok:
        return "rejected"
    if not measure_ok:
        return "invalid_measure"
    if not domain_topic_ok or not thinking_ok:
        return "misclassified"
    if (not sensation_ok) or (not prior_ok) or (not certainty_ok):
        return "needs_evidence"
    if certificate_requested and not can_issue_certificate:
        return "needs_evidence"
    return "accepted"


def _has_text(value: str | None) -> bool:
    return bool(isinstance(value, str) and value.strip())


def _is_domain_topic_match(domain: str, topic: str) -> bool:
    normalized_domain = domain.strip().lower()
    normalized_topic = topic.strip().lower()
    allowed_topics = _TOPICS_BY_DOMAIN.get(normalized_domain)
    if not allowed_topics:
        return True
    return normalized_topic in allowed_topics


def _is_thinking_type_match(topic: str, thinking_type: str) -> bool:
    normalized_topic = topic.strip().lower()
    normalized_type = thinking_type.strip().lower()
    allowed_types = _THINKING_TYPES_BY_TOPIC.get(normalized_topic)
    if not allowed_types:
        return normalized_type in {"deep", "enlightened", "surface"}
    return normalized_type in allowed_types


def _is_governing_measure_valid(domain: str, governing_measure: str) -> bool:
    normalized_domain = domain.strip().lower()
    normalized_measure = governing_measure.strip().lower()
    if not normalized_measure:
        return False
    allowed_measures = _MEASURES_BY_DOMAIN.get(normalized_domain)
    if not allowed_measures:
        return True
    return normalized_measure in allowed_measures


def _is_certainty_admissible(certainty_level: str, evidence_refs: list[str]) -> bool:
    normalized_level = certainty_level.strip().lower()
    if certainty_level not in _KNOWN_CERTAINTY_LEVELS and normalized_level not in _KNOWN_CERTAINTY_LEVELS:
        return False
    if normalized_level != "certificate":
        return True
    return len([ref for ref in evidence_refs if _has_text(ref)]) >= 2


def _unique_in_order(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
