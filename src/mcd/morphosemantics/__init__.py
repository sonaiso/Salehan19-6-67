"""Phase 7.3 — Arabic Morphosemantic Fractal Engine.

Every Arabic word is a folded cognitive graph: the root is the center of
potential, the pattern is the operator that unfolds meaning, and the
masdar abstracts the event.  This package provides the engines, data
models, and resolvers needed to traverse that graph programmatically.
"""
from __future__ import annotations

from mcd.morphosemantics.root_ontology import RootNode, load_root_ontology
from mcd.morphosemantics.pattern_operator_registry import PatternOperator, PatternOperatorRegistry
from mcd.morphosemantics.masdar_event_ontology import MasdarEvent, load_masdar_events
from mcd.morphosemantics.jamid_essence_ontology import JamidEssence, load_jamid_essences
from mcd.morphosemantics.folded_word_graph import FoldedWordGraph
from mcd.morphosemantics.concept_center import ConceptCenter

__all__ = [
    "RootNode",
    "load_root_ontology",
    "PatternOperator",
    "PatternOperatorRegistry",
    "MasdarEvent",
    "load_masdar_events",
    "JamidEssence",
    "load_jamid_essences",
    "FoldedWordGraph",
    "ConceptCenter",
]
