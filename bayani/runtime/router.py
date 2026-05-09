"""Pipeline router — maps Prompt Types to ordered layer sequences.

Each PT-xx type maps to a list of pipeline layer keys in the order they must
be executed.  The router enforces:

- PT-07 (Mafhoom) must enter ``mantuq_layer`` *before* ``mafhoom_layer``.
- PT-10 (Application) must include ``tahqeeq_manat_layer`` before
  ``application_layer``.
- PT-09 (Illah/Qiyas) must include ``causal_juridical_relations_layer``
  before any extension or qiyas layer.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------------
# Layer pipeline definitions per Prompt Type
# ---------------------------------------------------------------------------
# Only the layers *required* for each type are listed here (subset of the
# full 21-layer pipeline).  Layers that are always mandatory (e.g.
# epistemic_audit_layer) are appended automatically by get_required_layers().

_BASE_LAYERS: List[str] = [
    "reality_grounding_layer",
    "prior_opinion_filter_layer",
]

_ALWAYS_LAST: List[str] = [
    "epistemic_audit_layer",
]

# Full layer routing table
_PT_LAYER_MAP: Dict[str, List[str]] = {
    # PT-01  Existence
    "PT-01": [
        *_BASE_LAYERS,
    ],

    # PT-02  Definition
    "PT-02": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
    ],

    # PT-03  Attribute
    "PT-03": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "causal_juridical_relations_layer",
    ],

    # PT-04  Relational
    "PT-04": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "relational_mapping_layer",
    ],

    # PT-05  Linguistic/Syntactic
    "PT-05": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "arabic_operator_layer",
        "binding_layer",
        "signifier_analysis_layer",
        "signified_analysis_layer",
        "signifier_signified_relation_layer",
    ],

    # PT-06  Mantuq
    "PT-06": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "relational_mapping_layer",
        "signifier_analysis_layer",
        "signified_analysis_layer",
        "signifier_signified_relation_layer",
        "mantuq_layer",
    ],

    # PT-07  Mafhoom  — MUST enter mantuq before mafhoom
    "PT-07": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "relational_mapping_layer",
        "signifier_analysis_layer",
        "signified_analysis_layer",
        "signifier_signified_relation_layer",
        "mantuq_layer",   # prerequisite enforced here
        "mafhoom_layer",
    ],

    # PT-08  General/Specific
    "PT-08": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "signifier_analysis_layer",
        "mantuq_layer",
        "general_specific_layer",
        "absolute_restricted_layer",
        "tahqeeq_manat_layer",
    ],

    # PT-09  Illah/Qiyas  — MUST include causal_juridical_relations_layer first
    "PT-09": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "relational_mapping_layer",
        "causal_juridical_relations_layer",  # must precede any extension
        "tahqeeq_manat_layer",
    ],

    # PT-10  Application  — MUST include tahqeeq_manat before application
    "PT-10": [
        *_BASE_LAYERS,
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "relational_mapping_layer",
        "causal_juridical_relations_layer",
        "tahqeeq_manat_layer",   # enforced prerequisite
        "application_layer",
    ],
}


def get_required_layers(prompt_type_id: str) -> List[str]:
    """Return the ordered list of pipeline layers for *prompt_type_id*.

    The final ``epistemic_audit_layer`` is always appended.
    Raises :class:`ValueError` if *prompt_type_id* is not recognised.
    """
    if prompt_type_id not in _PT_LAYER_MAP:
        raise ValueError(
            f"Unknown prompt type id: {prompt_type_id!r}. "
            f"Valid values are: {sorted(_PT_LAYER_MAP.keys())}"
        )
    layers = list(_PT_LAYER_MAP[prompt_type_id])
    for last in _ALWAYS_LAST:
        if last not in layers:
            layers.append(last)
    return layers
