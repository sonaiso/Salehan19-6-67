"""Nabhani feature adapter for governed answer-birth ML examples."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


REALITY_KIND_TOKENS: tuple[str, ...] = (
    "observed",
    "artifact",
    "text",
    "experiment",
    "user_claim",
    "concept",
    "normative_claim",
    "unknown",
)
REALITY_STATUS_TOKENS: tuple[str, ...] = ("present", "inferred", "missing", "disputed", "not_applicable")
REALITY_ACCESS_MODE_TOKENS: tuple[str, ...] = ("direct", "trace", "source_text", "experiment", "user_report", "inferred", "none")
SOURCE_TYPE_TOKENS: tuple[str, ...] = (
    "direct_observation",
    "source_text",
    "user_input",
    "tool_output",
    "experiment",
    "repository_artifact",
    "prior_context",
    "none",
)
SOURCE_RANK_TOKENS: tuple[str, ...] = ("none", "weak", "ordinary", "governed", "proof_object")
SOURCE_ROLE_TOKENS: tuple[str, ...] = ("context", "evidence_candidate", "proof", "claim", "means", "none")
PRIOR_INFORMATION_KIND_TOKENS: tuple[str, ...] = (
    "none",
    "conversation_context",
    "project_context",
    "source_knowledge",
    "formal_axiom",
    "domain_rule",
)
PRIOR_INFORMATION_SUFFICIENCY_TOKENS: tuple[str, ...] = ("absent", "insufficient", "partial", "sufficient")
LINKING_TYPE_TOKENS: tuple[str, ...] = (
    "rational_link",
    "causal_link",
    "linguistic_link",
    "formal_link",
    "analogical_link",
    "invalid_link",
    "missing",
)
LINKING_VALIDITY_TOKENS: tuple[str, ...] = ("valid", "weak", "invalid", "missing")
CORRESPONDENCE_TYPE_TOKENS: tuple[str, ...] = ("direct_match", "partial_match", "inferred_match", "conflict", "unverified", "missing")
EVIDENCE_TYPE_TOKENS: tuple[str, ...] = (
    "none",
    "weak",
    "source_ref",
    "governed_trace",
    "proof_object",
    "normative_evidence",
    "empirical_evidence",
    "formal_proof",
)
EVIDENCE_SUFFICIENCY_TOKENS: tuple[str, ...] = ("absent", "insufficient", "partial", "sufficient", "governed")
METHOD_TYPE_TOKENS: tuple[str, ...] = ("rational", "scientific", "formal", "linguistic", "normative", "systemic")
JUDGMENT_DOMAIN_TOKENS: tuple[str, ...] = ("epistemic", "empirical", "formal", "linguistic", "normative", "legal", "shari", "worldview", "systemic")
CERTAINTY_RANK_TOKENS: tuple[str, ...] = ("zero", "possibility", "hypothesis", "weak_evidence", "strong_evidence", "certificate")
RANK_SOURCE_TOKENS: tuple[str, ...] = ("none", "trace_core_rank", "expected_final_judgment", "feature_annotation")
MISSING_FEATURE_TOKENS: tuple[str, ...] = ("reality", "source", "prior_information", "linking", "correspondence", "evidence")


@dataclass
class NabhaniFeatureValidationError:
    field: str
    message: str


@dataclass
class NabhaniFeatureValidationReport:
    valid: bool
    errors: list[NabhaniFeatureValidationError] = field(default_factory=list)


@dataclass
class NabhaniFeatureFrame:
    has_reality: bool
    reality_kind: str
    reality_status: str
    reality_access_mode: str
    has_source: bool
    source_type: str
    source_rank: str
    source_role: str
    has_prior_information: bool
    prior_information_kind: str
    prior_information_sufficiency: str
    has_linking: bool
    linking_type: str
    linking_validity: str
    has_correspondence: bool
    correspondence_type: str
    has_evidence: bool
    evidence_type: str
    evidence_sufficiency: str
    evidence_matches_claim_domain: bool
    method_type: str
    judgment_domain: str
    certainty_rank: str
    rank_source: str
    missing_features: list[str] = field(default_factory=list)
    feature_residuals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _token(value: object, *, default: str) -> str:
    token = str("" if value is None else value).strip().lower()
    return token or default


def _infer_judgment_domain(example: dict) -> str:
    output_kind = _token(example.get("mentality_frame", {}).get("output_kind"), default="epistemic")
    if output_kind == "descriptive":
        return "epistemic"
    if output_kind in JUDGMENT_DOMAIN_TOKENS:
        return output_kind
    return "epistemic"


def _infer_certainty_rank(example: dict, *, fallback: str = "zero") -> tuple[str, str]:
    feature_token = _token(example.get("nabhani_features", {}).get("certainty_rank"), default="")
    if feature_token in CERTAINTY_RANK_TOKENS:
        return feature_token, "feature_annotation"

    expected_final = _token(example.get("expected", {}).get("final_judgment"), default="")
    if expected_final in {"zero", "hypothesis", "certificate"}:
        return expected_final, "expected_final_judgment"

    trace_core = _token(example.get("thought_trace", {}).get("evidence_rank", {}).get("core"), default=fallback)
    if trace_core in CERTAINTY_RANK_TOKENS:
        return trace_core, "trace_core_rank"
    return fallback, "none"


def derive_nabhani_features_from_example(example: dict) -> NabhaniFeatureFrame:
    """Derive Nabhani features from an answer-birth training example."""
    feature_input = example.get("nabhani_features", {})
    consciousness = example.get("consciousness_frame", {})
    trace = example.get("thought_trace", {})
    expected = example.get("expected", {})
    method_type = _token(feature_input.get("method_type") or example.get("thinking_method", {}).get("method_type"), default="rational")
    judgment_domain = _token(feature_input.get("judgment_domain"), default=_infer_judgment_domain(example))
    certainty_rank, derived_rank_source = _infer_certainty_rank(example)

    has_reality = bool(feature_input.get("has_reality", bool(consciousness.get("reality_refs"))))
    has_source = bool(feature_input.get("has_source", bool(trace.get("evidence_refs")) or has_reality))
    has_prior_information = bool(feature_input.get("has_prior_information", bool(consciousness.get("prior_information_refs"))))
    has_linking = bool(feature_input.get("has_linking", bool(trace.get("trace_path_complete"))))
    has_correspondence = bool(feature_input.get("has_correspondence", bool(trace.get("trace_evidence_complete"))))
    has_evidence = bool(feature_input.get("has_evidence", bool(trace.get("evidence_refs"))))

    missing_features = list(feature_input.get("missing_features") or [])
    if not missing_features:
        if not has_reality:
            missing_features.append("reality")
        if not has_source:
            missing_features.append("source")
        if not has_prior_information:
            missing_features.append("prior_information")
        if not has_linking:
            missing_features.append("linking")
        if not has_correspondence:
            missing_features.append("correspondence")
        if not has_evidence:
            missing_features.append("evidence")

    feature_residuals = list(feature_input.get("feature_residuals") or [])
    if not feature_residuals:
        residual_map = {
            "reality": "missing_reality",
            "source": "missing_source",
            "prior_information": "missing_prior_information",
            "linking": "missing_linking",
            "correspondence": "missing_correspondence",
            "evidence": "missing_evidence",
        }
        for missing in missing_features:
            mapped = residual_map.get(missing)
            if mapped:
                feature_residuals.append(mapped)
    for token in expected.get("residuals", []) or []:
        normalized = _token(token, default="")
        if normalized and normalized.startswith("missing_") and normalized not in feature_residuals:
            feature_residuals.append(normalized)

    return NabhaniFeatureFrame(
        has_reality=has_reality,
        reality_kind=_token(feature_input.get("reality_kind"), default="unknown"),
        reality_status=_token(feature_input.get("reality_status"), default="present" if has_reality else "missing"),
        reality_access_mode=_token(feature_input.get("reality_access_mode"), default="trace" if has_reality else "none"),
        has_source=has_source,
        source_type=_token(feature_input.get("source_type"), default="repository_artifact" if has_source else "none"),
        source_rank=_token(feature_input.get("source_rank"), default="ordinary" if has_source else "none"),
        source_role=_token(feature_input.get("source_role"), default="evidence_candidate" if has_source else "none"),
        has_prior_information=has_prior_information,
        prior_information_kind=_token(feature_input.get("prior_information_kind"), default="project_context" if has_prior_information else "none"),
        prior_information_sufficiency=_token(
            feature_input.get("prior_information_sufficiency"), default="sufficient" if has_prior_information else "absent"
        ),
        has_linking=has_linking,
        linking_type=_token(feature_input.get("linking_type"), default="rational_link" if has_linking else "missing"),
        linking_validity=_token(feature_input.get("linking_validity"), default="valid" if has_linking else "missing"),
        has_correspondence=has_correspondence,
        correspondence_type=_token(feature_input.get("correspondence_type"), default="partial_match" if has_correspondence else "missing"),
        has_evidence=has_evidence,
        evidence_type=_token(feature_input.get("evidence_type"), default="source_ref" if has_evidence else "none"),
        evidence_sufficiency=_token(feature_input.get("evidence_sufficiency"), default="partial" if has_evidence else "absent"),
        evidence_matches_claim_domain=bool(feature_input.get("evidence_matches_claim_domain", True)),
        method_type=method_type,
        judgment_domain=judgment_domain,
        certainty_rank=certainty_rank,
        rank_source=_token(feature_input.get("rank_source"), default=derived_rank_source),
        missing_features=sorted(set(missing_features)),
        feature_residuals=sorted(set(feature_residuals)),
    )


def validate_nabhani_features(features: dict) -> NabhaniFeatureValidationReport:
    """Validate Nabhani features independently from the full example schema."""
    errors: list[NabhaniFeatureValidationError] = []

    def _require_token(field_name: str, allowed: tuple[str, ...]) -> str:
        token = _token(features.get(field_name), default="")
        if token not in allowed:
            errors.append(NabhaniFeatureValidationError(field_name, f"unrecognized token: {token or '<empty>'}"))
        return token

    for boolean_field in (
        "has_reality",
        "has_source",
        "has_prior_information",
        "has_linking",
        "has_correspondence",
        "has_evidence",
        "evidence_matches_claim_domain",
    ):
        if not isinstance(features.get(boolean_field), bool):
            errors.append(NabhaniFeatureValidationError(boolean_field, "field must be boolean"))

    has_reality = bool(features.get("has_reality"))
    has_source = bool(features.get("has_source"))
    has_prior_information = bool(features.get("has_prior_information"))
    has_linking = bool(features.get("has_linking"))
    has_correspondence = bool(features.get("has_correspondence"))
    has_evidence = bool(features.get("has_evidence"))

    reality_status = _require_token("reality_status", REALITY_STATUS_TOKENS)
    _require_token("reality_kind", REALITY_KIND_TOKENS)
    _require_token("reality_access_mode", REALITY_ACCESS_MODE_TOKENS)
    source_type = _require_token("source_type", SOURCE_TYPE_TOKENS)
    source_rank = _require_token("source_rank", SOURCE_RANK_TOKENS)
    source_role = _require_token("source_role", SOURCE_ROLE_TOKENS)
    prior_information_kind = _require_token("prior_information_kind", PRIOR_INFORMATION_KIND_TOKENS)
    prior_information_sufficiency = _require_token("prior_information_sufficiency", PRIOR_INFORMATION_SUFFICIENCY_TOKENS)
    linking_type = _require_token("linking_type", LINKING_TYPE_TOKENS)
    linking_validity = _require_token("linking_validity", LINKING_VALIDITY_TOKENS)
    correspondence_type = _require_token("correspondence_type", CORRESPONDENCE_TYPE_TOKENS)
    evidence_type = _require_token("evidence_type", EVIDENCE_TYPE_TOKENS)
    evidence_sufficiency = _require_token("evidence_sufficiency", EVIDENCE_SUFFICIENCY_TOKENS)
    _require_token("method_type", METHOD_TYPE_TOKENS)
    _require_token("judgment_domain", JUDGMENT_DOMAIN_TOKENS)
    _require_token("certainty_rank", CERTAINTY_RANK_TOKENS)
    _require_token("rank_source", RANK_SOURCE_TOKENS)

    missing_features = features.get("missing_features")
    if not isinstance(missing_features, list):
        errors.append(NabhaniFeatureValidationError("missing_features", "field must be a list"))
    else:
        for token in missing_features:
            normalized = _token(token, default="")
            if normalized not in MISSING_FEATURE_TOKENS:
                errors.append(NabhaniFeatureValidationError("missing_features", f"unsupported missing feature token: {token}"))

    feature_residuals = features.get("feature_residuals")
    if not isinstance(feature_residuals, list):
        errors.append(NabhaniFeatureValidationError("feature_residuals", "field must be a list"))

    if has_reality and reality_status == "missing":
        errors.append(NabhaniFeatureValidationError("reality_status", "reality_status cannot be missing when has_reality is true"))
    if (not has_reality) and reality_status == "present":
        errors.append(NabhaniFeatureValidationError("reality_status", "reality_status cannot be present when has_reality is false"))

    if not has_source and source_type != "none":
        errors.append(NabhaniFeatureValidationError("source_type", "source_type must be none when has_source is false"))
    if not has_source and source_rank != "none":
        errors.append(NabhaniFeatureValidationError("source_rank", "source_rank must be none when has_source is false"))
    if not has_source and source_role != "none":
        errors.append(NabhaniFeatureValidationError("source_role", "source_role must be none when has_source is false"))

    if not has_prior_information and prior_information_kind != "none":
        errors.append(
            NabhaniFeatureValidationError("prior_information_kind", "prior_information_kind must be none when has_prior_information is false")
        )
    if not has_prior_information and prior_information_sufficiency == "sufficient":
        errors.append(
            NabhaniFeatureValidationError(
                "prior_information_sufficiency",
                "prior_information_sufficiency cannot be sufficient when has_prior_information is false",
            )
        )

    if not has_linking and linking_type not in {"missing", "invalid_link"}:
        errors.append(NabhaniFeatureValidationError("linking_type", "linking_type must be missing or invalid_link when has_linking is false"))
    if not has_linking and linking_validity not in {"missing", "invalid"}:
        errors.append(NabhaniFeatureValidationError("linking_validity", "linking_validity must be missing or invalid when has_linking is false"))

    if not has_correspondence and correspondence_type not in {"missing", "unverified", "conflict"}:
        errors.append(
            NabhaniFeatureValidationError(
                "correspondence_type",
                "correspondence_type must be missing/unverified/conflict when has_correspondence is false",
            )
        )

    if not has_evidence and evidence_type != "none":
        errors.append(NabhaniFeatureValidationError("evidence_type", "evidence_type must be none when has_evidence is false"))
    if not has_evidence and evidence_sufficiency not in {"absent", "insufficient"}:
        errors.append(
            NabhaniFeatureValidationError(
                "evidence_sufficiency",
                "evidence_sufficiency must be absent/insufficient when has_evidence is false",
            )
        )

    return NabhaniFeatureValidationReport(valid=not errors, errors=errors)


def _token_to_id(token: str, choices: tuple[str, ...]) -> int:
    """Map a validated token to a stable index."""
    return choices.index(token)


def nabhani_features_to_training_vector(features: dict) -> dict:
    """Export stable numeric training vector from validated Nabhani features."""
    report = validate_nabhani_features(features)
    if not report.valid:
        message = "; ".join(f"{error.field}: {error.message}" for error in report.errors)
        raise ValueError(f"invalid nabhani features: {message}")

    normalized = {
        "has_reality": int(bool(features["has_reality"])),
        "has_source": int(bool(features["has_source"])),
        "has_prior_information": int(bool(features["has_prior_information"])),
        "has_linking": int(bool(features["has_linking"])),
        "has_correspondence": int(bool(features["has_correspondence"])),
        "has_evidence": int(bool(features["has_evidence"])),
        "method_type": _token_to_id(_token(features["method_type"], default="rational"), METHOD_TYPE_TOKENS),
        "judgment_domain": _token_to_id(_token(features["judgment_domain"], default="epistemic"), JUDGMENT_DOMAIN_TOKENS),
        "certainty_rank": _token_to_id(_token(features["certainty_rank"], default="zero"), CERTAINTY_RANK_TOKENS),
    }
    return normalized
