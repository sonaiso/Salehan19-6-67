"""Validator for governed answer-birth ML training examples."""
from __future__ import annotations

from dataclasses import dataclass, field

import jsonschema

from mcd.core.public_judgment import collapse_to_public_judgment
from mcd.ml.dataset_schema import (
    CORE_EVIDENCE_RANK_TOKENS,
    THINKING_EVIDENCE_RANK_TOKENS,
    load_answer_birth_training_example_schema,
)
from mcd.thinking.methods import thinking_rank_to_core_epistemic_rank


@dataclass
class ExampleValidationError:
    field: str
    message: str


@dataclass
class ExampleValidationReport:
    valid: bool
    errors: list[ExampleValidationError] = field(default_factory=list)


def validate_training_example(example: dict, *, schema: dict | None = None) -> ExampleValidationReport:
    """Validate a single training example against schema + governance rules."""
    errors: list[ExampleValidationError] = []
    active_schema = schema or load_answer_birth_training_example_schema()

    try:
        jsonschema.Draft202012Validator.check_schema(active_schema)
    except jsonschema.SchemaError as exc:
        errors.append(ExampleValidationError(field="schema", message=exc.message))
        return ExampleValidationReport(valid=False, errors=errors)

    validator = jsonschema.Draft202012Validator(active_schema)
    for err in validator.iter_errors(example):
        field = ".".join(str(part) for part in err.absolute_path) or "schema"
        errors.append(ExampleValidationError(field=field, message=err.message))

    expected = example.get("expected", {})
    birth = collapse_to_public_judgment(expected.get("birth_judgment", ""))
    final = collapse_to_public_judgment(expected.get("final_judgment", ""))
    requested = collapse_to_public_judgment(example.get("requested_public_judgment", ""))

    if requested == "hypothesis" and (birth == "certificate" or final == "certificate"):
        errors.append(ExampleValidationError("expected.birth_judgment", "silent promotion from hypothesis to certificate"))

    trace = example.get("thought_trace", {})
    for field_name in ("trace_path_complete", "trace_evidence_complete", "trace_certificate_complete"):
        if not isinstance(trace.get(field_name), bool):
            errors.append(ExampleValidationError(f"thought_trace.{field_name}", "trace completeness fields must be explicit booleans"))

    evidence_rank = trace.get("evidence_rank", {})
    thinking_rank = str(evidence_rank.get("thinking", "")).strip().lower()
    core_rank = str(evidence_rank.get("core", "")).strip().lower()
    if thinking_rank not in THINKING_EVIDENCE_RANK_TOKENS:
        errors.append(ExampleValidationError("thought_trace.evidence_rank.thinking", "unrecognized thinking evidence rank"))
    if core_rank not in CORE_EVIDENCE_RANK_TOKENS:
        errors.append(ExampleValidationError("thought_trace.evidence_rank.core", "unrecognized core evidence rank"))

    required_rank = str(example.get("thinking_method", {}).get("required_evidence_rank", "")).strip().lower()
    if required_rank not in THINKING_EVIDENCE_RANK_TOKENS and required_rank not in CORE_EVIDENCE_RANK_TOKENS:
        errors.append(ExampleValidationError("thinking_method.required_evidence_rank", "required_evidence_rank token is not recognized"))

    if thinking_rank in THINKING_EVIDENCE_RANK_TOKENS and core_rank in CORE_EVIDENCE_RANK_TOKENS:
        mapped_core = thinking_rank_to_core_epistemic_rank(thinking_rank).name.lower()
        if mapped_core != core_rank:
            errors.append(ExampleValidationError("thought_trace.evidence_rank", "thinking/core evidence rank mapping mismatch"))

    means = example.get("thinking_means", {})
    if bool(means.get("can_issue_judgment")):
        errors.append(ExampleValidationError("thinking_means.can_issue_judgment", "means cannot issue judgment"))

    blockers = expected.get("blockers")
    residuals = expected.get("residuals")
    if not isinstance(blockers, list):
        errors.append(ExampleValidationError("expected.blockers", "blockers must be an explicit list"))
    if not isinstance(residuals, list):
        errors.append(ExampleValidationError("expected.residuals", "residuals must be an explicit list"))

    labels = {str(item).strip().lower() for item in (blockers or []) + (residuals or [])}
    has_proof_object = bool((example.get("proof_object_ref") or "").strip())
    has_governance_gate = bool(example.get("governance_gate_passed"))
    has_reverse_trace = bool((example.get("reverse_trace_ref") or "").strip())
    if birth == "certificate" or final == "certificate":
        if not has_proof_object and "certificate_without_proof_object" not in labels:
            errors.append(
                ExampleValidationError(
                    "expected.residuals",
                    "certificate samples without proof_object_ref must preserve certificate_without_proof_object",
                )
            )
        if not has_governance_gate and "certificate_without_governance_gate" not in labels:
            errors.append(
                ExampleValidationError(
                    "expected.residuals",
                    "certificate samples without governance_gate_passed must preserve certificate_without_governance_gate",
                )
            )
        if not has_reverse_trace and "certificate_without_reverse_trace" not in labels:
            errors.append(
                ExampleValidationError(
                    "expected.residuals",
                    "certificate samples without reverse_trace_ref must preserve certificate_without_reverse_trace",
                )
            )

    method_type = str(example.get("thinking_method", {}).get("method_type", "")).strip().lower()
    output_kind = str(example.get("mentality_frame", {}).get("output_kind", "")).strip().lower()
    blockers_set = {str(item).strip().lower() for item in blockers or []}
    if method_type == "scientific" and output_kind == "worldview":
        if "scientific_method_as_worldview" not in blockers_set:
            errors.append(ExampleValidationError("expected.blockers", "scientific worldview output must carry blocker"))
    if method_type == "scientific" and output_kind in {"normative", "legal", "shari"}:
        if "scientific_method_as_normative_judgment" not in blockers_set:
            errors.append(ExampleValidationError("expected.blockers", "scientific normative output must carry blocker"))

    if "birth_judgment" not in expected or "final_judgment" not in expected:
        errors.append(ExampleValidationError("expected", "birth_judgment and final_judgment must both exist"))

    return ExampleValidationReport(valid=not errors, errors=errors)
