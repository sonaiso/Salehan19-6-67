"""Phase 5.3/7.1 — Cognitive Curriculum Learning for the Reasoning Mind."""
from __future__ import annotations

from .cognitive_unit import CognitiveUnit
from .cognitive_node import CognitiveNode
from .cognitive_edge import CognitiveEdge
from .cognitive_graph import CognitiveGraph
from .reality_frame import RealityFrame, RelationTriple
from .curriculum_schema import (
    VALID_LEVELS, VALID_TARGET_LAYERS, VALID_CERTAINTY_POLICIES, VALID_DIFFICULTIES,
    LEVEL_NAMES, LEVEL_PRIMARY_LAYERS,
)
from .curriculum_dataset import CurriculumDataset
from .curriculum_generator import CurriculumGenerator
from .curriculum_validator import CurriculumValidator, CurriculumValidationReport
from .curriculum_evaluator import CurriculumEvaluator, CurriculumEvaluationReport
from .calibration_bridge import CalibrationBridge, CurriculumCoverageReport
from .industrial_bridge import IndustrialBridge
from .learning_profiles import LearningProfile, PROFILES, get_profile
from .progression import ProgressionTracker
from .report import generate_curriculum_report
from .serializers import cognitive_unit_to_dict, reality_frame_to_dict
from .vector_space import ROLE_DIMENSIONS
from .role_vector import build_role_vector, validate_role_vector, blend_role_vectors
from .domain_vector import build_domain_vector, validate_domain_vector, blend_domain_vectors
from .composition_function import CompositionInput, CompositionResult, compose_vectors
from .mathematical_contract import MathematicalContractResult, check_mathematical_contract
from .graph_validator import GraphValidationResult, validate_graph
from .vector_validator import VectorValidationResult, validate_role_vector as validate_vector
from .invariant_validator import InvariantValidationResult, InvariantViolation, validate_invariants
from .golden_examples import GoldenExample, load_golden_examples
from .adversarial_curriculum import AdversarialExample, load_adversarial_examples, ADVERSARIAL_CATEGORIES
from .qualification_bridge import CurriculumQualificationMetrics, compute_qualification_metrics
from .depth_metrics import DepthMetricsCalculator, DepthMetricsReport
from .curriculum_coverage_matrix import CurriculumCoverageMatrix, CurriculumCoverageReport as CoverageCoverageReport
from .residual_curriculum_builder import (
    ResidualCurriculumBuilder, ResidualCurriculumUnit, ResidualBuildReport,
)

__all__ = [
    "CognitiveUnit", "CognitiveNode", "CognitiveEdge", "CognitiveGraph",
    "RealityFrame", "RelationTriple",
    "VALID_LEVELS", "VALID_TARGET_LAYERS", "VALID_CERTAINTY_POLICIES", "VALID_DIFFICULTIES",
    "LEVEL_NAMES", "LEVEL_PRIMARY_LAYERS",
    "CurriculumDataset", "CurriculumGenerator",
    "CurriculumValidator", "CurriculumValidationReport",
    "CurriculumEvaluator", "CurriculumEvaluationReport",
    "CalibrationBridge", "CurriculumCoverageReport", "IndustrialBridge",
    "LearningProfile", "PROFILES", "get_profile",
    "ProgressionTracker",
    "generate_curriculum_report",
    "cognitive_unit_to_dict", "reality_frame_to_dict",
    "ROLE_DIMENSIONS",
    "build_role_vector", "validate_role_vector", "blend_role_vectors",
    "build_domain_vector", "validate_domain_vector", "blend_domain_vectors",
    "CompositionInput", "CompositionResult", "compose_vectors",
    "MathematicalContractResult", "check_mathematical_contract",
    "GraphValidationResult", "validate_graph",
    "VectorValidationResult", "validate_vector",
    "InvariantValidationResult", "InvariantViolation", "validate_invariants",
    "GoldenExample", "load_golden_examples",
    "AdversarialExample", "load_adversarial_examples", "ADVERSARIAL_CATEGORIES",
    "CurriculumQualificationMetrics", "compute_qualification_metrics",
    "DepthMetricsCalculator", "DepthMetricsReport",
    "CurriculumCoverageMatrix", "CoverageCoverageReport",
    "ResidualCurriculumBuilder", "ResidualCurriculumUnit", "ResidualBuildReport",
]
