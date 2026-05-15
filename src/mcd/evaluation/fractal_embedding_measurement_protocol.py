"""Fractal embedding measurement protocol contracts for PR #104.

This module defines schema/contracts/metrics/loss and benchmark-ablation stubs.
It does not implement a trained fractal embedding model.
"""
from __future__ import annotations

from dataclasses import dataclass, field

FINAL_STATUSES: tuple[str, ...] = ("ZERO", "HYPOTHESIS", "CERTIFICATE")
LOCAL_ZERO_IN_PATH = "ZERO_IN_PATH"

REQUIRED_LOSS_CONTRACTS: tuple[str, ...] = (
    "AnswerLoss",
    "EvidenceAlignmentLoss",
    "ResidualDetectionLoss",
    "TraceCompletenessLoss",
    "DecisionCalibrationLoss",
    "ForbiddenTransitionLoss",
    "CertificateGateLoss",
)

REQUIRED_METRICS: tuple[str, ...] = (
    "answer_accuracy",
    "evidence_precision",
    "residual_recall",
    "trace_completeness",
    "decision_calibration_error",
    "false_certificate_rate",
    "forbidden_transition_violation_rate",
    "zero_in_path_locality_accuracy",
)

REQUIRED_ABLATION_COMPONENTS: tuple[str, ...] = (
    "Evidence",
    "Residual",
    "ReverseTrace",
    "CertificateGate",
)


@dataclass(frozen=True)
class FractalEmbeddingSpec:
    semantic_vector: tuple[float, ...]
    layer_vector: tuple[float, ...]
    path_vector: tuple[float, ...]
    candidate_vector: tuple[float, ...]
    constraint_vector: tuple[float, ...]
    evidence_vector: tuple[float, ...]
    residual_vector: tuple[float, ...]
    ranking_vector: tuple[float, ...]
    decision_vector: tuple[float, ...]
    reverse_trace_vector: tuple[float, ...]


@dataclass(frozen=True)
class GovernedMeaningPath:
    path_id: str
    claim: str
    constraints: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    reverse_trace_ref: str = ""
    typed_edges: tuple["EvidenceBearingEdge", ...] = ()


@dataclass(frozen=True)
class EvidenceBearingEdge:
    source: str
    target: str
    evidence_type: str
    evidence_ref: str
    supports_claim: bool


@dataclass(frozen=True)
class ResidualAwareVector:
    values: tuple[float, ...]
    residual_tags: tuple[str, ...] = ()
    blocking_residual_present: bool = False


@dataclass(frozen=True)
class TraceAwareVector:
    values: tuple[float, ...]
    reverse_trace_ref: str = ""
    trace_complete: bool = False


@dataclass(frozen=True)
class DecisionCalibrationTarget:
    answer_probability: float
    justified_decision_probability: float
    decision: str


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    domain: str
    input_text: str
    candidates: tuple[str, ...]
    constraints: tuple[str, ...]
    required_evidence: tuple[str, ...]
    expected_residuals: tuple[str, ...]
    forbidden_decisions: tuple[str, ...]
    allowed_decision_level: str
    reverse_trace_requirement: str


@dataclass(frozen=True)
class AblationSpec:
    ablation_id: str
    removed_component: str
    expected_risk: str


@dataclass(frozen=True)
class LossContract:
    name: str
    objective: str
    blocks_false_certificate: bool = False


@dataclass(frozen=True)
class DecisionGate:
    evidence_present: bool
    reverse_trace_complete: bool
    governance_gate_passed: bool
    proof_object_ref: str
    blocking_residual_present: bool = False


def can_issue_certificate(gate: DecisionGate) -> bool:
    return (
        gate.evidence_present
        and gate.reverse_trace_complete
        and gate.governance_gate_passed
        and bool(gate.proof_object_ref)
        and not gate.blocking_residual_present
    )


def answer_probability(score: float) -> float:
    return max(0.0, min(1.0, float(score)))


def justified_decision_probability(answer_prob: float, gate: DecisionGate) -> float:
    if not can_issue_certificate(gate):
        return 0.0
    return answer_probability(answer_prob)


def decide_status(answer_prob: float, gate: DecisionGate) -> str:
    prob = answer_probability(answer_prob)
    if can_issue_certificate(gate) and prob >= 0.95:
        return "CERTIFICATE"
    if prob >= 0.2:
        return "HYPOTHESIS"
    return "ZERO"


def aggregate_global_status(path_statuses: list[str]) -> str:
    normalized = [s.strip().upper() for s in path_statuses if s and s.strip()]
    non_local = [s for s in normalized if s != LOCAL_ZERO_IN_PATH]
    if not non_local:
        return "ZERO"
    if "CERTIFICATE" in non_local:
        return "CERTIFICATE"
    if "HYPOTHESIS" in non_local:
        return "HYPOTHESIS"
    return "ZERO"


def build_loss_contracts() -> tuple[LossContract, ...]:
    return (
        LossContract("AnswerLoss", "Optimize answer correctness."),
        LossContract("EvidenceAlignmentLoss", "Align claims with required evidence."),
        LossContract("ResidualDetectionLoss", "Detect and preserve residuals."),
        LossContract("TraceCompletenessLoss", "Penalize incomplete reverse traces."),
        LossContract("DecisionCalibrationLoss", "Calibrate confidence vs governed outcome."),
        LossContract("ForbiddenTransitionLoss", "Penalize forbidden transition usage."),
        LossContract(
            "CertificateGateLoss",
            "Penalize certificate output when gate obligations are incomplete.",
            blocks_false_certificate=True,
        ),
    )


