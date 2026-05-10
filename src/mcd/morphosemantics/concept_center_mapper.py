"""ConceptCenterMapper — builds a ConceptCenter from a FoldedWordGraph.

This mapper takes a FoldedWordGraph and populates all the axes of a
ConceptCenter, drawing on the root ontology, pattern operator registry,
masdar event ontology, and jamid essence ontology.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from mcd.morphosemantics.concept_center import ConceptCenter, empty_concept_center
from mcd.morphosemantics.folded_word_graph import FoldedWordGraph
from mcd.morphosemantics.root_ontology import get_root_by_id
from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
from mcd.morphosemantics.masdar_event_ontology import get_masdars_by_root
from mcd.morphosemantics.jamid_essence_ontology import get_jamid_by_term
from mcd.morphosemantics.pattern_certainty import PatternCertaintyScorer


class ConceptCenterMapper:
    """Maps a FoldedWordGraph → ConceptCenter with all axes populated."""

    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()
        self._certainty_scorer = PatternCertaintyScorer()

    def map(self, graph: FoldedWordGraph) -> ConceptCenter:
        cc = empty_concept_center(graph.word, graph.selected_root)
        cc.trace_ids = list(graph.trace_ids)

        # Surface forms: include the word itself
        cc.surface_forms = [graph.word]

        # Agency / patienthood / causation / instrument / time-place axes
        # from the pattern operator vector
        pattern_op = self._registry.get(graph.selected_pattern)
        if pattern_op:
            ov = pattern_op.operator_vector
            cc.agency_axis = {"agency": ov.get("agency", 0.0)}
            cc.patienthood_axis = {"patienthood": ov.get("patienthood", 0.0)}
            cc.causation_axis = {"causation": ov.get("causation", 0.0)}
            cc.instrument_axis = {"instrument": ov.get("instrument", 0.0)}
            cc.time_place_axis = {
                "place": ov.get("place", 0.0),
                "time": ov.get("time", 0.0),
            }
            cc.nisba_axis = {"nisba": ov.get("nisba", 0.0)}
            cc.comparison_axis = {"comparison": ov.get("comparison", 0.0)}
            cc.plurality_axis = {"plurality": ov.get("plurality", 0.0)}
            cc.attribute_axis = {
                "intensification": ov.get("intensification", 0.0),
                "reflexivity": ov.get("reflexivity", 0.0),
                "mutawaa": ov.get("mutawaa", 0.0),
                "diminutive": ov.get("diminutive", 0.0),
                "request": ov.get("request", 0.0),
            }

        # Essence axis from root
        root = get_root_by_id(graph.selected_root)
        if root:
            cc.essence_axis = {
                "semantic_core": 1.0,
                "causation_potential": root.causation_potential,
                "metaphor_potential": root.metaphor_potential,
            }
            cc.root_family = root.root_id
            cc.surface_forms = list({graph.word} | set(root.examples[:3]))

        # Event axis from masdar ontology
        masdars = get_masdars_by_root(graph.selected_root)
        if masdars:
            ev = masdars[0].event_vector
            cc.event_axis = {k: v for k, v in ev.items()}
        else:
            cc.event_axis = dict(graph.event_vector)

        # Certainty axis
        cert_result = self._certainty_scorer.score(
            graph.selected_pattern, graph.selected_root,
            override_policy=graph.certainty_policy,
        )
        cc.certainty_axis = {
            "certainty_score": cert_result.certainty_score,
            "certainty_policy": cert_result.certainty_policy,
        }

        # Context axis from domain vector
        cc.context_axis = dict(graph.domain_vector)

        # Evidence axis: how many masdars/roots we have to back the claim
        cc.evidence_axis = {
            "masdar_count": float(len(masdars)),
            "root_certainty": root.certainty if root else 0.5,
        }

        return cc
