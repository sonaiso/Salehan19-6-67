"""CertaintyScorer: multi-dimensional certainty scoring."""
from __future__ import annotations

from dataclasses import dataclass
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty, CERTAINTY_LEVELS
from mcd.core.measures import clamp

DIMENSION_WEIGHTS = {
    "reality_match":          0.20,
    "evidence_strength":      0.20,
    "semantic_fit":           0.15,
    "relation_validity":      0.15,
    "prior_relevance":        0.15,
    "context_fit":            0.10,
    "ambiguity_penalty":      0.05,
    "contradiction_penalty":  0.05,
}


def _level_from_score(score: float) -> str:
    for level, (lo, hi) in CERTAINTY_LEVELS.items():
        if lo <= score < hi:
            return level
    return "near_certainty"


@dataclass
class CertaintyScoreResult:
    score: float
    level: str
    dimensions: dict[str, float]
    explanation: str


class CertaintyScorer:

    def score(
        self,
        reality_match: float = 0.5,
        evidence_strength: float = 0.0,
        semantic_fit: float = 0.5,
        relation_validity: float = 0.5,
        prior_relevance: float = 0.5,
        context_fit: float = 0.5,
        ambiguity_penalty: float = 0.0,
        contradiction_penalty: float = 0.0,
    ) -> CertaintyScoreResult:
        dims = {
            "reality_match": reality_match,
            "evidence_strength": evidence_strength,
            "semantic_fit": semantic_fit,
            "relation_validity": relation_validity,
            "prior_relevance": prior_relevance,
            "context_fit": context_fit,
            "ambiguity_penalty": ambiguity_penalty,
            "contradiction_penalty": contradiction_penalty,
        }
        raw = (
            reality_match         * DIMENSION_WEIGHTS["reality_match"]
            + evidence_strength   * DIMENSION_WEIGHTS["evidence_strength"]
            + semantic_fit        * DIMENSION_WEIGHTS["semantic_fit"]
            + relation_validity   * DIMENSION_WEIGHTS["relation_validity"]
            + prior_relevance     * DIMENSION_WEIGHTS["prior_relevance"]
            + context_fit         * DIMENSION_WEIGHTS["context_fit"]
            - ambiguity_penalty   * DIMENSION_WEIGHTS["ambiguity_penalty"]
            - contradiction_penalty * DIMENSION_WEIGHTS["contradiction_penalty"]
        )
        final = clamp(raw)
        level = _level_from_score(final)
        explanation = f"score={final:.3f} level={level}"
        return CertaintyScoreResult(score=final, level=level, dimensions=dims, explanation=explanation)

    def score_from_evidence(self, evidence: list[Evidence], context: str = "") -> CertaintyScoreResult:
        if not evidence:
            return self.score(evidence_strength=0.0)
        avg_strength = sum(e.strength * e.reliability for e in evidence) / len(evidence)
        return self.score(
            evidence_strength=avg_strength,
            context_fit=0.5,
            reality_match=avg_strength,
        )
