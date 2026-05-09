"""Feature vector dataclass for Unicode characters."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FeatureVector:
    unicode_code: int
    is_arabic: bool
    is_letter: bool
    is_diacritic: bool
    is_space: bool
    is_punctuation: bool
    root_candidate_score: float = 0.0
    affix_candidate_score: float = 0.0
    weak_letter_score: float = 0.0
    diacritic_role: str = ""
    connects_right: bool = False
    connects_left: bool = False

    def to_dict(self) -> dict:
        return {
            "unicode_code": self.unicode_code,
            "is_arabic": self.is_arabic,
            "is_letter": self.is_letter,
            "is_diacritic": self.is_diacritic,
            "is_space": self.is_space,
            "is_punctuation": self.is_punctuation,
            "root_candidate_score": self.root_candidate_score,
            "affix_candidate_score": self.affix_candidate_score,
            "weak_letter_score": self.weak_letter_score,
            "diacritic_role": self.diacritic_role,
            "connects_right": self.connects_right,
            "connects_left": self.connects_left,
        }
