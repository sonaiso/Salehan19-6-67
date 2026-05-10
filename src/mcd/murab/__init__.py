"""mcd.murab — Arabic Mu'rab / I'rab Relational Engineering Layer (Phase 7.5).

Exports the main public API.
"""
from mcd.murab.murab_schema import MurabUnit
from mcd.murab.irab_case import IrabCase, IrabCaseRegistry, IRAB_CASE_REGISTRY
from mcd.murab.irab_marker import IrabMarker, IrabMarkerRegistry, IRAB_MARKER_REGISTRY
from mcd.murab.governing_factor import (
    GoverningFactor,
    GoverningFactorRegistry,
    GOVERNING_FACTOR_REGISTRY,
)
from mcd.murab.murab_graph_builder import (
    MurabGraph,
    MurabGraphBuilder,
    MurabEdge,
    MurabUnitNode,
    IrabCaseNode,
    MarkerNode,
    GoverningFactorNode,
    SyntacticRoleNode,
    SemanticRoleNode,
    RelationNode,
)
from mcd.murab.case_resolver import CaseResolver
from mcd.murab.syntactic_role_resolver import SyntacticRoleResolver
from mcd.murab.nominative_resolver import NominativeResolver
from mcd.murab.accusative_resolver import AccusativeResolver
from mcd.murab.genitive_resolver import GenitiveResolver
from mcd.murab.jussive_resolver import JussiveResolver
from mcd.murab.mood_resolver import MoodResolver
from mcd.murab.agreement_engine import AgreementEngine
from mcd.murab.dependency_resolver import DependencyResolver
from mcd.murab.idafa_engine import IdafaEngine
from mcd.murab.tawabi_engine import TawabiEngine
from mcd.murab.hal_tamyiz_engine import HalTamyizEngine
from mcd.murab.zarf_engine import ZarfEngine
from mcd.murab.estimated_irab_engine import EstimatedIrabEngine
from mcd.murab.irregular_irab_registry import (
    IrregularIrabRegistry,
    IRREGULAR_IRAB_REGISTRY,
)
from mcd.murab.murab_trace_linker import MurabTraceLinker, TraceLink
from mcd.murab.murab_certainty_policy import MurabCertaintyPolicy
from mcd.murab.murab_report import MurabReport
from mcd.murab.serializers import (
    murab_units_to_json,
    murab_units_to_markdown,
    murab_graph_to_json,
    murab_graph_to_markdown,
)
from mcd.murab.murab_analyzer import MurabAnalyzer

__all__ = [
    # Schema
    "MurabUnit",
    # I'rab cases
    "IrabCase",
    "IrabCaseRegistry",
    "IRAB_CASE_REGISTRY",
    # Markers
    "IrabMarker",
    "IrabMarkerRegistry",
    "IRAB_MARKER_REGISTRY",
    # Governing factors
    "GoverningFactor",
    "GoverningFactorRegistry",
    "GOVERNING_FACTOR_REGISTRY",
    # Graph
    "MurabGraph",
    "MurabGraphBuilder",
    "MurabEdge",
    "MurabUnitNode",
    "IrabCaseNode",
    "MarkerNode",
    "GoverningFactorNode",
    "SyntacticRoleNode",
    "SemanticRoleNode",
    "RelationNode",
    # Resolvers
    "CaseResolver",
    "SyntacticRoleResolver",
    "NominativeResolver",
    "AccusativeResolver",
    "GenitiveResolver",
    "JussiveResolver",
    "MoodResolver",
    # Engines
    "AgreementEngine",
    "DependencyResolver",
    "IdafaEngine",
    "TawabiEngine",
    "HalTamyizEngine",
    "ZarfEngine",
    "EstimatedIrabEngine",
    "IrregularIrabRegistry",
    "IRREGULAR_IRAB_REGISTRY",
    # Trace & certainty
    "MurabTraceLinker",
    "TraceLink",
    "MurabCertaintyPolicy",
    # Reports & serializers
    "MurabReport",
    "murab_units_to_json",
    "murab_units_to_markdown",
    "murab_graph_to_json",
    "murab_graph_to_markdown",
    # Main analyzer
    "MurabAnalyzer",
]
