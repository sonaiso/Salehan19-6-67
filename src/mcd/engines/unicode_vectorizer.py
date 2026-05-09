"""Unicode character vectorizer for Arabic."""
from __future__ import annotations

import unicodedata
from mcd.core.symbols import (
    is_arabic_letter, is_diacritic, is_weak_letter, is_hamza,
    connects_right as _connects_right,
    connects_left as _connects_left,
    char_to_name, ARABIC_HAMZA_FORMS,
)
from mcd.core.vectors import FeatureVector

_DIACRITIC_ROLES = {
    '\u064B': 'tanwin_f',
    '\u064C': 'tanwin_d',
    '\u064D': 'tanwin_k',
    '\u064E': 'fatha',
    '\u064F': 'damma',
    '\u0650': 'kasra',
    '\u0651': 'shadda',
    '\u0652': 'sukun',
}

# Single-char affixes
_AFFIX_PARTICLES = {'و', 'ف', 'ب', 'ل', 'ك'}


class UnicodeVectorizer:

    def vectorize(self, char: str) -> FeatureVector:
        if not char:
            raise ValueError("char must be non-empty")
        c = char[0]
        arabic = is_arabic_letter(c)
        diac = is_diacritic(c)
        space = c == ' '
        punct = not arabic and not diac and not space and not c.isalnum()
        letter = arabic and not diac

        root_score = 0.0
        affix_score = 0.0
        weak_score = 0.0
        diac_role = ""

        if letter:
            if is_hamza(c):
                root_score = 0.5
            elif is_weak_letter(c):
                root_score = 0.3
                weak_score = 1.0
            else:
                root_score = 0.8
            if c in _AFFIX_PARTICLES:
                affix_score = 0.7

        if diac:
            diac_role = _DIACRITIC_ROLES.get(c, "")

        return FeatureVector(
            unicode_code=ord(c),
            is_arabic=arabic or diac,
            is_letter=letter,
            is_diacritic=diac,
            is_space=space,
            is_punctuation=punct,
            root_candidate_score=root_score,
            affix_candidate_score=affix_score,
            weak_letter_score=weak_score,
            diacritic_role=diac_role,
            connects_right=_connects_right(c),
            connects_left=_connects_left(c),
        )

    def vectorize_word(self, word: str) -> list[FeatureVector]:
        return [self.vectorize(c) for c in word]

    def vectorize_text(self, text: str) -> list[tuple[str, FeatureVector]]:
        return [(c, self.vectorize(c)) for c in text]
