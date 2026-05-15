"""Golden Prior Knowledge Registry for governed baseline decisions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


DEFAULT_GOLDEN_PRIOR_DIR = (
    Path(__file__).resolve().parents[3] / "examples" / "golden_prior_knowledge"
)


class PriorScope(str, Enum):
    FORMAL = "FORMAL"
    COMPUTATIONAL = "COMPUTATIONAL"
    EMPIRICAL = "EMPIRICAL"
    LINGUISTIC = "LINGUISTIC"
    CONTEXTUAL = "CONTEXTUAL"


class CertaintyLevel(str, Enum):
    CONSTITUTIONAL_GOVERNANCE = "CONSTITUTIONAL_GOVERNANCE"
    FORMAL_CERTAINTY = "FORMAL_CERTAINTY"
    COMPUTATIONAL_CONTRACT = "COMPUTATIONAL_CONTRACT"
    EMPIRICAL_UNDER_CONDITIONS = "EMPIRICAL_UNDER_CONDITIONS"
    LINGUISTIC_NORMATIVE = "LINGUISTIC_NORMATIVE"
    CONTEXTUAL_USAGE = "CONTEXTUAL_USAGE"
    HYPOTHESIS_PRIOR = "HYPOTHESIS_PRIOR"


class GoldenRuleMaturityLevel(str, Enum):
    DRAFT_PRIOR = "DRAFT_PRIOR"
    SCOPED_PRIOR = "SCOPED_PRIOR"
    GOVERNING_PRIOR = "GOVERNING_PRIOR"
    GOLDEN_RULE_CANDIDATE = "GOLDEN_RULE_CANDIDATE"
    GOLDEN_RULE = "GOLDEN_RULE"


@dataclass(frozen=True)
class EvidenceRequirement:
    required_items: tuple[str, ...]
    all_required: bool = True
    notes: str = ""


@dataclass(frozen=True)
class CertificateBlocker:
    blocker_id: str
    description: str
    match_any: tuple[str, ...] = ()
    blocks_levels: tuple[str, ...] = ("CERTIFICATE", "CERTIFICATE_CANDIDATE")


@dataclass(frozen=True)
class ResidualExpectation:
    residual_id: str
    description: str
    local_only: bool = False
    blocks_certificate: bool = True


@dataclass(frozen=True)
class ReverseTraceRequirement:
    required: bool
    required_fields: tuple[str, ...] = ("input", "candidate", "evidence", "decision_path")


@dataclass(frozen=True)
class PriorRule:
    rule_id: str
    domain: str
    layer: str
    claim: str
    scope: PriorScope
    certainty_level: CertaintyLevel
    required_evidence: EvidenceRequirement
    certificate_blockers: tuple[CertificateBlocker, ...]
    expected_residuals: tuple[ResidualExpectation, ...]
    forbidden_transitions: tuple[str, ...]
    reverse_trace_requirements: ReverseTraceRequirement
    examples: tuple[str, ...] = ()
    test_refs: tuple[str, ...] = ()
    case_refs: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    is_golden_rule: bool = False
    maturity_level: GoldenRuleMaturityLevel = GoldenRuleMaturityLevel.DRAFT_PRIOR
    scope_complete: bool | None = None
    evidence_requirements_complete: bool | None = None
    certificate_blockers_complete: bool | None = None
    residual_expectations_defined: bool | None = None
    forbidden_transitions_defined: bool | None = None
    reverse_trace_requirements_defined: bool | None = None
    concept_measurement_capable: bool | None = None
    applicability_conditions: tuple[str, ...] = ()
    known_exceptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class PriorValidationResult:
    rule_id: str
    valid: bool
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class GoldenRuleQualificationResult:
    qualified: bool
    maturity_level: GoldenRuleMaturityLevel
    missing_requirements: tuple[str, ...]
    blocking_issues: tuple[str, ...]
    warnings: tuple[str, ...]
    can_block_certificate: bool
    can_measure_new_concepts: bool


@dataclass
class PriorRegistry:
    rules: tuple[PriorRule, ...] = field(default_factory=tuple)

    def add_rule(self, rule: PriorRule) -> None:
        self.rules = (*self.rules, rule)

    def find_rules(
        self,
        *,
        domain: str | None = None,
        layer: str | None = None,
        claim: str | None = None,
    ) -> list[PriorRule]:
        claim_norm = claim.lower().strip() if isinstance(claim, str) else None
        matched: list[PriorRule] = []
        for rule in self.rules:
            if domain is not None and rule.domain != domain:
                continue
            if layer is not None and rule.layer != layer:
                continue
            if claim_norm:
                if claim_norm != rule.claim.lower().strip() and claim_norm not in rule.claim.lower():
                    continue
            matched.append(rule)
        return matched

    def find_case_rules(self, case: dict[str, object]) -> list[PriorRule]:
        domain = str(case.get("domain", "")).strip()
        case_id = str(case.get("id", "")).strip()
        text = " ".join(
            [
                str(case.get("input", "")),
                " ".join(case.get("constraints", []) if isinstance(case.get("constraints"), list) else []),
                str(case.get("notes", "")),
            ]
        ).lower()
        direct = [
            rule
            for rule in self.rules
            if rule.domain == domain and (
                (case_id and case_id in set(rule.case_refs))
                or (rule.keywords and any(keyword.lower() in text for keyword in rule.keywords))
            )
        ]
        if direct:
            return direct
        return self.find_rules(domain=domain)

    def qualified_rules(
        self,
        *,
        min_maturity: GoldenRuleMaturityLevel = GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE,
    ) -> list[PriorRule]:
        rank = {
            GoldenRuleMaturityLevel.DRAFT_PRIOR: 0,
            GoldenRuleMaturityLevel.SCOPED_PRIOR: 1,
            GoldenRuleMaturityLevel.GOVERNING_PRIOR: 2,
            GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE: 3,
            GoldenRuleMaturityLevel.GOLDEN_RULE: 4,
        }
        threshold = rank[min_maturity]
        out: list[PriorRule] = []
        for rule in self.rules:
            qualification = qualify_golden_rule(rule)
            if rank[qualification.maturity_level] >= threshold:
                out.append(rule)
        return out

    def validate(self) -> dict[str, list[str]]:
        errors: dict[str, list[str]] = {}
        for rule in self.rules:
            result = validate_prior_rule(rule)
            if not result.valid:
                errors[rule.rule_id] = list(result.errors)
        return errors


_REQUIRED_FORBIDDEN_HINTS = {
    "score_only_certificate",
    "CI_PASS_TO_CERTIFICATE",
    "SMOKE_ONLY_TO_FIRE_CERTIFICATE",
    "TRIANGLE_WITHOUT_GEOMETRY_SCOPE_TO_CERTIFICATE",
}


def _has_test_or_benchmark_ref(rule: PriorRule) -> bool:
    return bool(rule.test_refs or rule.case_refs or rule.examples)


def qualify_golden_rule(rule: PriorRule) -> GoldenRuleQualificationResult:
    missing: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    scope_complete = rule.scope_complete if rule.scope_complete is not None else isinstance(rule.scope, PriorScope)
    certainty_explicit = isinstance(rule.certainty_level, CertaintyLevel)
    evidence_complete = (
        rule.evidence_requirements_complete
        if rule.evidence_requirements_complete is not None
        else bool(rule.required_evidence.required_items)
    )
    certificate_blockers_complete = (
        rule.certificate_blockers_complete
        if rule.certificate_blockers_complete is not None
        else bool(rule.certificate_blockers)
    )
    residuals_defined = (
        rule.residual_expectations_defined
        if rule.residual_expectations_defined is not None
        else bool(rule.expected_residuals)
    )
    forbidden_defined = (
        rule.forbidden_transitions_defined
        if rule.forbidden_transitions_defined is not None
        else bool(rule.forbidden_transitions)
    )
    reverse_trace_defined = (
        rule.reverse_trace_requirements_defined
        if rule.reverse_trace_requirements_defined is not None
        else bool(rule.reverse_trace_requirements.required)
    )
    has_tests = _has_test_or_benchmark_ref(rule)

    if not scope_complete:
        missing.append("scope")
        blockers.append("scope is required before any golden governance")
    if not certainty_explicit:
        missing.append("certainty_level")
        blockers.append("certainty level must be explicit")
    if not evidence_complete:
        missing.append("required_evidence")
        blockers.append("evidence requirements must be explicit")
    if not certificate_blockers_complete:
        missing.append("certificate_blockers")
        blockers.append("certificate blockers are required to govern certificate")
    if not residuals_defined:
        missing.append("expected_residuals")
        warnings.append("residual expectations missing; uncertainty governance is incomplete")
    if not forbidden_defined:
        missing.append("forbidden_transitions")
        warnings.append("forbidden transitions are not explicit")
    if not reverse_trace_defined:
        missing.append("reverse_trace_requirements")
        blockers.append("reverse trace requirements are mandatory for governed ascent")
    if not has_tests:
        missing.append("test_cases")
        warnings.append("no test/benchmark reference; rule cannot mature to GOLDEN_RULE")

    maturity = GoldenRuleMaturityLevel.DRAFT_PRIOR
    if scope_complete:
        maturity = GoldenRuleMaturityLevel.SCOPED_PRIOR
    if scope_complete and certainty_explicit and evidence_complete:
        maturity = GoldenRuleMaturityLevel.GOVERNING_PRIOR
    if (
        scope_complete
        and certainty_explicit
        and evidence_complete
        and certificate_blockers_complete
        and forbidden_defined
        and residuals_defined
        and reverse_trace_defined
    ):
        maturity = GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE
    if maturity == GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE and has_tests:
        maturity = GoldenRuleMaturityLevel.GOLDEN_RULE

    if rule.maturity_level != GoldenRuleMaturityLevel.DRAFT_PRIOR:
        maturity = rule.maturity_level

    can_block_certificate = certificate_blockers_complete and forbidden_defined
    concept_measurement_capable = (
        rule.concept_measurement_capable
        if rule.concept_measurement_capable is not None
        else (
            scope_complete
            and evidence_complete
            and forbidden_defined
            and reverse_trace_defined
            and can_block_certificate
        )
    )

    qualified = maturity in {
        GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE,
        GoldenRuleMaturityLevel.GOLDEN_RULE,
    }
    if qualified and not concept_measurement_capable:
        qualified = False
        blockers.append("concept measurement capability is required for golden qualification")

    return GoldenRuleQualificationResult(
        qualified=qualified,
        maturity_level=maturity,
        missing_requirements=tuple(dict.fromkeys(missing)),
        blocking_issues=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        can_block_certificate=can_block_certificate,
        can_measure_new_concepts=concept_measurement_capable,
    )


def validate_prior_rule(rule: PriorRule) -> PriorValidationResult:
    errors: list[str] = []
    if not rule.rule_id.strip():
        errors.append("rule_id is required")
    if not rule.domain.strip():
        errors.append("domain is required")
    if not rule.layer.strip():
        errors.append("layer is required")
    if not rule.claim.strip():
        errors.append("claim is required")
    if not isinstance(rule.scope, PriorScope):
        errors.append("scope must be PriorScope")
    if not isinstance(rule.certainty_level, CertaintyLevel):
        errors.append("certainty_level must be CertaintyLevel")
    if not rule.required_evidence.required_items:
        errors.append("required_evidence.required_items must be non-empty")
    if not rule.certificate_blockers:
        errors.append("certificate_blockers must be explicit")
    if not rule.reverse_trace_requirements.required:
        errors.append("reverse_trace_requirements.required must be true for governed prior rules")
    forbidden = set(rule.forbidden_transitions)
    if "score_only_certificate" in rule.claim.lower() and "score_only_certificate" not in forbidden:
        errors.append("score-only rules must explicitly forbid score_only_certificate")
    if any(hint in forbidden for hint in _REQUIRED_FORBIDDEN_HINTS):
        pass
    return PriorValidationResult(rule_id=rule.rule_id, valid=not errors, errors=tuple(errors))


def _load_requirement(raw: object) -> EvidenceRequirement:
    if not isinstance(raw, dict):
        raise ValueError("required_evidence must be an object")
    items = raw.get("required_items", [])
    if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
        raise ValueError("required_evidence.required_items must be a list[str]")
    return EvidenceRequirement(
        required_items=tuple(items),
        all_required=bool(raw.get("all_required", True)),
        notes=str(raw.get("notes", "")),
    )


def _load_blockers(raw: object) -> tuple[CertificateBlocker, ...]:
    if not isinstance(raw, list):
        raise ValueError("certificate_blockers must be a list")
    blockers: list[CertificateBlocker] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("certificate_blockers entries must be objects")
        blockers.append(
            CertificateBlocker(
                blocker_id=str(item.get("blocker_id", "")),
                description=str(item.get("description", "")),
                match_any=tuple(item.get("match_any", []) if isinstance(item.get("match_any"), list) else []),
                blocks_levels=tuple(
                    item.get("blocks_levels", ["CERTIFICATE", "CERTIFICATE_CANDIDATE"])
                    if isinstance(item.get("blocks_levels"), list)
                    else ["CERTIFICATE", "CERTIFICATE_CANDIDATE"]
                ),
            )
        )
    return tuple(blockers)


def _load_residuals(raw: object) -> tuple[ResidualExpectation, ...]:
    if not isinstance(raw, list):
        raise ValueError("expected_residuals must be a list")
    residuals: list[ResidualExpectation] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("expected_residuals entries must be objects")
        residuals.append(
            ResidualExpectation(
                residual_id=str(item.get("residual_id", "")),
                description=str(item.get("description", "")),
                local_only=bool(item.get("local_only", False)),
                blocks_certificate=bool(item.get("blocks_certificate", True)),
            )
        )
    return tuple(residuals)


def _load_reverse_trace_requirement(raw: object) -> ReverseTraceRequirement:
    if not isinstance(raw, dict):
        raise ValueError("reverse_trace_requirements must be an object")
    fields = raw.get("required_fields", ["input", "candidate", "evidence", "decision_path"])
    if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
        raise ValueError("reverse_trace_requirements.required_fields must be list[str]")
    return ReverseTraceRequirement(required=bool(raw.get("required", True)), required_fields=tuple(fields))


def _as_maturity(raw: object) -> GoldenRuleMaturityLevel:
    value = str(raw or GoldenRuleMaturityLevel.DRAFT_PRIOR.value)
    return GoldenRuleMaturityLevel(value)


def _parse_rule(raw: dict[str, object]) -> PriorRule:
    return PriorRule(
        rule_id=str(raw.get("rule_id", "")),
        domain=str(raw.get("domain", "")),
        layer=str(raw.get("layer", "")),
        claim=str(raw.get("claim", "")),
        scope=PriorScope(str(raw.get("scope", "CONTEXTUAL"))),
        certainty_level=CertaintyLevel(str(raw.get("certainty_level", "HYPOTHESIS_PRIOR"))),
        required_evidence=_load_requirement(raw.get("required_evidence", {})),
        certificate_blockers=_load_blockers(raw.get("certificate_blockers", [])),
        expected_residuals=_load_residuals(raw.get("expected_residuals", [])),
        forbidden_transitions=tuple(
            raw.get("forbidden_transitions", []) if isinstance(raw.get("forbidden_transitions"), list) else []
        ),
        reverse_trace_requirements=_load_reverse_trace_requirement(raw.get("reverse_trace_requirements", {})),
        examples=tuple(raw.get("examples", []) if isinstance(raw.get("examples"), list) else []),
        test_refs=tuple(raw.get("test_refs", []) if isinstance(raw.get("test_refs"), list) else []),
        case_refs=tuple(raw.get("case_refs", []) if isinstance(raw.get("case_refs"), list) else []),
        keywords=tuple(raw.get("keywords", []) if isinstance(raw.get("keywords"), list) else []),
        is_golden_rule=bool(raw.get("is_golden_rule", False)),
        maturity_level=_as_maturity(raw.get("maturity_level", GoldenRuleMaturityLevel.DRAFT_PRIOR.value)),
        scope_complete=raw.get("scope_complete") if isinstance(raw.get("scope_complete"), bool) else None,
        evidence_requirements_complete=(
            raw.get("evidence_requirements_complete")
            if isinstance(raw.get("evidence_requirements_complete"), bool)
            else None
        ),
        certificate_blockers_complete=(
            raw.get("certificate_blockers_complete")
            if isinstance(raw.get("certificate_blockers_complete"), bool)
            else None
        ),
        residual_expectations_defined=(
            raw.get("residual_expectations_defined")
            if isinstance(raw.get("residual_expectations_defined"), bool)
            else None
        ),
        forbidden_transitions_defined=(
            raw.get("forbidden_transitions_defined")
            if isinstance(raw.get("forbidden_transitions_defined"), bool)
            else None
        ),
        reverse_trace_requirements_defined=(
            raw.get("reverse_trace_requirements_defined")
            if isinstance(raw.get("reverse_trace_requirements_defined"), bool)
            else None
        ),
        concept_measurement_capable=(
            raw.get("concept_measurement_capable")
            if isinstance(raw.get("concept_measurement_capable"), bool)
            else None
        ),
        applicability_conditions=tuple(
            raw.get("applicability_conditions", [])
            if isinstance(raw.get("applicability_conditions"), list)
            else []
        ),
        known_exceptions=tuple(raw.get("known_exceptions", []) if isinstance(raw.get("known_exceptions"), list) else []),
    )


def load_prior_rules_file(path: Path) -> list[PriorRule]:
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, list):
        raise ValueError(f"Expected list of rules in {path}")
    rules = [_parse_rule(item) for item in payload if isinstance(item, dict)]
    if len(rules) != len(payload):
        raise ValueError(f"All entries in {path} must be objects")
    return rules


def load_golden_prior_registry(
    prior_dir: Path = DEFAULT_GOLDEN_PRIOR_DIR,
) -> PriorRegistry:
    registry = PriorRegistry()
    for path in sorted(prior_dir.glob("*.json")):
        with path.open(encoding="utf-8") as fh:
            payload = json.load(fh)
        if not (
            isinstance(payload, list)
            and payload
            and all(isinstance(item, dict) and "rule_id" in item for item in payload)
        ):
            continue
        for rule in [_parse_rule(item) for item in payload]:
            registry.add_rule(rule)
    return registry


def evaluate_case_against_priors(
    case: dict[str, object],
    rules: list[PriorRule],
) -> tuple[set[str], set[str], set[str], list[str]]:
    case_evidence = set(case.get("required_evidence", []) if isinstance(case.get("required_evidence"), list) else [])
    case_tokens: set[str] = set()
    for key in ("constraints", "expected_residuals", "forbidden_decisions"):
        value = case.get(key)
        if isinstance(value, list):
            case_tokens.update(str(item) for item in value)
    notes_blob = " ".join(
        [str(case.get("id", "")), str(case.get("input", "")), str(case.get("notes", ""))]
    ).lower()

    prior_missing: set[str] = set()
    prior_blocking: set[str] = set()
    prior_rule_ids: set[str] = set()
    error_tags: list[str] = []

    for rule in rules:
        prior_rule_ids.add(rule.rule_id)

        required = set(rule.required_evidence.required_items)
        missing_items = required - case_evidence
        if missing_items:
            prior_missing.add(rule.rule_id)

        for blocker in rule.certificate_blockers:
            hit = any(token in case_tokens for token in blocker.match_any)
            if not hit and blocker.match_any:
                hit = any(token.lower() in notes_blob for token in blocker.match_any)
            if hit:
                prior_blocking.add(blocker.blocker_id)

        for expected in rule.expected_residuals:
            if expected.residual_id not in case_tokens:
                if expected.residual_id and expected.residual_id.lower() in notes_blob:
                    continue
                error_tags.append(f"prior_expected_residual_missing:{expected.residual_id}")

    for rule_id in sorted(prior_missing):
        error_tags.append(f"prior_missing:{rule_id}")
    for blocker_id in sorted(prior_blocking):
        error_tags.append(f"prior_blocking:{blocker_id}")

    return prior_missing, prior_blocking, prior_rule_ids, error_tags
