"""ZarfEngine — handles Arabic ظرف (adverb of time and place)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ZarfType(str, Enum):
    ZAMAN = "zaman"      # زمان (time)
    MAKAN = "makan"      # مكان (place)
    SHIBH_JUMLA = "shibh_jumla"  # شبه جملة


@dataclass
class ZarfRelation:
    surface: str
    zarf_type: ZarfType
    edge_type: str  # time_of|place_of
    token_id: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "zarf_type": self.zarf_type.value,
            "edge_type": self.edge_type,
            "token_id": self.token_id,
            "certainty": self.certainty,
        }


TIME_WORDS = {"يومَ", "ليلةَ", "صباحاً", "مساءً", "أمسَ", "اليومَ", "غداً", "الآنَ", "حيناً",
              "وقتَ", "زمانَ", "ساعةَ", "شهرَ", "عامَ", "سنةَ", "منذُ", "قبلَ", "بعدَ"}

PLACE_WORDS = {"فوقَ", "تحتَ", "أمامَ", "خلفَ", "يمينَ", "يسارَ", "بينَ", "عندَ", "لدى",
               "جانبَ", "حولَ", "وسطَ", "وراءَ", "قبالةَ", "تجاهَ", "إزاءَ"}


class ZarfEngine:
    """Handles Arabic ظرف (adverbs of time and place)."""

    def detect_zarf(self, tokens: list) -> list:
        """Detect zarf relations from token list."""
        relations = []

        for i, tok in enumerate(tokens):
            stripped = self._strip_diacritics(tok)

            if tok in TIME_WORDS or stripped in {self._strip_diacritics(w) for w in TIME_WORDS}:
                relations.append(ZarfRelation(
                    surface=tok,
                    zarf_type=ZarfType.ZAMAN,
                    edge_type="time_of",
                    token_id=f"tok_{i}",
                    certainty=0.85,
                ))
            elif tok in PLACE_WORDS or stripped in {self._strip_diacritics(w) for w in PLACE_WORDS}:
                relations.append(ZarfRelation(
                    surface=tok,
                    zarf_type=ZarfType.MAKAN,
                    edge_type="place_of",
                    token_id=f"tok_{i}",
                    certainty=0.85,
                ))

        return relations

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
