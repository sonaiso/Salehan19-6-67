"""ConceptGrounder — turns a meaning into a concept only when grounded in reality.

A concept (مفهوم) in Nabhani's method is not simply the linguistic meaning of a word;
it is a meaning for which a corresponding reality has been perceived.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, List, Optional


GROUNDING_THRESHOLD = 0.60


@dataclass
class GroundedConcept:
    concept_id: str
    name: str
    source_meaning: str
    grounded_reality: Optional[str]
    supporting_relations: List[str]
    evidence: List[str]
    certainty: float
    status: str   # "grounded" | "partially_grounded" | "ungrounded"


class ConceptGrounder:
    """Ground a meaning to a concept using the PriorKnowledgeStore."""

    def ground(self, meaning: str, prior_store: Any = None) -> GroundedConcept:
        """Attempt to ground *meaning* into a concept.

        Checks:
        1. Is there a Thing/property/relation in PriorKnowledgeStore?
        2. Or is there a Fact that mentions this meaning?
        3. Or are there enough supporting relations?
        Assigns certainty accordingly and only marks as 'grounded' when ≥ threshold.
        """
        stem = _simple_stem(meaning)
        stripped = _strip_al(meaning)

        grounded_reality: Optional[str] = None
        supporting_relations: List[str] = []
        evidence_list: List[str] = []
        certainty = 0.30  # baseline for a mere linguistic meaning

        if prior_store is not None:
            # Check Things
            for query in [meaning, stripped, stem]:
                things = prior_store.query_things_by_name(query) if query else []
                if things:
                    thing = things[0]
                    grounded_reality = getattr(thing, "name", str(thing))
                    evidence_list.append(f"thing:{grounded_reality}")
                    certainty = max(certainty, 0.80)
                    break

            # Check Facts
            if not grounded_reality and hasattr(prior_store, "facts"):
                facts = prior_store.facts.find_by_claim(meaning)
                if not facts:
                    facts = prior_store.facts.find_by_claim(stem)
                if facts:
                    grounded_reality = meaning
                    evidence_list.append(f"fact:{facts[0].claim if hasattr(facts[0], 'claim') else str(facts[0])}")
                    certainty = max(certainty, 0.65)

            # Check Relations
            if hasattr(prior_store, "query_relations"):
                rels = prior_store.query_relations(source_id=meaning) + prior_store.query_relations(target_id=meaning)
                if rels:
                    supporting_relations = [r.relation_type for r in rels[:5]]
                    certainty = max(certainty, 0.55 + 0.05 * min(len(rels), 5))

        # Determine status
        if certainty >= GROUNDING_THRESHOLD and grounded_reality:
            status = "grounded"
        elif certainty >= GROUNDING_THRESHOLD * 0.7 and (grounded_reality or supporting_relations):
            status = "partially_grounded"
            certainty = min(certainty, GROUNDING_THRESHOLD - 0.01)
        else:
            status = "ungrounded"
            certainty = min(certainty, 0.45)

        return GroundedConcept(
            concept_id=f"concept_{uuid.uuid4().hex[:8]}",
            name=meaning,
            source_meaning=meaning,
            grounded_reality=grounded_reality,
            supporting_relations=supporting_relations,
            evidence=evidence_list,
            certainty=round(certainty, 4),
            status=status,
        )


# ---------------------------------------------------------------------------
# Helpers (duplicated to keep module self-contained)
# ---------------------------------------------------------------------------

def _strip_al(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word


def _simple_stem(word: str) -> str:
    stem = _strip_al(word)
    for suffix in ("ة", "ون", "ين"):
        if stem.endswith(suffix) and len(stem) > len(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem
