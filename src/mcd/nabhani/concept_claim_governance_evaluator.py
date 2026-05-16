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

_ONTOLOGICAL_OBJECT_TYPES = {
    "entity",
    "attribute",
    "event",
    "relation",
    "constraint",
    "state",
    "transformation",
    "causal_link",
}

_REPRESENTATION_TYPES = {
    "symbolic",
    "sensory",
    "linguistic",
    "mathematical",
    "shari",
    "social",
    "causal",
    "probabilistic",
}

_ALLOWED_REPRESENTATIONS_BY_OBJECT: dict[str, set[str]] = {
    "entity": {"symbolic", "sensory", "linguistic", "mathematical", "social"},
    "attribute": {"symbolic", "linguistic", "mathematical", "probabilistic"},
    "event": {"sensory", "linguistic", "causal", "mathematical", "probabilistic"},
    "relation": {"symbolic", "linguistic", "mathematical", "social", "causal"},
    "constraint": {"symbolic", "linguistic", "mathematical", "shari"},
    "state": {"sensory", "linguistic", "mathematical", "probabilistic"},
    "transformation": {"causal", "mathematical", "linguistic", "symbolic"},
    "causal_link": {"causal", "linguistic", "mathematical", "probabilistic"},
}


@dataclass(frozen=True)
class OntologicalMetricOperator:
    name: str
    existence_constraints: set[str]
    representation_constraints: set[str]
    semantic_constraints: set[str]
    inference_constraints: set[str]
    relation_constraints: set[str]
    allowed_domains: set[str]
    allowed_topics: set[str]
    certainty_constraints: set[str]
    reconstruction_constraints: set[str]


_METRIC_OPERATORS: dict[str, OntologicalMetricOperator] = {
    "experiment": OntologicalMetricOperator(
        name="experiment",
        existence_constraints={"event", "state", "transformation", "causal_link"},
        representation_constraints={"sensory", "causal", "mathematical", "probabilistic"},
        semantic_constraints={"empirical", "causal"},
        inference_constraints={"experimental", "inductive", "statistical"},
        relation_constraints={"causal", "observable", "functional"},
        allowed_domains={"scientific_experimental"},
        allowed_topics={"material", "human", "general"},
        certainty_constraints={"zero", "hypothesis", "certificate"},
        reconstruction_constraints={"reverse_trace_required_for_certificate"},
    ),
    "empirical": OntologicalMetricOperator(
        name="empirical",
        existence_constraints={"event", "state", "entity"},
        representation_constraints={"sensory", "mathematical", "probabilistic"},
        semantic_constraints={"empirical"},
        inference_constraints={"inductive", "statistical", "experimental"},
        relation_constraints={"observable", "functional"},
        allowed_domains={"scientific_experimental"},
        allowed_topics={"material", "human", "general"},
        certainty_constraints={"zero", "hypothesis", "certificate"},
        reconstruction_constraints={"reverse_trace_required_for_certificate"},
    ),
    "dalala": OntologicalMetricOperator(
        name="dalala",
        existence_constraints={"entity", "attribute", "relation"},
        representation_constraints={"symbolic", "linguistic"},
        semantic_constraints={"linguistic", "semantic"},
        inference_constraints={"dalala", "semantic_analysis"},
        relation_constraints={"linguistic", "symbolic"},
        allowed_domains={"rational_general"},
        allowed_topics={"concept", "general", "creed"},
        certainty_constraints={"zero", "hypothesis"},
        reconstruction_constraints={"semantic_trace_required"},
    ),
    "qiyas_shari": OntologicalMetricOperator(
        name="qiyas_shari",
        existence_constraints={"entity", "event", "relation", "constraint"},
        representation_constraints={"shari", "linguistic", "symbolic"},
        semantic_constraints={"normative", "shari"},
        inference_constraints={"qiyas_shari", "usuli"},
        relation_constraints={"illah", "legal_analogy"},
        allowed_domains={"shari", "normative"},
        allowed_topics={"legislation", "human", "society", "creed"},
        certainty_constraints={"zero", "hypothesis", "certificate"},
        reconstruction_constraints={"reverse_trace_required_for_certificate"},
    ),
    "rational": OntologicalMetricOperator(
        name="rational",
        existence_constraints={"entity", "attribute", "relation", "constraint", "state"},
        representation_constraints={"symbolic", "linguistic", "mathematical"},
        semantic_constraints={"logical", "conceptual", "semantic"},
        inference_constraints={"deductive", "rational", "logical"},
        relation_constraints={"logical", "conceptual"},
        allowed_domains={"rational_general"},
        allowed_topics={"general", "concept", "creed", "renaissance"},
        certainty_constraints={"zero", "hypothesis", "certificate"},
        reconstruction_constraints={"reasoning_trace_required"},
    ),
}

