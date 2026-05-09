"""LexicalGroundingEngine — grounds Arabic lexemes against the knowledge store."""
from __future__ import annotations

import uuid
from typing import Optional

from mcd.grounding.grounded_frame import GroundedLexeme, GroundingStatus
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data


# Words that are inherently ambiguous without context
_AMBIGUOUS_WORDS = {"علم", "عين", "جمال"}

# Words requiring revelation evidence for grounding
_SHARI_TERMS = {"حرام", "واجب", "مندوب", "مكروه", "مباح", "محرم", "فرض", "سنة"}


def _strip_article(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word


class LexicalGroundingEngine:
    """Grounds individual Arabic lexemes using the PriorKnowledgeStore."""

    def __init__(self, store: Optional[PriorKnowledgeStore] = None) -> None:
        if store is None:
            store = PriorKnowledgeStore()
            load_seed_data(store)
        self._store = store

    def ground(self, surface: str, context: str = "") -> GroundedLexeme:
        normalized = _strip_article(surface.strip())
        lexeme_id = str(uuid.uuid4())[:8]
        notes = ""
        warnings: list[str] = []

        # Check shari terms first — always partially grounded without revelation evidence
        if normalized in _SHARI_TERMS or surface in _SHARI_TERMS:
            return GroundedLexeme(
                lexeme_id=lexeme_id,
                surface=surface,
                normalized=normalized,
                dal=normalized,
                madlul=f"حكم شرعي: {normalized}",
                grounding_status=GroundingStatus.PARTIALLY_GROUNDED,
                prior_knowledge_refs=[],
                certainty=0.3,
                notes="يحتاج دليلاً شرعياً (نص وحي) للتحقق الكامل",
            )

        # Check ambiguous words
        if normalized in _AMBIGUOUS_WORDS or surface in _AMBIGUOUS_WORDS:
            # Try to ground from store, but mark as partially grounded
            things = self._store.query_things_by_name(normalized) or self._store.query_things_by_name(surface)
            if things:
                t = things[0]
                return GroundedLexeme(
                    lexeme_id=lexeme_id,
                    surface=surface,
                    normalized=normalized,
                    dal=normalized,
                    madlul=t.haqiqa,
                    grounding_status=GroundingStatus.PARTIALLY_GROUNDED,
                    reality_ref=t.thing_id,
                    prior_knowledge_refs=[t.thing_id],
                    certainty=float(t.certainty.score) * 0.7,
                    notes="لفظ مشترك — يحتاج سياقاً للتحقق requires_context",
                )
            return GroundedLexeme(
                lexeme_id=lexeme_id,
                surface=surface,
                normalized=normalized,
                dal=normalized,
                grounding_status=GroundingStatus.PARTIALLY_GROUNDED,
                certainty=0.2,
                notes="لفظ مشترك — يحتاج سياقاً requires_context",
            )

        # Try to find in ThingStore by name
        things = (
            self._store.query_things_by_name(normalized)
            or self._store.query_things_by_name(surface)
        )
        if things:
            t = things[0]
            return GroundedLexeme(
                lexeme_id=lexeme_id,
                surface=surface,
                normalized=normalized,
                dal=normalized,
                madlul=t.haqiqa,
                grounding_status=GroundingStatus.GROUNDED,
                reality_ref=t.thing_id,
                prior_knowledge_refs=[t.thing_id],
                evidence_refs=[ev.source_id for ev in t.evidence],
                certainty=float(t.certainty.score),
                notes="",
            )

        # Try properties
        for prop in self._store.properties.all():
            if normalized in prop.names.values() or surface in prop.names.values():
                return GroundedLexeme(
                    lexeme_id=lexeme_id,
                    surface=surface,
                    normalized=normalized,
                    dal=normalized,
                    madlul=prop.names.get("ar", normalized),
                    grounding_status=GroundingStatus.GROUNDED,
                    prior_knowledge_refs=[prop.property_id],
                    evidence_refs=[ev.source_id for ev in prop.evidence],
                    certainty=float(prop.certainty.score),
                    notes="",
                )

        # Try relations
        for rel in self._store.relations.values():
            if normalized == rel.relation_type or surface == rel.relation_type:
                return GroundedLexeme(
                    lexeme_id=lexeme_id,
                    surface=surface,
                    normalized=normalized,
                    dal=normalized,
                    grounding_status=GroundingStatus.GROUNDED,
                    prior_knowledge_refs=[rel.relation_id],
                    certainty=float(rel.certainty),
                    notes="",
                )

        # Linguistic meaning only → partially grounded
        if len(normalized) >= 2:
            return GroundedLexeme(
                lexeme_id=lexeme_id,
                surface=surface,
                normalized=normalized,
                dal=normalized,
                grounding_status=GroundingStatus.PARTIALLY_GROUNDED,
                certainty=0.2,
                notes="معنى لغوي فقط — لا إحالة واقعية موثقة",
            )

        # Nothing found
        return GroundedLexeme(
            lexeme_id=lexeme_id,
            surface=surface,
            normalized=normalized,
            dal=normalized,
            grounding_status=GroundingStatus.UNGROUNDED,
            certainty=0.0,
            notes="لم يُعثر على أي إحالة",
        )
