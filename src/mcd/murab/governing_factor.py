"""GoverningFactor — what forces a particular I'rab case on a word."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GoverningFactor:
    factor_id: str
    surface: str
    factor_type: str  # verb|preposition|particle|nasikh|jazim|nasib|idafa|
                      # dependency|semantic_governor
    governs_case: list[str] = field(default_factory=list)
    scope: str = "next_token"  # next_token|clause|sentence
    certainty: float = 1.0

    def to_dict(self) -> dict:
        return {
            "factor_id": self.factor_id,
            "surface": self.surface,
            "factor_type": self.factor_type,
            "governs_case": self.governs_case,
            "scope": self.scope,
            "certainty": self.certainty,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GoverningFactor":
        return cls(
            factor_id=d["factor_id"],
            surface=d["surface"],
            factor_type=d["factor_type"],
            governs_case=d.get("governs_case", []),
            scope=d.get("scope", "next_token"),
            certainty=d.get("certainty", 1.0),
        )


# Harakat-free surface → governing factor mappings
_HARDCODED: list[dict] = [
    # حروف الجر
    {"factor_id": "gf_bi", "surface": "ب", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_fi", "surface": "في", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_ila", "surface": "إلى", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_ala", "surface": "على", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_min", "surface": "من", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_li", "surface": "ل", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_an", "surface": "عن", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_hatta", "surface": "حتى", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_ka", "surface": "ك", "factor_type": "preposition",
     "governs_case": ["genitive"], "scope": "next_token", "certainty": 1.0},
    # النواسخ (إنّ وأخواتها) → تنصب الاسم وترفع الخبر
    {"factor_id": "gf_inna", "surface": "إنّ", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_anna", "surface": "أنّ", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_laakinna", "surface": "لكنّ", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_kaanna", "surface": "كأنّ", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_layta", "surface": "ليت", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_laalla", "surface": "لعلّ", "factor_type": "nasikh",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    # كان وأخواتها → ترفع الاسم وتنصب الخبر
    {"factor_id": "gf_kana", "surface": "كان", "factor_type": "nasikh",
     "governs_case": ["nominative", "accusative"], "scope": "clause", "certainty": 1.0},
    {"factor_id": "gf_laysa", "surface": "ليس", "factor_type": "nasikh",
     "governs_case": ["nominative", "accusative"], "scope": "clause", "certainty": 1.0},
    # أدوات الجزم
    {"factor_id": "gf_lam", "surface": "لم", "factor_type": "jazim",
     "governs_case": ["jussive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_lamma", "surface": "لمّا", "factor_type": "jazim",
     "governs_case": ["jussive"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_la_nahiy", "surface": "لا", "factor_type": "jazim",
     "governs_case": ["jussive"], "scope": "next_token", "certainty": 0.7},
    # أدوات النصب (مضارع)
    {"factor_id": "gf_lan", "surface": "لن", "factor_type": "nasib",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    {"factor_id": "gf_an_nasib", "surface": "أن", "factor_type": "nasib",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 0.8},
    {"factor_id": "gf_kay", "surface": "كي", "factor_type": "nasib",
     "governs_case": ["accusative"], "scope": "next_token", "certainty": 1.0},
    # الفعل الماضي → يرفع الفاعل وينصب المفعول
    {"factor_id": "gf_past_verb", "surface": "__past_verb__", "factor_type": "verb",
     "governs_case": ["nominative", "accusative"], "scope": "clause", "certainty": 1.0},
]


class GoverningFactorRegistry:
    def __init__(self) -> None:
        self._by_id: dict[str, GoverningFactor] = {}
        self._by_surface: dict[str, GoverningFactor] = {}
        for entry in _HARDCODED:
            gf = GoverningFactor.from_dict(entry)
            self._by_id[gf.factor_id] = gf
            self._by_surface[gf.surface] = gf

    def get(self, factor_id: str) -> Optional[GoverningFactor]:
        return self._by_id.get(factor_id)

    def get_by_surface(self, surface: str) -> Optional[GoverningFactor]:
        return self._by_surface.get(surface)

    def all(self) -> list[GoverningFactor]:
        return list(self._by_id.values())

    def prepositions(self) -> list[GoverningFactor]:
        return [gf for gf in self._by_id.values() if gf.factor_type == "preposition"]


GOVERNING_FACTOR_REGISTRY = GoverningFactorRegistry()
