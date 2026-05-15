"""Evaluation & Industrial Readiness Layer (EIRL) — audits, KPIs, benchmarks, and readiness scoring."""

from mcd.evaluation.certainty_calibration import CertaintyCalibration, CalibrationReport
from mcd.evaluation.fractal_embedding_measurement_protocol import (
    FractalEmbeddingSpec,
    GovernedMeaningPath,
    EvidenceBearingEdge,
    ResidualAwareVector,
    TraceAwareVector,
    DecisionCalibrationTarget,
    BenchmarkCase,
    AblationSpec,
)
from mcd.evaluation.fractal_benchmark_dataset import (
    ALLOWED_DECISION_LEVELS,
    DOMAIN_FILES,
    REQUIRED_CASE_FIELDS,
    benchmark_dataset_summary,
    iter_all_cases,
    load_all_domain_cases,
    load_domain_cases,
    validate_all_cases,
    validate_case,
)
from mcd.evaluation.fractal_baseline_comparison import run_fractal_baseline_comparison
from mcd.evaluation.prior_aware_baseline_ablation import (
    compute_prior_coverage_matrix,
    run_prior_aware_baseline_ablation,
)
from mcd.evaluation.judgment_routing_matrix import JudgmentRoutingMatrix, MatrixEntry

__all__ = [
    "CertaintyCalibration",
    "CalibrationReport",
    "JudgmentRoutingMatrix",
    "MatrixEntry",
    "FractalEmbeddingSpec",
    "GovernedMeaningPath",
    "EvidenceBearingEdge",
    "ResidualAwareVector",
    "TraceAwareVector",
    "DecisionCalibrationTarget",
    "BenchmarkCase",
    "AblationSpec",
    "ALLOWED_DECISION_LEVELS",
    "DOMAIN_FILES",
    "REQUIRED_CASE_FIELDS",
    "benchmark_dataset_summary",
    "iter_all_cases",
    "load_all_domain_cases",
    "load_domain_cases",
    "validate_all_cases",
    "validate_case",
    "run_fractal_baseline_comparison",
    "run_prior_aware_baseline_ablation",
    "compute_prior_coverage_matrix",
]
