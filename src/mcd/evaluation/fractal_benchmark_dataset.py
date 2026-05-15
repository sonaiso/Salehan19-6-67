"""Fractal governance benchmark dataset loader/validator for PR #105."""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_CASE_FIELDS: tuple[str, ...] = (
    "id",
    "domain",
    "input",
    "candidates",
    "constraints",
    "required_evidence",
    "expected_residuals",
    "forbidden_decisions",
    "allowed_decision_level",
    "reverse_trace_required",
    "notes",
)

ALLOWED_DECISION_LEVELS: tuple[str, ...] = (
    "ZERO",
    "HYPOTHESIS",
    "STRONG",
    "CERTIFICATE_CANDIDATE",
    "CERTIFICATE",
)

REQUIRED_CERTIFICATE_OBLIGATIONS: tuple[str, ...] = (
    "proof_object",
    "governance_gate_passed",
    "reverse_trace_complete",
    "evidence_complete",
    "no_blocking_residual",
)

DOMAIN_FILES: dict[str, str] = {
    "arabic_language": "arabic_language.json",
    "mathematics": "mathematics.json",
    "physical_reality": "physical_reality.json",
    "coding_pr_governance": "coding_pr_governance.json",
}

DEFAULT_BENCHMARK_DIR = (
    Path(__file__).resolve().parents[3] / "examples" / "fractal_governance_benchmarks"
)


def _all_str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _certificate_obligations_explicitly_satisfied(case: dict[str, object]) -> bool:
    obligations = case.get("certificate_obligations")
    if not isinstance(obligations, dict):
        return False
    if any(not isinstance(obligations.get(key), bool) for key in REQUIRED_CERTIFICATE_OBLIGATIONS):
        return False
    return all(bool(obligations[key]) for key in REQUIRED_CERTIFICATE_OBLIGATIONS)


def load_domain_cases(
    domain: str,
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
) -> list[dict[str, object]]:
    if domain not in DOMAIN_FILES:
        raise ValueError(f"Unsupported domain '{domain}'")
    path = dataset_dir / DOMAIN_FILES[domain]
    with path.open(encoding="utf-8") as fh:
        rows = json.load(fh)
    if not isinstance(rows, list):
        raise ValueError(f"Expected list of cases in {path}")
    return rows


def load_all_domain_cases(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
) -> dict[str, list[dict[str, object]]]:
    return {domain: load_domain_cases(domain, dataset_dir=dataset_dir) for domain in DOMAIN_FILES}


def iter_all_cases(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
) -> list[dict[str, object]]:
    all_cases: list[dict[str, object]] = []
    for rows in load_all_domain_cases(dataset_dir=dataset_dir).values():
        all_cases.extend(rows)
    return all_cases


def validate_case(case: dict[str, object]) -> list[str]:
    errors: list[str] = []

    missing = [field for field in REQUIRED_CASE_FIELDS if field not in case]
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
        return errors

    if not isinstance(case["id"], str) or not case["id"].strip():
        errors.append("id must be a non-empty string")
    if not isinstance(case["domain"], str) or case["domain"] not in DOMAIN_FILES:
        errors.append("domain must be one of benchmark domains")
    if not isinstance(case["input"], str) or not case["input"].strip():
        errors.append("input must be a non-empty string")

    for key in (
        "candidates",
        "constraints",
        "required_evidence",
        "expected_residuals",
        "forbidden_decisions",
    ):
        if not _all_str_list(case[key]):
            errors.append(f"{key} must be a list of strings")

    allowed_level = case["allowed_decision_level"]
    if allowed_level not in ALLOWED_DECISION_LEVELS:
        errors.append(
            "allowed_decision_level must be one of "
            + ", ".join(ALLOWED_DECISION_LEVELS)
        )

    reverse_trace_required = case["reverse_trace_required"]
    if not isinstance(reverse_trace_required, bool):
        errors.append("reverse_trace_required must be bool")
    elif allowed_level in {"STRONG", "CERTIFICATE_CANDIDATE"} and not reverse_trace_required:
        errors.append("STRONG/CERTIFICATE_CANDIDATE cases require reverse_trace_required=true")

    if not isinstance(case["notes"], str) or not case["notes"].strip():
        errors.append("notes must be a non-empty string")

    obligations_satisfied = _certificate_obligations_explicitly_satisfied(case)
    residuals = case.get("expected_residuals", [])
    required_evidence = case.get("required_evidence", [])

    obligations_incomplete = (
        not obligations_satisfied
        or not reverse_trace_required
        or not isinstance(required_evidence, list)
        or len(required_evidence) == 0
        or (isinstance(residuals, list) and len(residuals) > 0)
    )

    forbidden_decisions = case.get("forbidden_decisions", [])
    if isinstance(forbidden_decisions, list):
        if obligations_incomplete and "CERTIFICATE" not in forbidden_decisions:
            errors.append(
                "CERTIFICATE must be forbidden when evidence/trace/residual obligations are incomplete"
            )
    else:
        errors.append("forbidden_decisions must be a list of strings")

    if allowed_level == "CERTIFICATE" and not obligations_satisfied:
        errors.append("CERTIFICATE level requires explicit certificate obligations")

    return errors


def validate_all_cases(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
) -> dict[str, list[str]]:
    errors_by_id: dict[str, list[str]] = {}
    seen_ids: set[str] = set()

    for case in iter_all_cases(dataset_dir=dataset_dir):
        case_id = str(case.get("id", "MISSING_ID"))
        case_errors = validate_case(case)
        if case_id in seen_ids:
            case_errors.append("duplicate case id")
        seen_ids.add(case_id)
        if case_errors:
            errors_by_id[case_id] = case_errors

    return errors_by_id


def benchmark_dataset_summary(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
) -> dict[str, object]:
    loaded = load_all_domain_cases(dataset_dir=dataset_dir)
    return {
        "theorem_status": "STRONG_HYPOTHESIS",
        "domains": sorted(list(loaded.keys())),
        "counts": {domain: len(cases) for domain, cases in loaded.items()},
        "total_cases": sum(len(cases) for cases in loaded.values()),
    }
