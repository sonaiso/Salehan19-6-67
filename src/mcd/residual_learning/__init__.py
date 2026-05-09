"""Phase 7 — Cognitive Residual Learning Engine.

GPT suggests. Mathematical Contract judges. Cognitive Residual teaches.
"""
from .proposal_schema import GPTProposal, ProposalGraph, ProposalType
from .residual_schema import CognitiveResidual, ResidualType, Severity
from .residual_calculator import ResidualCalculator
from .residual_classifier import ResidualClassifier
from .learning_action import LearningAction, ActionType
from .learning_router import LearningRouter
from .residual_dataset_builder import ResidualDatasetBuilder
from .residual_calibration import ResidualCalibrationEngine, ResidualCalibrationReport
from .residual_test_generator import ResidualTestGenerator, TestSpec
from .residual_report import ResidualReport
from .engine import CognitiveResidualLearningEngine, ResidualAnalysisResult

__all__ = [
    "GPTProposal",
    "ProposalGraph",
    "ProposalType",
    "CognitiveResidual",
    "ResidualType",
    "Severity",
    "ResidualCalculator",
    "ResidualClassifier",
    "LearningAction",
    "ActionType",
    "LearningRouter",
    "ResidualDatasetBuilder",
    "ResidualCalibrationEngine",
    "ResidualCalibrationReport",
    "ResidualTestGenerator",
    "TestSpec",
    "ResidualReport",
    "CognitiveResidualLearningEngine",
    "ResidualAnalysisResult",
]
