"""Source Trust Policy — evaluates quality of source documents."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from mcd.industrial.api_contract import SourceAPIResponse, SourceDocument

# Pre-compiled pattern for Arabic and ASCII token extraction
_TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[a-zA-Z]+")


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

    _STOPWORDS: frozenset[str] = frozenset({
        "في", "من", "على", "إلى", "عن", "ما", "هل", "هو", "هي", "و", "أو",
        "the", "a", "an", "is", "in", "of", "to", "for", "and", "or", "with",
    })

    def _tokenize(self, text: str) -> set[str]:
        """Extract meaningful Arabic/ASCII tokens, removing stopwords."""
        tokens = _TOKEN_RE.findall(text.lower())
        return {t for t in tokens if t not in self._STOPWORDS and len(t) > 1}

    def _compute_relevance(self, query_text: str, doc_content: str) -> float:
        """Compute relevance score using lexical overlap."""
        if not query_text or not doc_content:
            return 0.1 if doc_content else 0.0

        query_tokens = self._tokenize(query_text)
        doc_tokens = self._tokenize(doc_content)
        if not query_tokens:
            return 0.3
        overlap = len(query_tokens & doc_tokens)
        score = overlap / max(1, len(query_tokens))
        if score == 0.0:
            score = 0.3  # base: content present but no lexical overlap
        if query_text.lower()[:20] in doc_content.lower():
            score = min(1.0, score + 0.2)
        return min(1.0, max(0.0, score))

    def evaluate(self, doc: SourceDocument, query_text: str = "") -> SourceTrustResult:
        authority_score = self.AUTHORITY_SCORES.get(doc.authority_level, 0.5)
        freshness_score = self.FRESHNESS_SCORES.get(doc.freshness, 0.4)

        relevance_score = self._compute_relevance(query_text, doc.content)

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
