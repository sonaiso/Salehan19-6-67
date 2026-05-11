"""Phase 8 — Cognitive Fractal Kernel (CFK).

Public API:
    CognitiveFractalPipeline  — full pipeline orchestrator
    CognitiveFractalResult    — pipeline output
    CognitiveFractalUnit      — fractal unit schema (N,V,R,O,E,C,P,T,Z)
    KernelProjection          — projection of one coordinate into K
    FractalKernel             — kernel K that unifies three projections
    ProofObject               — final judgment schema
    ProofObjectBuilder        — builds ProofObject from KernelResult
    ConservationLawChecker    — checks five conservation laws
    ComparisonTable           — section-16 comparison table
    ComparisonTableBuilder    — builds ComparisonTable
    StatisticalTransform      — S(x): GPT → fractal
    ArabicSemanticTransform   — A(x): Arabic → fractal
    EpistemicTransform        — E(x): Epistemic → fractal
"""
from mcd.cfk.cfk_schema import (
    CognitiveFractalUnit,
    KernelProjection,
    JudgmentStatus,
    CoordinateType,
    NodeInfo,
    VectorInfo,
    RelationsInfo,
    OperatorsInfo,
    EvidenceInfo,
    CertaintyInfo,
    ProofInfo,
    TraceInfo,
    ResidualInfo,
)
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform, compute_epistemic_certainty
from mcd.cfk.fractal_kernel import FractalKernel, KernelResult
from mcd.cfk.conservation_law import ConservationLawChecker, ConservationCheckResult, ConservationViolation
from mcd.cfk.proof_object import ProofObject, ProofObjectBuilder
from mcd.cfk.cfk_comparison_table import ComparisonTable, ComparisonTableBuilder, ComparisonRow
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline, CognitiveFractalResult
from mcd.cfk.cfk_report import generate_markdown_report, generate_json_report
from mcd.cfk.serializers import cfk_result_to_json, proof_to_json, unit_to_json
from mcd.cfk.cfk_integration_contract import (
    CFKIntegrationContract,
    ContractValidator,
    ContractCheckResult,
    ContractViolation,
    STATISTICAL_TRANSFORM_CONTRACT,
    ARABIC_SEMANTIC_TRANSFORM_CONTRACT,
    MABNI_CONTRACT,
    MURAB_CONTRACT,
    EPISTEMIC_TRANSFORM_CONTRACT,
    PROOF_OBJECT_BUILDER_CONTRACT,
    ALL_CONTRACTS,
    CONTRACTS_BY_LAYER,
)
from mcd.cfk.cross_layer_conservation import (
    CrossLayerConservationChecker,
    CrossLayerConservationReport,
    CrossLayerViolation,
)
from mcd.cfk.reverse_trace import ReverseTrace, ReverseTraceBuilder

__all__ = [
    # Schema
    "CognitiveFractalUnit",
    "KernelProjection",
    "JudgmentStatus",
    "CoordinateType",
    "NodeInfo", "VectorInfo", "RelationsInfo", "OperatorsInfo",
    "EvidenceInfo", "CertaintyInfo", "ProofInfo", "TraceInfo", "ResidualInfo",
    # Transforms
    "StatisticalTransform",
    "ArabicSemanticTransform",
    "EpistemicTransform",
    "compute_epistemic_certainty",
    # Kernel
    "FractalKernel",
    "KernelResult",
    # Conservation
    "ConservationLawChecker",
    "ConservationCheckResult",
    "ConservationViolation",
    # Proof
    "ProofObject",
    "ProofObjectBuilder",
    # Table
    "ComparisonTable",
    "ComparisonTableBuilder",
    "ComparisonRow",
    # Pipeline
    "CognitiveFractalPipeline",
    "CognitiveFractalResult",
    # Reports
    "generate_markdown_report",
    "generate_json_report",
    # Serializers
    "cfk_result_to_json",
    "proof_to_json",
    "unit_to_json",
    # Phase 8.1 — Integration Contract
    "CFKIntegrationContract",
    "ContractValidator",
    "ContractCheckResult",
    "ContractViolation",
    "STATISTICAL_TRANSFORM_CONTRACT",
    "ARABIC_SEMANTIC_TRANSFORM_CONTRACT",
    "MABNI_CONTRACT",
    "MURAB_CONTRACT",
    "EPISTEMIC_TRANSFORM_CONTRACT",
    "PROOF_OBJECT_BUILDER_CONTRACT",
    "ALL_CONTRACTS",
    "CONTRACTS_BY_LAYER",
    # Phase 8.1 — Cross-Layer Conservation
    "CrossLayerConservationChecker",
    "CrossLayerConservationReport",
    "CrossLayerViolation",
    # Phase 8.1 — ReverseTrace
    "ReverseTrace",
    "ReverseTraceBuilder",
]
