"""IrregularIrabRegistry — handles Arabic irregular I'rab patterns."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class IrregularIrabEntry:
    word: str
    irregular_type: str  # five_nouns|dual|sound_masculine_plural|sound_feminine_plural|diptote|five_verbs
    nominative_marker: str
    accusative_marker: str
    genitive_marker: str
    notes: str

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "irregular_type": self.irregular_type,
            "nominative_marker": self.nominative_marker,
            "accusative_marker": self.accusative_marker,
            "genitive_marker": self.genitive_marker,
            "notes": self.notes,
        }


# الأسماء الخمسة (Five Nouns)
FIVE_NOUNS = {
    "أب": IrregularIrabEntry("أب", "five_nouns", "waw", "alif", "ya", "أب أخ حم فم ذو"),
    "أخ": IrregularIrabEntry("أخ", "five_nouns", "waw", "alif", "ya", ""),
    "حم": IrregularIrabEntry("حم", "five_nouns", "waw", "alif", "ya", ""),
    "فم": IrregularIrabEntry("فم", "five_nouns", "waw", "alif", "ya", ""),
    "ذو": IrregularIrabEntry("ذو", "five_nouns", "waw", "alif", "ya", ""),
}

# جمع المذكر السالم patterns
SOUND_MASCULINE_ENDINGS = {"ون", "ين"}

# جمع المؤنث السالم patterns
SOUND_FEMININE_ENDINGS = {"ات"}

# الممنوع من الصرف - diptotes (no tanwin, genitive marked by fatha not kasra)
DIPTOTE_PATTERNS = {
    "patterns": ["أفعل", "مفاعل", "فعالى", "فعلاء", "أفعلاء"],
    "proper_nouns_foreign": True,
}


class IrregularIrabRegistry:
    """Registry for irregular Arabic I'rab patterns."""

    def get_five_noun(self, word: str) -> Optional[IrregularIrabEntry]:
        """Get irregular entry for أسماء خمسة."""
        return FIVE_NOUNS.get(word)

    def is_dual(self, word: str) -> bool:
        """Check if word is dual form."""
        stripped = self._strip_diacritics(word)
        return stripped.endswith('ان') or stripped.endswith('ين')

    def is_sound_masculine_plural(self, word: str) -> bool:
        """Check if word is sound masculine plural."""
        stripped = self._strip_diacritics(word)
        return stripped.endswith('ون') or stripped.endswith('ين')

    def is_sound_feminine_plural(self, word: str) -> bool:
        """Check if word is sound feminine plural."""
        stripped = self._strip_diacritics(word)
        return stripped.endswith('ات')

    def get_dual_markers(self, case: str) -> str:
        """Get marker for dual."""
        if case == "nominative":
            return "alif"
        return "ya"

    def get_sound_masc_plural_markers(self, case: str) -> str:
        """Get marker for sound masculine plural."""
        if case == "nominative":
            return "waw"
        return "ya"

    def get_sound_fem_plural_markers(self, case: str) -> str:
        """Get marker for sound feminine plural."""
        if case == "accusative":
            return "fatha"
        return "kasra"

    def analyze_word(self, word: str, irab_case: str) -> dict:
        """Analyze irregular I'rab for a word."""
        stripped = self._strip_diacritics(word)

        five_noun = self.get_five_noun(stripped)
        if five_noun:
            return {
                "irregular_type": "five_nouns",
                "marker": five_noun.nominative_marker if irab_case == "nominative"
                          else five_noun.accusative_marker if irab_case == "accusative"
                          else five_noun.genitive_marker,
                "notes": five_noun.notes,
            }

        if self.is_dual(word):
            return {
                "irregular_type": "dual",
                "marker": self.get_dual_markers(irab_case),
                "notes": "المثنى - ألف في الرفع وياء في النصب والجر",
            }

        if self.is_sound_masculine_plural(word):
            return {
                "irregular_type": "sound_masculine_plural",
                "marker": self.get_sound_masc_plural_markers(irab_case),
                "notes": "جمع المذكر السالم - واو في الرفع وياء في النصب والجر",
            }

        if self.is_sound_feminine_plural(word):
            return {
                "irregular_type": "sound_feminine_plural",
                "marker": self.get_sound_fem_plural_markers(irab_case),
                "notes": "جمع المؤنث السالم - ضمة في الرفع وكسرة في النصب والجر",
            }

        return {"irregular_type": "regular", "marker": None, "notes": ""}

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
