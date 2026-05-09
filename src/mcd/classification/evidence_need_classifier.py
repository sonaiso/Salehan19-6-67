"""EvidenceNeedClassifier — determines what kind of evidence a prompt requires."""
from __future__ import annotations

from mcd.classification.taxonomy import EvidenceNeed, JudgmentType, KnowledgeCategory

# ---------------------------------------------------------------------------
# Evidence rules by knowledge category and judgment type
# ---------------------------------------------------------------------------

# (knowledge_category → required evidence types)
_CATEGORY_EVIDENCE: dict[str, list[tuple[str, float]]] = {
    KnowledgeCategory.SCIENCE: [
        (EvidenceNeed.SENSORY, 0.80),
        (EvidenceNeed.EXPERIMENTAL, 0.75),
    ],
    KnowledgeCategory.LANGUAGE: [
        (EvidenceNeed.LINGUISTIC, 0.85),
        (EvidenceNeed.CONTEXTUAL, 0.70),
    ],
    KnowledgeCategory.METHOD: [
        (EvidenceNeed.TEXTUAL, 0.70),
        (EvidenceNeed.CONTEXTUAL, 0.65),
    ],
    KnowledgeCategory.CULTURE: [
        (EvidenceNeed.CONTEXTUAL, 0.65),
        (EvidenceNeed.TEXTUAL, 0.55),
        (EvidenceNeed.HISTORICAL, 0.50),
    ],
    KnowledgeCategory.CIVILIZATION: [
        (EvidenceNeed.HISTORICAL, 0.75),
        (EvidenceNeed.TEXTUAL, 0.65),
    ],
    KnowledgeCategory.TECHNOLOGY: [
        (EvidenceNeed.TECHNICAL, 0.85),
        (EvidenceNeed.TEXTUAL, 0.60),
    ],
}

# (judgment_type → required evidence types)
_JUDGMENT_EVIDENCE: dict[str, list[tuple[str, float]]] = {
    JudgmentType.SHARI: [
        (EvidenceNeed.SHARI, 1.0),
        (EvidenceNeed.TEXTUAL, 0.90),
    ],
    JudgmentType.TECHNICAL: [
        (EvidenceNeed.TECHNICAL, 0.85),
        (EvidenceNeed.TEXTUAL, 0.55),
    ],
    JudgmentType.PRACTICAL: [
        (EvidenceNeed.TEXTUAL, 0.60),
        (EvidenceNeed.CONTEXTUAL, 0.55),
    ],
    JudgmentType.VALUE: [
        (EvidenceNeed.CONTEXTUAL, 0.65),
        (EvidenceNeed.HISTORICAL, 0.55),
        (EvidenceNeed.TEXTUAL, 0.50),
    ],
    JudgmentType.EPISTEMIC: [
        (EvidenceNeed.SENSORY, 0.50),
        (EvidenceNeed.EXPERIMENTAL, 0.50),
        (EvidenceNeed.CONTEXTUAL, 0.50),
    ],
}


class EvidenceNeedClassifier:
    """Determine the evidence types needed to answer a prompt."""

    def classify(
        self,
        judgment_types: dict[str, float],
        knowledge_categories: dict[str, float],
        concept_evidence_hints: dict[str, float] | None = None,
    ) -> dict[str, float]:
        """Return EvidenceNeed → score dict (multi-label, additive)."""
        scores: dict[str, float] = {}

        # From knowledge categories
        for cat, cat_score in knowledge_categories.items():
            for evidence_type, base_score in _CATEGORY_EVIDENCE.get(cat, []):
                combined = round(cat_score * base_score, 4)
                scores[evidence_type] = max(scores.get(evidence_type, 0.0), combined)

        # From judgment types
        for jt, jt_score in judgment_types.items():
            for evidence_type, base_score in _JUDGMENT_EVIDENCE.get(jt, []):
                combined = round(jt_score * base_score, 4)
                scores[evidence_type] = max(scores.get(evidence_type, 0.0), combined)

        # From concept-level hints (direct lexicon hits)
        if concept_evidence_hints:
            for evidence_type, hint_score in concept_evidence_hints.items():
                scores[evidence_type] = max(scores.get(evidence_type, 0.0), hint_score)

        # Ensure at least one entry
        if not scores:
            scores[EvidenceNeed.CONTEXTUAL] = 0.40

        return {k: round(v, 4) for k, v in scores.items() if v > 0.0}