def build_benchmark_contracts() -> tuple[BenchmarkCase, ...]:
    return (
        BenchmarkCase(
            case_id="FEM-AR-001",
            domain="arabic_language",
            input_text="رأيت دخانًا",
            candidates=("توجد نار محتملة", "توجد نار قطعًا"),
            constraints=("no_certificate_without_direct_evidence",),
            required_evidence=("direct_fire_observation",),
            expected_residuals=("smoke_not_direct_fire", "steam_or_dust_alternative"),
            forbidden_decisions=("CERTIFICATE",),
            allowed_decision_level="HYPOTHESIS",
            reverse_trace_requirement="must_link_observation_to_decision",
        ),
        BenchmarkCase(
            case_id="FEM-MATH-001",
            domain="mathematics",
            input_text="Claim: for all n, n^2 - n + 41 is prime",
            candidates=("true_for_small_n", "always_true"),
            constraints=("no_universal_certificate_without_proof",),
            required_evidence=("formal_counterexample_check_or_proof",),
            expected_residuals=("finite_check_not_universal_proof",),
            forbidden_decisions=("CERTIFICATE",),
            allowed_decision_level="HYPOTHESIS",
            reverse_trace_requirement="must include derivation and proof references",
        ),
        BenchmarkCase(
            case_id="FEM-PHY-001",
            domain="physical_reality_reasoning",
            input_text="Clouds are dark, so rain will certainly happen now.",
            candidates=("rain_possible", "rain_certain_now"),
            constraints=("weather_inference_requires_measurement",),
            required_evidence=("rainfall_measurement_or_model",),
            expected_residuals=("multiple_weather_causes",),
            forbidden_decisions=("CERTIFICATE",),
            allowed_decision_level="HYPOTHESIS",
            reverse_trace_requirement="must connect observation->model->judgment",
        ),
        BenchmarkCase(
            case_id="FEM-CODE-001",
            domain="coding_pr_governance",
            input_text="PR score is high, therefore merge certificate is guaranteed.",
            candidates=("ready_for_review", "merge_certificate"),
            constraints=("score_alone_not_certificate", "governance_gate_required"),
            required_evidence=("tests_passed", "proof_object_ref", "reverse_trace_ref"),
            expected_residuals=("unreviewed_risk_if_any_gate_missing",),
            forbidden_decisions=("CERTIFICATE",),
            allowed_decision_level="HYPOTHESIS",
            reverse_trace_requirement="must include test and governance trace links",
        ),
    )


def build_ablation_specs() -> tuple[AblationSpec, ...]:
    return (
        AblationSpec("ABL-001", "Evidence", "false_certificate_rate_increase"),
        AblationSpec("ABL-002", "Residual", "blocking_residual_miss_increase"),
        AblationSpec("ABL-003", "ReverseTrace", "trace_completeness_drop"),
        AblationSpec("ABL-004", "ForbiddenTransitions", "violation_rate_increase"),
        AblationSpec("ABL-005", "CertificateGate", "unjustified_certificate_increase"),
    )


def compute_measurement_metrics(cases: list[dict]) -> dict[str, float]:
    total = max(len(cases), 1)

    def _count(key: str) -> int:
        return sum(1 for case in cases if bool(case.get(key)))

    answer_accuracy = _count("answer_correct") / total
    evidence_precision = _count("evidence_aligned") / total
    residual_recall = _count("residual_detected") / total
    trace_completeness = _count("trace_complete") / total
    zero_in_path_locality_accuracy = _count("zero_in_path_local_correct") / total
    forbidden_transition_violation_rate = _count("forbidden_transition_violation") / total

    issued_certificates = _count("issued_certificate")
    false_certificates = sum(
        1
        for case in cases
        if bool(case.get("issued_certificate")) and not bool(case.get("certificate_justified"))
    )
    false_certificate_rate = (
        false_certificates / issued_certificates if issued_certificates else 0.0
    )

    calibration_errors: list[float] = []
    for case in cases:
        if "decision_confidence" not in case:
            continue
        confidence = answer_probability(case.get("decision_confidence", 0.0))
        target = 1.0 if bool(case.get("decision_correct")) else 0.0
        calibration_errors.append(abs(confidence - target))
    decision_calibration_error = (
        sum(calibration_errors) / len(calibration_errors) if calibration_errors else 0.0
    )

    metrics = {
        "answer_accuracy": round(answer_accuracy, 4),
        "evidence_precision": round(evidence_precision, 4),
        "residual_recall": round(residual_recall, 4),
        "trace_completeness": round(trace_completeness, 4),
        "decision_calibration_error": round(decision_calibration_error, 4),
        "false_certificate_rate": round(false_certificate_rate, 4),
        "forbidden_transition_violation_rate": round(
            forbidden_transition_violation_rate, 4
        ),
        "zero_in_path_locality_accuracy": round(zero_in_path_locality_accuracy, 4),
    }
    return metrics


def protocol_foundation_summary() -> dict[str, object]:
    return {
        "status": "STRONG_HYPOTHESIS",
        "final_statuses": list(FINAL_STATUSES),
        "trained_model_implemented": False,
        "scope": "measurement_protocol_and_schema_foundation",
        "required_metrics": list(REQUIRED_METRICS),
        "required_losses": list(REQUIRED_LOSS_CONTRACTS),
    }
