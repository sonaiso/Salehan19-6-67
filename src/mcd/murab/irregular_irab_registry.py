"""IrregularIrabRegistry — I'rab markers for non-standard Arabic word patterns."""
from __future__ import annotations

import re

_HARAKAT = re.compile(r"[\u064b-\u065f]")

# أسماء الخمسة (the five nouns) bare forms
_FIVE_NOUNS = {"أب", "أخ", "حم", "فو", "ذو"}

# Known ممنوع من الصرف patterns (partial — proper nouns, broken plurals on fatha)
_MAMNOO_ROOTS = {"أحمد", "إبراهيم", "مساجد", "مدارس", "أفضل", "أحسن"}


class IrregularIrabRegistry:
    """Registry for irregular I'rab patterns in Arabic grammar.

    Covers:
        - أسماء خمسة  (five nouns): use waw/alif/ya instead of damma/fatha/kasra
        - مثنى (dual): use alif for nominative, ya for genitive/accusative
        - جمع مذكر سالم (SMP): use waw for nominative, ya for gen/acc
        - جمع مؤنث سالم (SFP): use damma for nom, kasra for gen/acc
        - ممنوع من الصرف (diptote): fatha instead of kasra in genitive
        - أفعال خمسة (five verbs): nun for indicative, deleted-nun for subj/jussive
        - معتل الآخر (weak-final verbs): deletion of weak letter
    """

    _FIVE_NOUN_MARKERS = {
        "nominative": "waw",
        "accusative": "alif",
        "genitive":   "ya",
    }

    _DUAL_MARKERS = {
        "nominative": "alif",
        "accusative": "ya",
        "genitive":   "ya",
    }

    _SMP_MARKERS = {   # جمع مذكر سالم
        "nominative": "waw",
        "accusative": "ya",
        "genitive":   "ya",
    }

    _SFP_MARKERS = {   # جمع مؤنث سالم
        "nominative": "damma",
        "accusative": "kasra",
        "genitive":   "kasra",
    }

    _DIPTOTE_MARKERS = {   # ممنوع من الصرف
        "nominative": "damma",
        "accusative": "fatha",
        "genitive":   "fatha",  # no tanwin, fatha replaces kasra
    }

    _FIVE_VERBS_MARKERS = {
        "nominative": "nun",
        "accusative": "deleted_nun",
        "jussive":    "deleted_nun",
    }

    def get_marker_for_case(self, word_type: str, irab_case: str) -> str:
        table = self._get_table(word_type)
        return table.get(irab_case, "damma")

    def _get_table(self, word_type: str) -> dict:
        return {
            "five_nouns":       self._FIVE_NOUN_MARKERS,
            "dual":             self._DUAL_MARKERS,
            "sound_plural":     self._SMP_MARKERS,
            "broken_plural":    self._SFP_MARKERS,
            "diptote":          self._DIPTOTE_MARKERS,
            "five_verbs":       self._FIVE_VERBS_MARKERS,
        }.get(word_type, {})

    def is_irregular(self, surface: str) -> bool:
        bare = _HARAKAT.sub("", surface)
        # Strip al-
        if bare.startswith("ال"):
            bare = bare[2:]
        if bare in _FIVE_NOUNS:
            return True
        if bare in _MAMNOO_ROOTS:
            return True
        # Dual ending
        if bare.endswith("ان") or bare.endswith("ين"):
            return True
        # Sound masculine plural
        if bare.endswith("ون") or bare.endswith("ين"):
            return True
        # Sound feminine plural
        if bare.endswith("ات"):
            return True
        return False


IRREGULAR_IRAB_REGISTRY = IrregularIrabRegistry()
