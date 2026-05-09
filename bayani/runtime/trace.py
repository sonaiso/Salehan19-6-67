"""Epistemic trace recorder for the Bayani Mustadil Runtime Engine.

Every layer-to-layer transition is recorded as an
:class:`~bayani.runtime.contracts.EpistemicTraceStep` and appended to an
:class:`~bayani.runtime.contracts.EpistemicTrace` instance.

The bridge description for each transition is looked up from a static table
first; if no entry is found a generic description is generated so that the
trace is always complete.
"""

from __future__ import annotations

from typing import List

from bayani.runtime.contracts import EpistemicTrace, EpistemicTraceStep


# ---------------------------------------------------------------------------
# Static bridge descriptions
# ---------------------------------------------------------------------------
# Key: (from_layer, to_layer)  →  bridge description

_BRIDGE_TABLE: dict[tuple[str, str], str] = {
    ("reality_grounding_layer", "prior_opinion_filter_layer"):
        "existence confirmed; prior opinions must now be separated from evidence",
    ("prior_opinion_filter_layer", "differentiation_layer"):
        "clean evidence base allows concept differentiation",
    ("differentiation_layer", "essence_assignment_layer"):
        "concepts distinguished; essence can now be assigned",
    ("essence_assignment_layer", "domain_assignment_layer"):
        "essence assigned; domain placement follows",
    ("domain_assignment_layer", "relational_mapping_layer"):
        "domain fixed; relational structure can be mapped",
    ("relational_mapping_layer", "arabic_operator_layer"):
        "relations mapped; Arabic operators need validation",
    ("arabic_operator_layer", "binding_layer"):
        "operators validated; entity can be bound to documented reference",
    ("binding_layer", "concept_formation_layer"):
        "entity bound; concept formation proceeds on solid ground",
    ("concept_formation_layer", "judgment_formation_layer"):
        "concept formed; judgment can now be generated",
    ("judgment_formation_layer", "signifier_analysis_layer"):
        "judgment formed; signifier analysis validates its linguistic basis",
    ("signifier_analysis_layer", "signified_analysis_layer"):
        "signifier analysed; signified must be examined next",
    ("signified_analysis_layer", "signifier_signified_relation_layer"):
        "signified examined; dall-madlul relation must be established",
    ("signifier_signified_relation_layer", "mantuq_layer"):
        "dall-madlul relation confirmed; explicit meaning can be extracted",
    ("mantuq_layer", "mafhoom_layer"):
        "mafhoom_requires_mantuq — mantuq rank established before implicit meaning",
    ("mafhoom_layer", "general_specific_layer"):
        "implicit meaning determined; scope analysis follows",
    ("general_specific_layer", "absolute_restricted_layer"):
        "scope determined; mutlaq/muqayyad check follows",
    ("absolute_restricted_layer", "causal_juridical_relations_layer"):
        "mutlaq/muqayyad settled; causal relations can now be classified",
    ("causal_juridical_relations_layer", "tahqeeq_manat_layer"):
        "causal relations classified; manat must be verified before application",
    ("tahqeeq_manat_layer", "application_layer"):
        "tahqeeq_manat_completed — application permitted only after manat verified",
    ("application_layer", "epistemic_audit_layer"):
        "application complete; final audit closes the pipeline",
    # Shortcut paths (when earlier layers are skipped for a PT type)
    ("prior_opinion_filter_layer", "epistemic_audit_layer"):
        "direct audit after existence check (short pipeline)",
    ("essence_assignment_layer", "epistemic_audit_layer"):
        "definition complete; audit finalises output",
    ("relational_mapping_layer", "epistemic_audit_layer"):
        "relational mapping complete; audit finalises output",
    ("mantuq_layer", "epistemic_audit_layer"):
        "mantuq determined; audit finalises output",
    ("tahqeeq_manat_layer", "epistemic_audit_layer"):
        "tahqeeq complete; audit finalises output",
}

# Invariants that are checked at specific transitions
_TRANSITION_INVARIANTS: dict[tuple[str, str], str] = {
    ("mantuq_layer", "mafhoom_layer"):    "NoMafhumStrongerThanMantuq",
    ("tahqeeq_manat_layer", "application_layer"): "NoApplicationWithoutTahqeeqManat",
    ("causal_juridical_relations_layer", "tahqeeq_manat_layer"): "NoManatAsIllah",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_trace(layer_sequence: List[str]) -> EpistemicTrace:
    """Build an :class:`EpistemicTrace` for an ordered list of layer names.

    A :class:`EpistemicTraceStep` is created for every consecutive pair of
    layers.
    """
    trace = EpistemicTrace()
    for i in range(len(layer_sequence) - 1):
        from_layer = layer_sequence[i]
        to_layer = layer_sequence[i + 1]
        key = (from_layer, to_layer)
        bridge = _BRIDGE_TABLE.get(
            key,
            f"{from_layer} completes prerequisites for {to_layer}",
        )
        forbidden_jump_checked = _TRANSITION_INVARIANTS.get(key, "")
        step = EpistemicTraceStep(
            from_layer=from_layer,
            to_layer=to_layer,
            bridge=bridge,
            validated=True,
            forbidden_jump_checked=forbidden_jump_checked,
        )
        trace.add(step)
    return trace
