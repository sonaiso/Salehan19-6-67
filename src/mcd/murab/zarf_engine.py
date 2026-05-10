"""ZarfEngine — classifies ظرف (adverbial) constructions."""
from __future__ import annotations

import re

_HARAKAT = re.compile(r"[\u064b-\u065f]")

_ZAMAN_WORDS = {"يوم", "أمس", "غد", "الآن", "قبل", "بعد", "حين", "وقت",
                "ساعة", "ليلة", "صباح", "مساء", "شهر", "سنة", "عام"}
_MAKAN_WORDS = {"أمام", "خلف", "فوق", "تحت", "يمين", "يسار", "بين", "عند",
                "لدى", "مع", "جانب", "وسط", "حول", "داخل", "خارج"}


class ZarfEngine:
    """Classifies adverbial (ظرف) tokens."""

    def resolve(
        self,
        surface: str,
        context: list[str],
    ) -> dict:
        bare = _HARAKAT.sub("", surface)
        warnings: list[str] = []

        if bare in _ZAMAN_WORDS:
            return {
                "zarf_type": "zaman",
                "relation_type": "advmod:tmod",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        if bare in _MAKAN_WORDS:
            return {
                "zarf_type": "makan",
                "relation_type": "advmod:lmod",
                "certainty_policy": "certain_syntactic",
                "warnings": warnings,
            }

        # شبه جملة (prepositional phrase acting as adverbial)
        context_bare = [_HARAKAT.sub("", t) for t in context]
        if context_bare and context_bare[-1] in {"في", "على", "من", "إلى", "عند"}:
            return {
                "zarf_type": "shibh_jumla",
                "relation_type": "advmod:pp",
                "certainty_policy": "probable_syntactic",
                "warnings": warnings,
            }

        warnings.append("zarf_type_undetermined_context_needed")
        return {
            "zarf_type": "majazi",
            "relation_type": "advmod",
            "certainty_policy": "hypothesis",
            "warnings": warnings,
        }
