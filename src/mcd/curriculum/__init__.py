"""Phase 5.3 — Cognitive Curriculum Learning for the Reasoning Mind."""
from __future__ import annotations

from .cognitive_unit import CognitiveUnit
from .reality_frame import RealityFrame, RelationTriple
from .curriculum_schema import VALID_LEVELS, VALID_TARGET_LAYERS, VALID_CERTAINTY_POLICIES, VALID_DIFFICULTIES
from .curriculum_dataset import CurriculumDataset
from .curriculum_generator import CurriculumGenerator
from .curriculum_validator import CurriculumValidator, CurriculumValidationReport
from .curriculum_evaluator import CurriculumEvaluator, CurriculumEvaluationReport
from .calibration_bridge import CalibrationBridge
from .industrial_bridge import IndustrialBridge
from .learning_profiles import LearningProfile, PROFILES
from .progression import ProgressionTracker
from .report import generate_curriculum_report
from .serializers import cognitive_unit_to_dict, reality_frame_to_dict

__all__ = [
    "CognitiveUnit", "RealityFrame", "RelationTriple",
    "VALID_LEVELS", "VALID_TARGET_LAYERS", "VALID_CERTAINTY_POLICIES", "VALID_DIFFICULTIES",
    "CurriculumDataset", "CurriculumGenerator",
    "CurriculumValidator", "CurriculumValidationReport",
    "CurriculumEvaluator", "CurriculumEvaluationReport",
    "CalibrationBridge", "IndustrialBridge",
    "LearningProfile", "PROFILES",
    "ProgressionTracker",
    "generate_curriculum_report",
    "cognitive_unit_to_dict", "reality_frame_to_dict",
]
