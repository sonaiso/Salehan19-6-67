"""DalMadlulMapper — maps sign (دال) → meaning (مدلول) → grounded concept (مفهوم).

Types of semantic reference (أنواع الدلالة):
- mutabaqa  (مطابقة)  : word fully covers the meaning
- tadammun  (تضمن)    : word covers a part of the meaning
- iltizam   (التزام)  : meaning implied but not contained in the word
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DalMadlulMapping:
    dal: str                  # the sign / symbol / word
    madlul: str               # the intended meaning
    concept: Optional[str]    # grounded concept name (None if not grounded)
    dalalah_type: str         # "mutabaqa" | "tadammun" | "iltizam"
    grounding_status: str     # "ungrounded_linguistic_meaning" | "partially_grounded" | "grounded_concept" | "verified_concept"
    explanation: str


# Simple Arabic morphology helpers
def _strip_al(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word


def _simple_stem(word: str) -> str:
    stem = _strip_al(word)
    if stem.endswith("ة") and len(stem) > 1:
        stem = stem[:-1]
    if stem.endswith("ون") and len(stem) > 2:
        stem = stem[:-2]
    if stem.endswith("ين") and len(stem) > 2:
        stem = stem[:-2]
    return stem


class DalMadlulMapper:
    """Map Arabic words to their semantic reference and grounding status."""

    def map(
        self,
        dal: str,
        madlul: str,
        has_reality: bool = False,
        prior_knowledge: Optional[str] = None,
        verified: bool = False,
    ) -> DalMadlulMapping:
        """Map a single dal → madlul pair.

        Args:
            dal:            The sign/word.
            madlul:         Its intended meaning.
            has_reality:    Whether a corresponding reality was found.
            prior_knowledge: Description of prior knowledge supporting the concept.
            verified:       Whether the concept has been independently verified.
        """
        # Determine dalalah type by simple heuristics
        if dal.strip() == madlul.strip():
            dalalah_type = "mutabaqa"
        elif _simple_stem(dal) in madlul or _simple_stem(madlul) in dal:
            dalalah_type = "tadammun"
        else:
            dalalah_type = "iltizam"

        # Determine grounding status
        if verified and has_reality:
            grounding_status = "verified_concept"
            concept = madlul
        elif has_reality or prior_knowledge:
            grounding_status = "grounded_concept"
            concept = madlul
        elif prior_knowledge and not has_reality:
            grounding_status = "partially_grounded"
            concept = madlul
        else:
            grounding_status = "ungrounded_linguistic_meaning"
            concept = None

        if grounding_status == "ungrounded_linguistic_meaning":
            explanation = (
                f"'{dal}' → معنى لغوي '{madlul}' بلا واقع مدرك؛ "
                "لا يُعدّ مفهومًا بعد."
            )
        elif grounding_status == "partially_grounded":
            explanation = (
                f"'{dal}' → '{madlul}' مدعوم جزئيًا بمعلومات سابقة لكن لا واقع صريح."
            )
        elif grounding_status == "grounded_concept":
            explanation = (
                f"'{dal}' → مفهوم '{madlul}' مؤسَّس على واقع أو معلومات سابقة."
            )
        else:
            explanation = (
                f"'{dal}' → مفهوم '{madlul}' محقَّق ومُدرَك له واقع ثابت."
            )

        return DalMadlulMapping(
            dal=dal,
            madlul=madlul,
            concept=concept,
            dalalah_type=dalalah_type,
            grounding_status=grounding_status,
            explanation=explanation,
        )

    def map_text(self, text: str, prior_store: Any = None) -> List[DalMadlulMapping]:
        """Tokenize text and map each word."""
        words = text.split()
        results: List[DalMadlulMapping] = []
        for word in words:
            stem = _simple_stem(word)
            has_reality = False
            prior_knowledge: Optional[str] = None

            if prior_store is not None:
                things = (
                    prior_store.query_things_by_name(word) or
                    prior_store.query_things_by_name(stem) or
                    prior_store.query_things_by_name(_strip_al(word))
                )
                if things:
                    has_reality = True
                    prior_knowledge = things[0].name if hasattr(things[0], "name") else str(things[0])

                if not prior_knowledge:
                    facts = prior_store.facts.find_by_claim(word) if hasattr(prior_store, "facts") else []
                    if facts:
                        prior_knowledge = word

            results.append(
                self.map(
                    dal=word,
                    madlul=stem or word,
                    has_reality=has_reality,
                    prior_knowledge=prior_knowledge,
                )
            )
        return results
