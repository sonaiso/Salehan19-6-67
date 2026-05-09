"""FractalComposer: compose lower-level nodes into higher-level nodes."""
from __future__ import annotations

import uuid
from mcd.core.nodes import KnowledgeNode
from mcd.core.relations import Relation
from mcd.core.evidence import Evidence
from mcd.core.certainty import Certainty
from mcd.core.measures import weighted_average


class FractalComposer:

    def compose(
        self,
        units: list[KnowledgeNode],
        context: str = "",
        evidence: list[Evidence] | None = None,
    ) -> KnowledgeNode:
        if not units:
            return KnowledgeNode(
                node_id=str(uuid.uuid4()),
                level="concept",
                surface="",
                certainty=Certainty.from_score(0.0),
            )
        # Determine target level
        levels = [u.level for u in units]
        if all(l == "letter" or l == "unicode" or l == "diacritic" for l in levels):
            return self.compose_word(units)
        if all(l == "word" for l in levels):
            return self.compose_phrase(units)
        return self.compose_phrase(units)

    def compose_word(self, chars: list[KnowledgeNode]) -> KnowledgeNode:
        surface = ''.join(n.surface for n in chars)
        scores = [n.certainty.score if n.certainty else 0.5 for n in chars]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        features: dict = {}
        for n in chars:
            features.update(n.features)
        return KnowledgeNode(
            node_id=f"word_{surface}_{uuid.uuid4().hex[:6]}",
            level="word",
            surface=surface,
            features=features,
            role_vector={},
            relations=[r for n in chars for r in n.relations],
            certainty=Certainty.from_score(avg_score, "linguistic"),
        )

    def compose_phrase(self, words: list[KnowledgeNode]) -> KnowledgeNode:
        surface = ' '.join(n.surface for n in words)
        scores = [n.certainty.score if n.certainty else 0.5 for n in words]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        level = "phrase" if len(words) < 4 else "sentence"
        return KnowledgeNode(
            node_id=f"{level}_{uuid.uuid4().hex[:8]}",
            level=level,
            surface=surface,
            features={"word_count": len(words)},
            relations=[r for n in words for r in n.relations],
            certainty=Certainty.from_score(avg_score, "syntactic"),
        )

    def compose_sentence(self, words: list[KnowledgeNode], relations: list[Relation]) -> KnowledgeNode:
        surface = ' '.join(n.surface for n in words)
        scores = [n.certainty.score if n.certainty else 0.5 for n in words]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        relation_ids = [r.relation_id for r in relations]
        return KnowledgeNode(
            node_id=f"sentence_{uuid.uuid4().hex[:8]}",
            level="sentence",
            surface=surface,
            features={"word_count": len(words), "relation_count": len(relations)},
            relations=relation_ids,
            certainty=Certainty.from_score(avg_score, "syntactic"),
        )
