"""ReasoningEngine: produce Claims from nodes and relations."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from mcd.core.nodes import KnowledgeNode
from mcd.core.relations import Relation
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty
from mcd.engines.certainty_scorer import CertaintyScorer


@dataclass
class Claim:
    claim_id: str
    text: str
    target_reality: str
    prior_information: list[str]
    relations: list[Relation]
    evidence: list[Evidence]
    certainty: Certainty
    hypotheses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "target_reality": self.target_reality,
            "prior_information": self.prior_information,
            "relations": [r.to_dict() for r in self.relations],
            "certainty": {
                "score": self.certainty.score,
                "level": self.certainty.level,
                "evidence_type": self.certainty.evidence_type,
                "explanation": self.certainty.explanation,
            },
            "hypotheses": self.hypotheses,
        }


class ReasoningEngine:

    def __init__(self, store=None) -> None:
        self._store = store
        self._scorer = CertaintyScorer()

    def reason(
        self,
        nodes: list[KnowledgeNode],
        relations: list[Relation],
        context: str = "",
    ) -> list[Claim]:
        claims: list[Claim] = []
        # Build claim for each relation
        for rel in relations:
            claim = self._build_claim_for_relation(rel, context)
            if claim is not None:
                claims.append(claim)
        # Build claim for each word node with a known thing
        if self._store:
            for node in nodes:
                if node.level == "word":
                    prior = self._find_prior_for_thing(node.surface)
                    if prior:
                        result = self._scorer.score(
                            reality_match=0.85,
                            evidence_strength=0.85,
                            semantic_fit=0.80,
                            prior_relevance=0.90,
                        )
                        claim = Claim(
                            claim_id=f"claim_{uuid.uuid4().hex[:8]}",
                            text=node.surface,
                            target_reality=node.surface,
                            prior_information=prior,
                            relations=[],
                            evidence=[],
                            certainty=Certainty.from_score(result.score, "prior_knowledge"),
                        )
                        claims.append(claim)
        claims.sort(key=lambda c: c.certainty.score, reverse=True)
        return claims

    def _build_claim_for_relation(self, relation: Relation, context: str) -> Claim | None:
        prior = []
        if self._store:
            prior = self._find_prior_for_thing(relation.source) + self._find_prior_for_thing(relation.target)

        prior_relevance = 0.80 if prior else 0.30
        reality_match = 0.80 if prior else 0.40
        evidence_strength = float(relation.certainty) if relation.certainty else 0.5

        result = self._scorer.score(
            reality_match=reality_match,
            evidence_strength=evidence_strength,
            prior_relevance=prior_relevance,
            semantic_fit=0.60,
        )
        return Claim(
            claim_id=f"claim_{uuid.uuid4().hex[:8]}",
            text=f"{relation.source} {relation.relation_type} {relation.target}",
            target_reality=relation.target,
            prior_information=prior,
            relations=[relation],
            evidence=list(relation.evidence) if relation.evidence else [],
            certainty=Certainty.from_score(result.score, "relational"),
        )

    def _find_prior_for_thing(self, name: str) -> list[str]:
        if not self._store:
            return []
        # Try direct lookup and stripped lookup
        for query in [name, name.replace('ال', '').strip(), name.replace('ة', '').strip()]:
            things = self._store.query_things_by_name(query)
            if things:
                return [f"{t.thing_id}: {t.haqiqa}" for t in things]
        facts = self._store.facts.find_by_claim(name)
        if facts:
            return [f.claim for f in facts]
        return []