_MEASURE_ALIASES = {
    "experimental": "experiment",
    "quantitative": "experiment",
    "formal": "rational",
    "logical": "rational",
    "scriptural": "qiyas_shari",
    "usuli": "qiyas_shari",
    "fiqh": "qiyas_shari",
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
    ontological_object_type: str | None = None
    representation_type: str | None = None
    relation_type: str | None = None
    semantic_type: str | None = None
    inference_type: str | None = None
    evidence_basis_type: str | None = None
    inference_basis_type: str | None = None
    judgment_basis_type: str | None = None


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

        ontological_object_type = _resolve_ontological_object_type(claim)
        ontological_object_ok = ontological_object_type in _ONTOLOGICAL_OBJECT_TYPES
        if not ontological_object_ok:
            residuals.append("unsupported_data_type")

        representation_type = _resolve_representation_type(claim)
        representational_eligibility_ok, representational_residuals = _evaluate_representational_eligibility(
            ontological_object_type=ontological_object_type,
            representation_type=representation_type,
        )
        residuals.extend(representational_residuals)

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

        metric_eval = _evaluate_metric_operator(
            claim=claim,
            ontological_object_type=ontological_object_type,
            representation_type=representation_type,
        )
        measure_ok = metric_eval["measure_ok"]
        if not measure_ok:
            residuals.append("invalid_governing_measure")
        residuals.extend(metric_eval["residuals"])

        semantic_inference_ok = metric_eval["semantic_inference_ok"]
        semantic_layer_separation_eval = _evaluate_semantic_layer_separation(
            claim=claim,
            semantic_inference_gate=semantic_inference_ok,
        )
        semantic_layer_separation_ok = semantic_layer_separation_eval["semantic_layer_separation_ok"]
        residuals.extend(semantic_layer_separation_eval["residuals"])

        certainty_ok = _is_certainty_admissible(
            claim.certainty_level,
            claim.evidence_refs,
            certificate_allowed_by_metric=metric_eval["certificate_allowed"],
        )
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
            "ontological_object_gate": ontological_object_ok,
            "representational_eligibility_gate": representational_eligibility_ok,
            "reality_gate": reality_ok,
            "sensation_or_transmission_gate": sensation_ok,
            "prior_knowledge_gate": prior_ok,
            "domain_topic_gate": domain_topic_ok,
            "thinking_type_gate": thinking_ok,
            "governing_measure_gate": measure_ok,
            "semantic_inference_gate": semantic_inference_ok,
            "semantic_layer_separation_gate": semantic_layer_separation_ok,
            "certainty_gate": certainty_ok,
            "reverse_trace_gate": reverse_trace_ok,
        }

        status = _resolve_status(
            ontological_object_ok=ontological_object_ok,
            representational_eligibility_ok=representational_eligibility_ok,
            reality_ok=reality_ok,
            measure_ok=measure_ok,
            domain_topic_ok=domain_topic_ok,
            thinking_ok=thinking_ok,
            semantic_inference_ok=semantic_inference_ok,
            semantic_layer_separation_ok=semantic_layer_separation_ok,
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
    ontological_object_ok: bool,
    representational_eligibility_ok: bool,
    reality_ok: bool,
    measure_ok: bool,
    domain_topic_ok: bool,
    thinking_ok: bool,
    semantic_inference_ok: bool,
    semantic_layer_separation_ok: bool,
    sensation_ok: bool,
    prior_ok: bool,
    certainty_ok: bool,
    certificate_requested: bool,
    can_issue_certificate: bool,
) -> str:
    if not ontological_object_ok or not representational_eligibility_ok:
        return "invalid_measure"
    if not reality_ok:
        return "rejected"
    if not domain_topic_ok or not thinking_ok:
        return "misclassified"
    if not measure_ok:
        return "invalid_measure"
    if not semantic_inference_ok or not semantic_layer_separation_ok:
        return "invalid_measure"
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


def _is_certainty_admissible(
    certainty_level: str,
    evidence_refs: list[str],
    *,
    certificate_allowed_by_metric: bool,
) -> bool:
    normalized_level = certainty_level.strip().lower()
    if certainty_level not in _KNOWN_CERTAINTY_LEVELS and normalized_level not in _KNOWN_CERTAINTY_LEVELS:
        return False
    if normalized_level != "certificate":
        return True
    if not certificate_allowed_by_metric:
        return False
    return len([ref for ref in evidence_refs if _has_text(ref)]) >= 2


def _resolve_ontological_object_type(claim: ConceptClaim) -> str:
    value = str(claim.ontological_object_type or "").strip().lower()
    if value:
        return value
    topic = str(claim.topic or "").strip().lower()
    if topic in {"material", "human", "society"}:
        return "event"
    if topic in {"concept", "creed"}:
        return "entity"
    if topic in {"legislation"}:
        return "constraint"
    return "entity"


