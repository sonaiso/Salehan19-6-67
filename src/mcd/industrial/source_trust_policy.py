"""Source Trust Policy — evaluates quality of source documents."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.industrial.api_contract import SourceAPIResponse, SourceDocument


@dataclass
class SourceTrustResult:
    source_id: str
    trust_score: float
    authority_score: float
    freshness_score: float
    relevance_score: float
    injection_risk: float
    final_trust: float
    warnings: list[str] = field(default_factory=list)


class SourceTrustPolicy:
    AUTHORITY_SCORES: dict[str, float] = {
        "official": 1.0,
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2,
    }
    FRESHNESS_SCORES: dict[str, float] = {
        "current": 1.0,
        "acceptable": 0.7,
        "stale": 0.3,
        "unknown": 0.4,
    }
    INJECTION_PHRASES = ["تجاهل تعليمات", "ignore system", "override instructions"]

    def evaluate(self, doc: SourceDocument, query_text: str = "") -> SourceTrustResult:
        authority_score = self.AUTHORITY_SCORES.get(doc.authority_level, 0.5)
        freshness_score = self.FRESHNESS_SCORES.get(doc.freshness, 0.4)

        # Simple relevance: non-zero if doc has content and query is not empty
        if query_text and doc.content:
            relevance_score = 0.6
        elif doc.content:
            relevance_score = 0.5
        else:
            relevance_score = 0.1

        # Injection risk
        injection_risk = 0.0
        warnings: list[str] = []
        content_lower = doc.content.lower()
        for phrase in self.INJECTION_PHRASES:
            if phrase in doc.content or phrase.lower() in content_lower:
                injection_risk = 0.95
                warnings.append("injection_phrase_detected")
                break

        trust_score = (authority_score + freshness_score + relevance_score) / 3.0

        if doc.authority_level == "low":
            warnings.append("low_authority_source")
        if doc.freshness == "stale":
            warnings.append("stale_document")

        final_trust = trust_score * (1.0 - injection_risk * 0.9)

        return SourceTrustResult(
            source_id=doc.source_id,
            trust_score=trust_score,
            authority_score=authority_score,
            freshness_score=freshness_score,
            relevance_score=relevance_score,
            injection_risk=injection_risk,
            final_trust=final_trust,
            warnings=warnings,
        )

    def evaluate_response(
        self, response: SourceAPIResponse, query_text: str = ""
    ) -> list[SourceTrustResult]:
        return [self.evaluate(doc, query_text) for doc in response.documents]

    def overall_trust(self, results: list[SourceTrustResult]) -> float:
        """Return mean final_trust or 0.0 if empty."""
        if not results:
            return 0.0
        return sum(r.final_trust for r in results) / len(results)
