"""Prior-aware baseline ablation runner for benchmark dataset #108."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from mcd.evaluation.fractal_baseline_comparison import (
    DECISION_LEVELS,
    GovernedProtocolBaseline,
    _compute_metrics,
)
from mcd.evaluation.fractal_benchmark_dataset import DEFAULT_BENCHMARK_DIR, iter_all_cases
from mcd.knowledge.golden_prior_registry import (
    GoldenRuleMaturityLevel,
    PriorRegistry,
    load_golden_prior_registry,
    qualify_golden_rule,
)

LEVEL_SCORE: dict[str, int] = {level: index for index, level in enumerate(DECISION_LEVELS)}
_CERT_ASCENT_LEVELS = {"CERTIFICATE_CANDIDATE", "CERTIFICATE"}
_FINAL_JUDGMENTS = ["ZERO", "HYPOTHESIS", "CERTIFICATE"]

MODE_WITHOUT_PRIORS = "without_prior_registry"
MODE_WITH_ALL_PRIORS = "with_all_priors"
MODE_WITH_GOLDEN_PRIORS = MODE_WITH_ALL_PRIORS
MODE_WITH_QUALIFIED_GOLDEN_RULES = "with_qualified_golden_rules"
MODE_PRIOR_DISABLED = "prior_disabled_ablation"
MODE_PRIOR_BLOCKERS_ONLY = "prior_blockers_only"
MODE_PRIOR_EVIDENCE_ONLY = "prior_evidence_requirements_only"
MODE_PRIOR_RESIDUALS_ONLY = "prior_residual_expectations_only"


def _trace_complete_for_rule(case: dict[str, object], required_fields: tuple[str, ...]) -> bool:
    trace = case.get("trace_definition")
    if not isinstance(trace, dict):
        return False
    for field in required_fields:
        value = trace.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def _qualified_golden_rules(rules: list[object]) -> list[object]:
    qualified = []
    for rule in rules:
        q = qualify_golden_rule(rule)
        if q.maturity_level in {
            GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE,
            GoldenRuleMaturityLevel.GOLDEN_RULE,
        } and q.can_measure_new_concepts:
            qualified.append(rule)
    return qualified


def _rule_maturity_levels(rules: list[object]) -> dict[str, str]:
    return {rule.rule_id: qualify_golden_rule(rule).maturity_level.value for rule in rules}


def _active_rules_for_mode(*, mode: str, all_rules: list[object], golden_rules: list[object]) -> list[object]:
    if mode == MODE_WITH_QUALIFIED_GOLDEN_RULES:
        return golden_rules
    if mode == MODE_PRIOR_BLOCKERS_ONLY:
        return all_rules
    if mode == MODE_PRIOR_EVIDENCE_ONLY:
        return all_rules
    if mode == MODE_PRIOR_RESIDUALS_ONLY:
        return all_rules
    if mode == MODE_WITH_ALL_PRIORS:
        return all_rules
    return []


def _mode_checks(mode: str) -> tuple[bool, bool, bool]:
    check_blockers = mode in {MODE_WITH_ALL_PRIORS, MODE_WITH_QUALIFIED_GOLDEN_RULES, MODE_PRIOR_BLOCKERS_ONLY}
    check_evidence = mode in {MODE_WITH_ALL_PRIORS, MODE_WITH_QUALIFIED_GOLDEN_RULES, MODE_PRIOR_EVIDENCE_ONLY}
    check_residuals = mode in {MODE_WITH_ALL_PRIORS, MODE_WITH_QUALIFIED_GOLDEN_RULES, MODE_PRIOR_RESIDUALS_ONLY}
    return check_blockers, check_evidence, check_residuals


def _evaluate_signals(
    *,
    case: dict[str, object],
    rules: list[object],
    check_blockers: bool,
    check_evidence: bool,
    check_residuals: bool,
) -> dict[str, object]:
    case_tokens: set[str] = set()
    for key in ("constraints", "expected_residuals", "forbidden_decisions"):
        value = case.get(key)
        if isinstance(value, list):
            case_tokens.update(str(item) for item in value)
    case_evidence = set(case.get("required_evidence", []) if isinstance(case.get("required_evidence"), list) else [])

    missing_required_evidence: set[str] = set()
    activated_blockers: set[str] = set()
    missing_expected_residuals: set[str] = set()
    trace_enforced = True

    for rule in rules:
        required = set(rule.required_evidence.required_items)
        missing_required_evidence.update(required - case_evidence)
        trace_enforced = trace_enforced and _trace_complete_for_rule(
            case, rule.reverse_trace_requirements.required_fields
        )

        if check_blockers:
            for blocker in rule.certificate_blockers:
                if any(token in case_tokens for token in blocker.match_any):
                    activated_blockers.add(blocker.blocker_id)

        if check_residuals:
            for residual in rule.expected_residuals:
                if residual.residual_id not in case_tokens:
                    missing_expected_residuals.add(residual.residual_id)

    return {
        "missing_required_evidence": sorted(missing_required_evidence) if check_evidence else [],
        "activated_blockers": sorted(activated_blockers),
        "missing_expected_residuals": sorted(missing_expected_residuals),
        "trace_enforced": trace_enforced,
    }


def _decision_after_priors(
    *,
    before: str,
    missing_rule: bool,
    activated_blockers: list[str],
    missing_evidence: list[str],
    missing_residuals: list[str],
    block_certificate_on_missing_prior_coverage: bool,
) -> tuple[str, list[str]]:
    after = before
    residuals: list[str] = []
    should_block = False

    if missing_rule and block_certificate_on_missing_prior_coverage:
        residuals.append("prior_coverage_gap")
        should_block = True
    if activated_blockers:
        residuals.extend(f"prior_blocking:{item}" for item in activated_blockers)
        should_block = True
    if missing_evidence:
        residuals.extend(f"prior_missing_evidence:{item}" for item in missing_evidence)
        should_block = True
    if missing_residuals:
        residuals.extend(f"prior_expected_residual_missing:{item}" for item in missing_residuals)
        should_block = True

    if after in _CERT_ASCENT_LEVELS and should_block:
        after = "HYPOTHESIS"

    return after, sorted(dict.fromkeys(residuals))


def compute_prior_coverage_matrix(
    *,
    cases: list[dict[str, object]],
    registry: PriorRegistry,
    mode: str = MODE_WITH_ALL_PRIORS,
    block_certificate_on_missing_prior_coverage: bool = True,
) -> list[dict[str, object]]:
    check_blockers, check_evidence, check_residuals = _mode_checks(mode)

    rows: list[dict[str, object]] = []
    base = GovernedProtocolBaseline(prior_registry=None)

    for case in cases:
        before = base.predict(case)
        all_rules = registry.find_case_rules(case)
        golden_rules = _qualified_golden_rules(all_rules)
        active_rules = _active_rules_for_mode(mode=mode, all_rules=all_rules, golden_rules=golden_rules)

        signals = _evaluate_signals(
            case=case,
            rules=active_rules,
            check_blockers=check_blockers,
            check_evidence=check_evidence,
            check_residuals=check_residuals,
        )

        after, residuals_added = _decision_after_priors(
            before=before.predicted_decision,
            missing_rule=not all_rules,
            activated_blockers=signals["activated_blockers"],
            missing_evidence=signals["missing_required_evidence"],
            missing_residuals=signals["missing_expected_residuals"],
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        )
        if not golden_rules:
            residuals_added = sorted(dict.fromkeys([*residuals_added, "golden_rule_coverage_gap"]))
            if after in _CERT_ASCENT_LEVELS:
                after = "HYPOTHESIS"

        golden_signals = _evaluate_signals(
            case=case,
            rules=golden_rules,
            check_blockers=True,
            check_evidence=True,
            check_residuals=True,
        )
        golden_after, _ = _decision_after_priors(
            before=before.predicted_decision,
            missing_rule=not golden_rules,
            activated_blockers=golden_signals["activated_blockers"],
            missing_evidence=golden_signals["missing_required_evidence"],
            missing_residuals=golden_signals["missing_expected_residuals"],
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        )

        decision_delta = "UNCHANGED" if after == before.predicted_decision else f"{before.predicted_decision}->{after}"
        rows.append(
            {
                "case_id": str(case["id"]),
                "domain": str(case["domain"]),
                "mode": mode,
                "matched_prior_rule_ids": sorted(rule.rule_id for rule in all_rules),
                "matched_golden_rule_ids": sorted(rule.rule_id for rule in golden_rules),
                "missing_prior_rule": not all_rules,
                "missing_golden_rule": not golden_rules,
                "prior_maturity_level": _rule_maturity_levels(all_rules),
                "certificate_blockers_activated": signals["activated_blockers"],
                "missing_evidence_detected": bool(signals["missing_required_evidence"]),
                "required_evidence_missing": signals["missing_required_evidence"],
                "expected_residuals_missing": signals["missing_expected_residuals"],
                "residuals_added_by_priors": residuals_added,
                "decision_before_priors": before.predicted_decision,
                "decision_after_priors": after,
                "decision_after_golden_rules_only": golden_after,
                "decision_delta": decision_delta,
            }
        )
    return rows


def _apply_prior_matrix_to_results(
    *,
    cases: list[dict[str, object]],
    matrix_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    base = GovernedProtocolBaseline(prior_registry=None)
    rows_by_id = {str(row["case_id"]): row for row in matrix_rows}
    out: list[dict[str, object]] = []

    for case in cases:
        base_result = asdict(base.predict(case))
        row = rows_by_id[str(case["id"])]
        decision_after = str(row["decision_after_priors"])
        tags = list(base_result["error_tags"])
        tags.extend(str(tag) for tag in row["residuals_added_by_priors"])

        if row["missing_prior_rule"]:
            tags.append("prior_missing:prior_coverage_gap")
        for blocker in row["certificate_blockers_activated"]:
            tags.append(f"prior_blocking:{blocker}")

        final_tags = tuple(dict.fromkeys(tags))
        result = {
            **base_result,
            "predicted_decision": decision_after,
            "final_judgment": (
                "CERTIFICATE"
                if decision_after == "CERTIFICATE"
                else ("ZERO" if decision_after == "ZERO" else "HYPOTHESIS")
            ),
            "has_blocking_residual": bool(base_result["has_blocking_residual"] or row["residuals_added_by_priors"]),
            "prior_rule_ids": tuple(row["matched_prior_rule_ids"]),
            "prior_residual_tags": tuple(row["residuals_added_by_priors"]),
            "error_tags": final_tags,
        }
        if (
            LEVEL_SCORE.get(decision_after, 0) < LEVEL_SCORE.get(case.get("expected_decision_level", "HYPOTHESIS"), 1)
            and decision_after in {"ZERO", "HYPOTHESIS"}
        ):
            if "overblocking" not in result["error_tags"]:
                result["error_tags"] = tuple(list(result["error_tags"]) + ["overblocking"])
        out.append(result)

    return out


def _prior_metrics(matrix_rows: list[dict[str, object]]) -> dict[str, float]:
    total = max(1, len(matrix_rows))
    matched_prior = sum(1 for row in matrix_rows if not row["missing_prior_rule"])
    matched_golden = sum(1 for row in matrix_rows if not row["missing_golden_rule"])
    activated_golden = sum(1 for row in matrix_rows if row["matched_golden_rule_ids"])
    blocker_hits = sum(1 for row in matrix_rows if row["certificate_blockers_activated"])
    missing_evidence = sum(1 for row in matrix_rows if row["missing_evidence_detected"])
    uncovered = sum(1 for row in matrix_rows if row["missing_golden_rule"])
    concept_blocked = sum(
        1
        for row in matrix_rows
        if row["decision_before_priors"] in _CERT_ASCENT_LEVELS and row["decision_after_priors"] in {"ZERO", "HYPOTHESIS"}
    )

    return {
        "prior_rule_coverage_rate": round(matched_prior / total, 4),
        "golden_rule_coverage_rate": round(matched_golden / total, 4),
        "golden_rule_activation_rate": round(activated_golden / total, 4),
        "certificate_blocker_activation_rate": round(blocker_hits / total, 4),
        "missing_evidence_rate": round(missing_evidence / total, 4),
        "concept_admissibility_block_rate": round(concept_blocked / total, 4),
        "uncovered_case_rate": round(uncovered / total, 4),
        "prior_coverage_gap_count": float(sum(1 for row in matrix_rows if row["missing_prior_rule"])),
    }


def _build_mode_report(
    *,
    mode: str,
    cases: list[dict[str, object]],
    registry: PriorRegistry | None,
    block_certificate_on_missing_prior_coverage: bool,
) -> dict[str, object]:
    if registry is None:
        base = GovernedProtocolBaseline(prior_registry=None)
        result_objects = [base.predict(case) for case in cases]
        results = [asdict(item) for item in result_objects]
        metrics = _compute_metrics(cases, result_objects)
        metrics.update(
            {
                "prior_rule_coverage_rate": 0.0,
                "golden_rule_coverage_rate": 0.0,
                "golden_rule_activation_rate": 0.0,
                "certificate_blocker_activation_rate": 0.0,
                "missing_evidence_rate": 0.0,
                "concept_admissibility_block_rate": 0.0,
                "uncovered_case_rate": 0.0,
                "prior_coverage_gap_count": 0.0,
            }
        )
        return {"mode": mode, "metrics": metrics, "cases": results, "prior_coverage_matrix": []}

    matrix = compute_prior_coverage_matrix(
        cases=cases,
        registry=registry,
        mode=mode,
        block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
    )
    adjusted = _apply_prior_matrix_to_results(cases=cases, matrix_rows=matrix)
    result_objects = [GovernedProtocolBaseline(prior_registry=None).predict(case) for case in cases]
    for idx, row in enumerate(adjusted):
        result_objects[idx] = result_objects[idx].__class__(**row)  # type: ignore[arg-type]
    metrics = _compute_metrics(cases, result_objects)
    metrics.update(_prior_metrics(matrix))

    return {
        "mode": mode,
        "metrics": metrics,
        "cases": adjusted,
        "prior_coverage_matrix": matrix,
    }


def run_prior_aware_baseline_ablation(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
    *,
    prior_registry: PriorRegistry | None = None,
    block_certificate_on_missing_prior_coverage: bool = True,
) -> dict[str, object]:
    cases = iter_all_cases(dataset_dir=dataset_dir)
    registry = prior_registry if prior_registry is not None else load_golden_prior_registry()

    modes = {
        MODE_WITHOUT_PRIORS: _build_mode_report(
            mode=MODE_WITHOUT_PRIORS,
            cases=cases,
            registry=None,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_WITH_ALL_PRIORS: _build_mode_report(
            mode=MODE_WITH_ALL_PRIORS,
            cases=cases,
            registry=registry,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_WITH_QUALIFIED_GOLDEN_RULES: _build_mode_report(
            mode=MODE_WITH_QUALIFIED_GOLDEN_RULES,
            cases=cases,
            registry=registry,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_PRIOR_DISABLED: _build_mode_report(
            mode=MODE_PRIOR_DISABLED,
            cases=cases,
            registry=None,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_PRIOR_BLOCKERS_ONLY: _build_mode_report(
            mode=MODE_PRIOR_BLOCKERS_ONLY,
            cases=cases,
            registry=registry,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_PRIOR_EVIDENCE_ONLY: _build_mode_report(
            mode=MODE_PRIOR_EVIDENCE_ONLY,
            cases=cases,
            registry=registry,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
        MODE_PRIOR_RESIDUALS_ONLY: _build_mode_report(
            mode=MODE_PRIOR_RESIDUALS_ONLY,
            cases=cases,
            registry=registry,
            block_certificate_on_missing_prior_coverage=block_certificate_on_missing_prior_coverage,
        ),
    }

    # Backward-compat alias
    modes[MODE_WITH_GOLDEN_PRIORS] = modes[MODE_WITH_ALL_PRIORS]

    without = modes[MODE_WITHOUT_PRIORS]["metrics"]
    with_all = modes[MODE_WITH_ALL_PRIORS]["metrics"]
    deltas = {
        "false_certificate_delta": round(with_all["false_certificate_rate"] - without["false_certificate_rate"], 4),
        "overblocking_delta": round(with_all["overblocking_rate"] - without["overblocking_rate"], 4),
        "residual_preservation_delta": round(
            with_all["residual_preservation_rate"] - without["residual_preservation_rate"], 4
        ),
        "prior_false_certificate_delta": round(
            with_all["false_certificate_rate"] - without["false_certificate_rate"], 4
        ),
        "prior_overblocking_delta": round(with_all["overblocking_rate"] - without["overblocking_rate"], 4),
        "prior_gettier_detection_delta": round(
            with_all["gettier_detection_rate"] - without["gettier_detection_rate"], 4
        ),
        "prior_trace_enforcement_delta": round(
            with_all["reverse_trace_coverage"] - without["reverse_trace_coverage"], 4
        ),
    }

    gaps = [
        row["case_id"]
        for row in modes[MODE_WITH_ALL_PRIORS]["prior_coverage_matrix"]
        if row["missing_prior_rule"]
    ]
    return {
        "protocol_id": "PRIOR-AWARE-BASELINE-ABLATION-108",
        "dataset_id": "fractal_governance_benchmark_105",
        "dataset_path": str(dataset_dir),
        "deterministic": True,
        "trained_model_used": False,
        "external_models_used": [],
        "artificial_consciousness_claim": False,
        "global_certificate_claim": False,
        "final_epistemic_judgments": _FINAL_JUDGMENTS,
        "theorem_status": "STRONG_HYPOTHESIS",
        "modes": modes,
        "deltas": deltas,
        "prior_coverage_gap_residual": {
            "residual_id": "prior_coverage_gap",
            "count": len(gaps),
            "case_ids": gaps,
            "default_policy_blocks_certificate": block_certificate_on_missing_prior_coverage,
        },
    }