def _resolve_representation_type(claim: ConceptClaim) -> str:
    value = str(claim.representation_type or "").strip().lower()
    if value:
        return value
    topic = str(claim.topic or "").strip().lower()
    if topic in {"legislation", "creed"}:
        return "shari"
    measure = str(claim.governing_measure or "").strip().lower()
    if measure in {"experimental", "experiment", "empirical", "quantitative"}:
        return "sensory"
    if measure in {"scriptural", "usuli", "fiqh", "qiyas_shari"}:
        return "shari"
    if measure in {"dalala"}:
        return "linguistic"
    return "symbolic"


def _evaluate_representational_eligibility(
    *,
    ontological_object_type: str,
    representation_type: str,
) -> tuple[bool, list[str]]:
    residuals: list[str] = []
    if representation_type not in _REPRESENTATION_TYPES:
        residuals.append("unsupported_data_type")
        return False, residuals
    allowed = _ALLOWED_REPRESENTATIONS_BY_OBJECT.get(ontological_object_type, set())
    if allowed and representation_type not in allowed:
        residuals.append("metric_extension_fallacy")
        return False, residuals
    return True, residuals


def _evaluate_metric_operator(
    *,
    claim: ConceptClaim,
    ontological_object_type: str,
    representation_type: str,
) -> dict[str, bool | list[str]]:
    residuals: list[str] = []
    normalized_measure = str(claim.governing_measure or "").strip().lower()
    normalized_domain = str(claim.domain or "").strip().lower()
    normalized_topic = str(claim.topic or "").strip().lower()
    normalized_relation = str(claim.relation_type or "").strip().lower()
    normalized_semantic = str(claim.semantic_type or "").strip().lower()
    normalized_inference = str(claim.inference_type or "").strip().lower()
    canonical_measure = _MEASURE_ALIASES.get(normalized_measure, normalized_measure)
    operator = _METRIC_OPERATORS.get(canonical_measure)
    if operator is None:
        return {"measure_ok": _is_governing_measure_valid(claim.domain, claim.governing_measure), "semantic_inference_ok": True, "certificate_allowed": True, "residuals": residuals}

    measure_ok = True
    semantic_inference_ok = True

    if normalized_domain not in operator.allowed_domains:
        measure_ok = False
        residuals.append("invalid_measure_domain")
    if normalized_topic not in operator.allowed_topics:
        measure_ok = False
        residuals.append("invalid_measure_topic")
    if ontological_object_type not in operator.existence_constraints:
        measure_ok = False
        residuals.append("metric_extension_fallacy")
    if representation_type not in operator.representation_constraints:
        measure_ok = False
        residuals.append("metric_extension_fallacy")
    if normalized_relation and normalized_relation not in operator.relation_constraints:
        semantic_inference_ok = False
        residuals.append("metric_extension_fallacy")
    if normalized_semantic and normalized_semantic not in operator.semantic_constraints:
        semantic_inference_ok = False
        residuals.append("metric_extension_fallacy")
    if normalized_inference and normalized_inference not in operator.inference_constraints:
        semantic_inference_ok = False
        residuals.append("metric_extension_fallacy")

    certificate_allowed = "certificate" in operator.certainty_constraints and measure_ok and semantic_inference_ok
    if str(claim.certainty_level or "").strip().lower() == "certificate" and not certificate_allowed:
        residuals.append("metric_certainty_capped")

    return {
        "measure_ok": measure_ok,
        "semantic_inference_ok": semantic_inference_ok,
        "certificate_allowed": certificate_allowed,
        "residuals": _unique_in_order(residuals),
    }


def _evaluate_semantic_layer_separation(
    *,
    claim: ConceptClaim,
    semantic_inference_gate: bool,
) -> dict[str, bool | list[str]]:
    residuals: list[str] = []
    normalized_evidence_basis = str(claim.evidence_basis_type or "").strip().lower()
    normalized_inference_basis = str(claim.inference_basis_type or "").strip().lower()
    normalized_judgment_basis = str(claim.judgment_basis_type or "").strip().lower()

    if normalized_judgment_basis in {"definition", "definitional"}:
        residuals.append("definition_as_judgment")
    if normalized_evidence_basis in {"interpretation", "interpretive"}:
        residuals.append("interpretation_as_evidence")
    if normalized_inference_basis in {"relation", "relational"}:
        residuals.append("relation_as_inference")
    if normalized_judgment_basis in {"semantic", "dalala"} and not semantic_inference_gate:
        residuals.append("dalala_without_gate")

    return {
        "semantic_layer_separation_ok": not residuals,
        "residuals": _unique_in_order(residuals),
    }


def _unique_in_order(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
