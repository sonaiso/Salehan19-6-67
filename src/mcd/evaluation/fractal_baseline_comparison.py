"""Deterministic governed-vs-naive baseline comparison for benchmark dataset #105."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from mcd.evaluation.fractal_benchmark_dataset import (
    DEFAULT_BENCHMARK_DIR,
    iter_all_cases,
)
from mcd.knowledge.golden_prior_registry import PriorRegistry, evaluate_case_against_priors

DECISION_LEVELS: tuple[str, ...] = (
    "ZERO",
    "HYPOTHESIS",
    "STRONG",
    "CERTIFICATE_CANDIDATE",
    "CERTIFICATE",
)

LEVEL_SCORE: dict[str, int] = {level: index for index, level in enumerate(DECISION_LEVELS)}
HIGHER_THAN_HYPOTHESIS = {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}


def _trace_complete(case: dict[str, object]) -> bool:
    trace = case.get("trace_definition")
    if not isinstance(trace, dict):
        return False
    required = ("input", "candidate", "evidence", "decision_path")
    return all(isinstance(trace.get(key), str) and trace.get(key).strip() for key in required)


def _certificate_obligations_complete(case: dict[str, object]) -> bool:
    obligations = case.get("certificate_obligations")
    if not isinstance(obligations, dict):
        return False
    required = (
        "proof_object",
        "governance_gate_passed",
        "reverse_trace_complete",
        "evidence_complete",
        "no_blocking_residual",
    )
    return all(bool(obligations.get(key)) for key in required)


def _baseline_confidence(case: dict[str, object]) -> float:
    level = str(case.get("allowed_decision_level", "HYPOTHESIS"))
    base = {
        "ZERO": 0.1,
        "HYPOTHESIS": 0.78,
        "STRONG": 0.9,
        "CERTIFICATE_CANDIDATE": 0.97,
        "CERTIFICATE": 0.99,
    }.get(level, 0.5)
    if case.get("required_evidence") and isinstance(case["required_evidence"], list):
        base += min(0.02, 0.005 * len(case["required_evidence"]))
    if case.get("expected_residuals") and isinstance(case["expected_residuals"], list):
        base -= min(0.05, 0.01 * len(case["expected_residuals"]))
    return max(0.0, min(1.0, round(base, 4)))


def _level_from_confidence(
    confidence: float,
    *,
    certificate_threshold: float = 0.97,
    strong_threshold: float = 0.84,
    hypothesis_threshold: float = 0.2,
) -> str:
    if confidence >= certificate_threshold:
        return "CERTIFICATE"
    if confidence >= strong_threshold:
        return "STRONG"
    if confidence >= hypothesis_threshold:
        return "HYPOTHESIS"
    return "ZERO"


@dataclass(frozen=True)
class BaselineCaseResult:
    case_id: str
    domain: str
    baseline: str
    predicted_decision: str
    confidence: float
    evidence_complete: bool
    governance_gate_passed: bool
    reverse_trace_complete: bool
    has_blocking_residual: bool
    preserved_residuals: bool
    local_zero_in_path: bool
    local_zero_preserved: bool
    final_judgment: str
    prior_rule_ids: tuple[str, ...]
    prior_residual_tags: tuple[str, ...]
    error_tags: tuple[str, ...]


class BaseBaseline:
    name = "base"

    def predict(self, case: dict[str, object]) -> BaselineCaseResult:
        raise NotImplementedError

    @staticmethod
    def _final_judgment(decision: str) -> str:
        if decision == "CERTIFICATE":
            return "CERTIFICATE"
        if decision == "ZERO":
            return "ZERO"
        return "HYPOTHESIS"

    def _build_result(
        self,
        *,
        case: dict[str, object],
        predicted_decision: str,
        confidence: float,
        evidence_complete: bool,
        governance_gate_passed: bool,
        reverse_trace_complete: bool,
        has_blocking_residual: bool,
        preserved_residuals: bool,
        prior_rule_ids: tuple[str, ...] = (),
        prior_residual_tags: tuple[str, ...] = (),
    ) -> BaselineCaseResult:
        local_zero_in_path = bool(case.get("local_zero_in_path"))
        local_zero_preserved = not (local_zero_in_path and predicted_decision == "ZERO")
        tags = _error_tags(
            case=case,
            predicted_decision=predicted_decision,
            evidence_complete=evidence_complete,
            governance_gate_passed=governance_gate_passed,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=has_blocking_residual,
            preserved_residuals=preserved_residuals,
            local_zero_preserved=local_zero_preserved,
            prior_error_tags=prior_residual_tags,
        )
        return BaselineCaseResult(
            case_id=str(case["id"]),
            domain=str(case["domain"]),
            baseline=self.name,
            predicted_decision=predicted_decision,
            confidence=confidence,
            evidence_complete=evidence_complete,
            governance_gate_passed=governance_gate_passed,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=has_blocking_residual,
            preserved_residuals=preserved_residuals,
            local_zero_in_path=local_zero_in_path,
            local_zero_preserved=local_zero_preserved,
            final_judgment=self._final_judgment(predicted_decision),
            prior_rule_ids=prior_rule_ids,
            prior_residual_tags=prior_residual_tags,
            error_tags=tuple(tags),
        )


class AnswerConfidenceBaseline(BaseBaseline):
    name = "AnswerConfidenceBaseline"

    def predict(self, case: dict[str, object]) -> BaselineCaseResult:
        confidence = _baseline_confidence(case)
        decision = _level_from_confidence(confidence)
        evidence_complete = bool(case.get("required_evidence"))
        reverse_trace_complete = _trace_complete(case)
        return self._build_result(
            case=case,
            predicted_decision=decision,
            confidence=confidence,
            evidence_complete=evidence_complete,
            governance_gate_passed=False,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=False,
            preserved_residuals=False,
        )


class NaiveCertificateBaseline(BaseBaseline):
    name = "NaiveCertificateBaseline"

    def predict(self, case: dict[str, object]) -> BaselineCaseResult:
        confidence = _baseline_confidence(case)
        decision = "CERTIFICATE" if confidence >= 0.85 else _level_from_confidence(confidence)
        evidence_complete = bool(case.get("required_evidence"))
        reverse_trace_complete = _trace_complete(case)
        return self._build_result(
            case=case,
            predicted_decision=decision,
            confidence=confidence,
            evidence_complete=evidence_complete,
            governance_gate_passed=False,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=False,
            preserved_residuals=False,
        )


class ConservativeHypothesisBaseline(BaseBaseline):
    name = "ConservativeHypothesisBaseline"

    def predict(self, case: dict[str, object]) -> BaselineCaseResult:
        confidence = _baseline_confidence(case)
        decision = "ZERO" if confidence < 0.25 else "HYPOTHESIS"
        evidence_complete = bool(case.get("required_evidence"))
        reverse_trace_complete = _trace_complete(case)
        return self._build_result(
            case=case,
            predicted_decision=decision,
            confidence=confidence,
            evidence_complete=evidence_complete,
            governance_gate_passed=False,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=bool(case.get("expected_residuals")),
            preserved_residuals=True,
        )


class GovernedProtocolBaseline(BaseBaseline):
    name = "GovernedProtocolBaseline"

    def __init__(self, prior_registry: PriorRegistry | None = None) -> None:
        self._prior_registry = prior_registry

    def predict(self, case: dict[str, object]) -> BaselineCaseResult:
        confidence = _baseline_confidence(case)
        evidence_complete = bool(case.get("required_evidence"))
        reverse_trace_complete = _trace_complete(case) and bool(case.get("reverse_trace_required"))
        has_blocking_residual = bool(case.get("expected_residuals"))
        governance_gate_passed = bool(_certificate_obligations_complete(case))
        prior_rule_ids: tuple[str, ...] = ()
        prior_residual_tags: tuple[str, ...] = ()

        if self._prior_registry is not None:
            rules = self._prior_registry.find_case_rules(case)
            prior_missing, prior_blocking, used_rule_ids, prior_tags = evaluate_case_against_priors(case, rules)
            prior_rule_ids = tuple(sorted(used_rule_ids))
            prior_residual_tags = tuple(prior_tags)
            if prior_blocking:
                has_blocking_residual = True

        if confidence < 0.2:
            decision = "ZERO"
        elif confidence < 0.8:
            decision = "HYPOTHESIS"
        elif confidence < 0.95:
            decision = "STRONG"
        else:
            decision = "CERTIFICATE_CANDIDATE"

        if decision in {"STRONG", "CERTIFICATE_CANDIDATE"} and not reverse_trace_complete:
            decision = "HYPOTHESIS"

        if decision == "CERTIFICATE_CANDIDATE":
            can_certificate = (
                evidence_complete
                and governance_gate_passed
                and reverse_trace_complete
                and not has_blocking_residual
                and "CERTIFICATE" not in set(case.get("forbidden_decisions", []))
            )
            decision = "CERTIFICATE" if can_certificate else "CERTIFICATE_CANDIDATE"

        if self._prior_registry is not None and decision in {"CERTIFICATE_CANDIDATE", "CERTIFICATE"}:
            if any(tag.startswith("prior_missing:") or tag.startswith("prior_blocking:") for tag in prior_residual_tags):
                decision = "HYPOTHESIS"
                has_blocking_residual = True

        if decision == "CERTIFICATE" and (
            not evidence_complete
            or not governance_gate_passed
            or not reverse_trace_complete
            or has_blocking_residual
        ):
            decision = "HYPOTHESIS"

        if bool(case.get("local_zero_in_path")) and decision == "ZERO":
            decision = "HYPOTHESIS"

        return self._build_result(
            case=case,
            predicted_decision=decision,
            confidence=confidence,
            evidence_complete=evidence_complete,
            governance_gate_passed=governance_gate_passed,
            reverse_trace_complete=reverse_trace_complete,
            has_blocking_residual=has_blocking_residual,
            preserved_residuals=True,
            prior_rule_ids=prior_rule_ids,
            prior_residual_tags=prior_residual_tags,
        )


def _is_gettier_case(case: dict[str, object]) -> bool:
    case_id = str(case.get("id", "")).lower()
    notes = str(case.get("notes", "")).lower()
    return "gettier" in case_id or "gettier-style" in notes


def _is_false_certificate(
    *,
    case: dict[str, object],
    predicted_decision: str,
    evidence_complete: bool,
    governance_gate_passed: bool,
    reverse_trace_complete: bool,
    has_blocking_residual: bool,
) -> bool:
    if predicted_decision != "CERTIFICATE":
        return False
    forbidden = set(case.get("forbidden_decisions", []))
    return (
        "CERTIFICATE" in forbidden
        or not evidence_complete
        or not governance_gate_passed
        or not reverse_trace_complete
        or has_blocking_residual
    )


def _error_tags(
    *,
    case: dict[str, object],
    predicted_decision: str,
    evidence_complete: bool,
    governance_gate_passed: bool,
    reverse_trace_complete: bool,
    has_blocking_residual: bool,
    preserved_residuals: bool,
    local_zero_preserved: bool,
    prior_error_tags: tuple[str, ...] = (),
) -> list[str]:
    tags: list[str] = []
    expected_level = str(case.get("expected_decision_level", "HYPOTHESIS"))
    forbidden = set(case.get("forbidden_decisions", []))
    predicted_score = LEVEL_SCORE.get(predicted_decision, LEVEL_SCORE["HYPOTHESIS"])
    expected_score = LEVEL_SCORE.get(expected_level, LEVEL_SCORE["HYPOTHESIS"])

    false_certificate = _is_false_certificate(
        case=case,
        predicted_decision=predicted_decision,
        evidence_complete=evidence_complete,
        governance_gate_passed=governance_gate_passed,
        reverse_trace_complete=reverse_trace_complete,
        has_blocking_residual=has_blocking_residual,
    )
    if false_certificate:
        tags.append("false_certificate")

    if predicted_score > expected_score and predicted_decision in HIGHER_THAN_HYPOTHESIS:
        tags.append("false_strong")
    if expected_level in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"} and predicted_decision in {
        "ZERO",
        "HYPOTHESIS",
    }:
        tags.append("overblocking")
    if case.get("expected_residuals") and not preserved_residuals:
        tags.append("lost_residual")
    if predicted_decision in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"} and not reverse_trace_complete:
        tags.append("missing_trace")
    if bool(case.get("local_zero_in_path")) and not local_zero_preserved:
        tags.append("zero_globalized")
    if _is_gettier_case(case) and predicted_decision == "CERTIFICATE":
        tags.append("gettier_failure")
    if predicted_decision in forbidden or false_certificate:
        tags.append("forbidden_transition")
    tags.extend(prior_error_tags)
    return tags


def _decision_target(expected_level: str) -> float:
    return {
        "ZERO": 0.0,
        "HYPOTHESIS": 0.55,
        "STRONG": 0.82,
        "CERTIFICATE_CANDIDATE": 0.93,
        "CERTIFICATE": 0.98,
    }.get(expected_level, 0.55)


def _compute_metrics(cases: list[dict[str, object]], results: list[BaselineCaseResult]) -> dict[str, float]:
    total = max(1, len(results))
    false_certificates = 0
    certificate_count = 0
    overblocking = 0
    residual_preserved = 0
    trace_cover_total = 0
    trace_cover_ok = 0
    forbidden_violations = 0
    zero_local_total = 0
    zero_local_ok = 0
    calibration_errors: list[float] = []
    gettier_total = 0
    gettier_detected = 0

    for case, result in zip(cases, results):
        if result.predicted_decision == "CERTIFICATE":
            certificate_count += 1
            if "false_certificate" in result.error_tags:
                false_certificates += 1
        if "overblocking" in result.error_tags:
            overblocking += 1
        if not case.get("expected_residuals") or result.preserved_residuals:
            residual_preserved += 1
        if result.predicted_decision in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}:
            trace_cover_total += 1
            if result.reverse_trace_complete:
                trace_cover_ok += 1
        if "forbidden_transition" in result.error_tags:
            forbidden_violations += 1
        if result.local_zero_in_path:
            zero_local_total += 1
            if result.local_zero_preserved:
                zero_local_ok += 1
        if _is_gettier_case(case):
            gettier_total += 1
            if result.predicted_decision != "CERTIFICATE":
                gettier_detected += 1
        calibration_errors.append(
            abs(result.confidence - _decision_target(str(case.get("expected_decision_level", "HYPOTHESIS"))))
        )

    false_certificate_rate = false_certificates / certificate_count if certificate_count else 0.0
    overblocking_candidates = sum(
        1
        for case in cases
        if str(case.get("expected_decision_level")) in {"STRONG", "CERTIFICATE_CANDIDATE", "CERTIFICATE"}
    )
    overblocking_rate = overblocking / overblocking_candidates if overblocking_candidates else 0.0
    residual_preservation_rate = residual_preserved / total
    reverse_trace_coverage = trace_cover_ok / trace_cover_total if trace_cover_total else 1.0
    forbidden_transition_violation_rate = forbidden_violations / total
    zero_in_path_locality_accuracy = zero_local_ok / zero_local_total if zero_local_total else 1.0
    decision_calibration_error = sum(calibration_errors) / len(calibration_errors) if calibration_errors else 0.0
    gettier_detection_rate = gettier_detected / gettier_total if gettier_total else 1.0

    return {
        "false_certificate_rate": round(false_certificate_rate, 4),
        "overblocking_rate": round(overblocking_rate, 4),
        "residual_preservation_rate": round(residual_preservation_rate, 4),
        "reverse_trace_coverage": round(reverse_trace_coverage, 4),
        "forbidden_transition_violation_rate": round(forbidden_transition_violation_rate, 4),
        "zero_in_path_locality_accuracy": round(zero_in_path_locality_accuracy, 4),
        "decision_calibration_error": round(decision_calibration_error, 4),
        "gettier_detection_rate": round(gettier_detection_rate, 4),
    }


def run_fractal_baseline_comparison(
    dataset_dir: Path = DEFAULT_BENCHMARK_DIR,
    prior_registry: PriorRegistry | None = None,
) -> dict[str, object]:
    cases = iter_all_cases(dataset_dir=dataset_dir)
    baselines: tuple[BaseBaseline, ...] = (
        AnswerConfidenceBaseline(),
        NaiveCertificateBaseline(),
        ConservativeHypothesisBaseline(),
        GovernedProtocolBaseline(prior_registry=prior_registry),
    )

    by_baseline: dict[str, dict[str, object]] = {}
    for baseline in baselines:
        results = [baseline.predict(case) for case in cases]
        by_baseline[baseline.name] = {
            "metrics": _compute_metrics(cases, results),
            "cases": [asdict(result) for result in results],
        }

    return {
        "protocol_id": "FRACTAL-BASELINE-COMPARISON-106",
        "dataset_id": "fractal_governance_benchmark_105",
        "dataset_path": str(dataset_dir),
        "deterministic": True,
        "trained_model_used": False,
        "external_models_used": [],
        "final_epistemic_judgments": ["ZERO", "HYPOTHESIS", "CERTIFICATE"],
        "theorem_status": "STRONG_HYPOTHESIS",
        "non_goals_enforced": {
            "external_model_data_collection": False,
            "training": False,
            "global_certificate_claim": False,
            "fgn_trained_claim": False,
        },
        "baselines": by_baseline,
    }
