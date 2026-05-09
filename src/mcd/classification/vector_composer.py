"""VectorComposer — fractal composition of concept vectors into a prompt-level vector.

Formula:
    V(prompt) = normalize(Σ w_i * V(concept_i) + intent_bias + domain_bias)

Weights default to equal; all secondary labels are preserved (no winner-takes-all).
"""
from __future__ import annotations

import math
from mcd.classification.prompt_frame import PromptConcept


# Intent → dimension boosts
_INTENT_BIAS: dict[str, dict[str, dict[str, float]]] = {
    "judge": {
        "judgment_types": {"epistemic": 0.10, "shari": 0.10},
    },
    "build": {
        "judgment_types": {"technical": 0.15, "practical": 0.10},
        "knowledge_categories": {"technology": 0.15},
    },
    "define": {
        "judgment_types": {"epistemic": 0.10},
        "knowledge_categories": {"language": 0.15},
    },
    "explain": {
        "judgment_types": {"epistemic": 0.10},
        "knowledge_categories": {"method": 0.10},
    },
    "plan": {
        "judgment_types": {"practical": 0.15, "technical": 0.10},
    },
}

_DIMENSIONS = (
    "root_domain",
    "concept_types",
    "knowledge_categories",
    "judgment_hints",
    "evidence_hints",
)

# Mapping from PromptConcept field names to output key names
_CONCEPT_FIELD_MAP = {
    "root_domain": "root_domain",
    "concept_type": "concept_types",
    "knowledge_category": "knowledge_categories",
    "judgment_hint": "judgment_types",
    "evidence_hint": "evidence_needs",
}


class VectorComposer:
    """Compose concept-level vectors into a unified prompt-level vector."""

    def compose(
        self,
        concepts: list[PromptConcept],
        intent: str = "",
    ) -> dict[str, dict[str, float]]:
        """Return composed vectors for all dimensions.

        Each dimension is a dict[label → float] with values in [0, 1].
        Secondary labels are preserved; no single label dominates entirely.
        """
        if not concepts:
            return {
                "root_domain": {},
                "concept_types": {},
                "knowledge_categories": {},
                "judgment_types": {},
                "evidence_needs": {},
            }

        # Accumulate per-dimension totals
        accumulator: dict[str, dict[str, float]] = {
            "root_domain": {},
            "concept_types": {},
            "knowledge_categories": {},
            "judgment_types": {},
            "evidence_needs": {},
        }

        weight = 1.0 / len(concepts)
        for concept in concepts:
            for concept_field, output_key in _CONCEPT_FIELD_MAP.items():
                dim_dict: dict[str, float] = getattr(concept, concept_field, {})
                for label, score in dim_dict.items():
                    accumulator[output_key][label] = (
                        accumulator[output_key].get(label, 0.0) + weight * score
                    )

        # Apply intent biases
        bias = _INTENT_BIAS.get(intent, {})
        for output_key, label_boosts in bias.items():
            for label, boost in label_boosts.items():
                accumulator[output_key][label] = min(
                    1.0, accumulator[output_key].get(label, 0.0) + boost
                )

        # Normalize each dimension independently to [0, 1]
        # but preserve relative magnitudes (soft cap, not hard normalisation)
        result: dict[str, dict[str, float]] = {}
        for key, scores in accumulator.items():
            if not scores:
                result[key] = {}
                continue
            max_score = max(scores.values())
            if max_score > 1.0:
                result[key] = {
                    label: round(v / max_score, 4) for label, v in scores.items()
                }
            else:
                result[key] = {label: round(v, 4) for label, v in scores.items()}

        return result
