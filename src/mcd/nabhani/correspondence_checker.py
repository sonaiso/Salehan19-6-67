"""CorrespondenceChecker — verifies that a thought corresponds to reality.

Axiom AX-07: صحة الفكر بمطابقته للواقع
The validity of a thought is determined by its correspondence (مطابقة) to reality.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class CorrespondenceResult:
    match_score: float    # 0.0 – 1.0
    match_type: str       # one of the types listed below
    contradictions: List[str]
    missing_context: List[str]
    explanation: str


MATCH_TYPES = (
    "direct_reality_match",
    "source_match",
    "relation_match",
    "semantic_match",
    "prior_knowledge_match",
    "contradiction_detected",
    "insufficient_data",
)


class CorrespondenceChecker:
    """Check how well a claim text corresponds to reality or prior knowledge."""

    def check(
        self,
        claim_text: str,
        reality: Optional[str] = None,
        prior_store: Any = None,
        relations: Optional[List[Any]] = None,
    ) -> CorrespondenceResult:
        contradictions: List[str] = []
        missing_context: List[str] = []
        score = 0.0
        match_type = "insufficient_data"

        words = set(claim_text.split())

        # --- Direct reality match ---
        if reality:
            reality_words = set(reality.split())
            overlap = words & reality_words
            if len(overlap) >= 1:
                score = max(score, 0.70 + 0.05 * min(len(overlap), 5))
                match_type = "direct_reality_match"
            else:
                missing_context.append("no_overlap_with_reality")

        # --- Relation match ---
        if relations:
            rel_words: set[str] = set()
            for r in relations:
                if hasattr(r, "source"):
                    rel_words.add(r.source)
                if hasattr(r, "target"):
                    rel_words.add(r.target)
                elif isinstance(r, dict):
                    rel_words.update({r.get("source", ""), r.get("target", "")})
            if rel_words & words:
                score = max(score, 0.65)
                if match_type == "insufficient_data":
                    match_type = "relation_match"

        # --- Prior knowledge match ---
        if prior_store is not None:
            found = False
            for word in words:
                things = prior_store.query_things_by_name(word) or prior_store.query_things_by_name(_strip_al(word))
                if things:
                    score = max(score, 0.75)
                    if match_type == "insufficient_data":
                        match_type = "prior_knowledge_match"
                    found = True
                    break
            if not found:
                missing_context.append("no_prior_knowledge_found")

        # --- Contradiction detection (very basic) ---
        neg_words = {"لا", "ليس", "لم", "لن", "غير", "ما"}
        if neg_words & words and score > 0.50:
            # Possible negation of something we thought matched
            contradictions.append("negation_detected_in_claim")

        if not reality and not relations and prior_store is None:
            missing_context.append("no_reality_or_store_provided")

        # Clamp
        score = round(min(1.0, max(0.0, score)), 4)

        if score == 0.0:
            match_type = "insufficient_data"
        elif contradictions:
            match_type = "contradiction_detected"

        explanation = (
            f"درجة المطابقة: {score:.2f} | نوع: {match_type}"
        )
        if missing_context:
            explanation += f" | سياق ناقص: {', '.join(missing_context)}"
        if contradictions:
            explanation += f" | تعارضات: {', '.join(contradictions)}"

        return CorrespondenceResult(
            match_score=score,
            match_type=match_type,
            contradictions=contradictions,
            missing_context=missing_context,
            explanation=explanation,
        )


def _strip_al(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word
