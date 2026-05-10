"""Mabni package — Arabic Mabni Logical-Pragmatic Control Layer."""
from __future__ import annotations

from mcd.mabni.answer_particle_resolver import AnswerParticleResolver, AnswerParticleResult
from mcd.mabni.attached_pronoun_unfolder import AttachedPronounUnfolder, PronounUnfoldResult
from mcd.mabni.conditional_engine import ConditionalEngine, ConditionalResult
from mcd.mabni.counterfactual_engine import CounterfactualEngine, CounterfactualResult
from mcd.mabni.demonstrative_resolver import DemonstrativeResolver, DemonstrativeResult
from mcd.mabni.emphasis_evidence_separator import EmphasisEvidenceSeparator, EmphasisAnalysisResult
from mcd.mabni.exception_restriction_engine import ExceptionRestrictionEngine, ExceptionResult
from mcd.mabni.in_resolver import InResolver, InResolutionResult
from mcd.mabni.la_resolver import LaResolver, LaResolutionResult
from mcd.mabni.ma_resolver import MaResolver, MaResolutionResult
from mcd.mabni.mabni_certainty_policy import MabniCertaintyPolicy, CertaintyPolicyResult
from mcd.mabni.mabni_graph_builder import MabniGraph, MabniGraphBuilder, MabniEdge, MabniNode
from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_registry import MabniRegistry
from mcd.mabni.mabni_report import MabniReport
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction
from mcd.mabni.mabni_trace_linker import MabniTraceLinker, MabniTraceLink, MabniTraceReport
from mcd.mabni.mabni_unfolder import MabniUnfolder, MabniUnfoldResult
from mcd.mabni.man_resolver import ManResolver, ManResolutionResult
from mcd.mabni.pragmatic_vector import MabniPragmaticVector
from mcd.mabni.preposition_resolver import PrepositionResolver, PrepositionResolutionResult
from mcd.mabni.qasr_engine import QasrEngine, QasrResult
from mcd.mabni.relative_pronoun_resolver import RelativePronounResolver, RelativePronounResult
from mcd.mabni.speech_act_resolver import SpeechActResolver, SpeechActResult
from mcd.mabni.serializers import to_json, from_json, to_jsonl

__all__ = [
    # Schema
    "MabniType", "LogicalFunction", "PragmaticFunction", "CertaintyEffect",
    # Core operator
    "MabniOperator", "MabniPragmaticVector",
    # Registry
    "MabniRegistry",
    # Resolvers
    "MaResolver", "MaResolutionResult",
    "ManResolver", "ManResolutionResult",
    "InResolver", "InResolutionResult",
    "LaResolver", "LaResolutionResult",
    "DemonstrativeResolver", "DemonstrativeResult",
    "RelativePronounResolver", "RelativePronounResult",
    "AnswerParticleResolver", "AnswerParticleResult",
    "PrepositionResolver", "PrepositionResolutionResult",
    "SpeechActResolver", "SpeechActResult",
    "AttachedPronounUnfolder", "PronounUnfoldResult",
    # Engines
    "ConditionalEngine", "ConditionalResult",
    "CounterfactualEngine", "CounterfactualResult",
    "ExceptionRestrictionEngine", "ExceptionResult",
    "QasrEngine", "QasrResult",
    "EmphasisEvidenceSeparator", "EmphasisAnalysisResult",
    # Policy
    "MabniCertaintyPolicy", "CertaintyPolicyResult",
    # Graph
    "MabniGraph", "MabniGraphBuilder", "MabniNode", "MabniEdge",
    # Trace
    "MabniTraceLinker", "MabniTraceLink", "MabniTraceReport",
    # Orchestrator
    "MabniUnfolder", "MabniUnfoldResult",
    # Report
    "MabniReport",
    # Serializers
    "to_json", "from_json", "to_jsonl",
]
