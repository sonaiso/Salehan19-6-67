"""GoverningFactor — Arabic governing particle/verb analysis."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "murab"

# Prepositions that govern genitive
PREPOSITIONS = {"في", "من", "إلى", "على", "عن", "ب", "ل", "ك", "منذ", "مذ", "حتى", "خلا", "عدا", "حاشا",
                "الباء", "اللام", "الكاف", "مع", "رب", "واو القسم", "تاء القسم"}

# Particles that govern accusative for name (اسم), nominative for predicate (خبر)
INNA_PARTICLES = {"إنّ", "إن", "أنّ", "أن", "كأنّ", "كأن", "لكنّ", "لكن", "ليت", "لعل", "لعلّ"}

# Particles that govern nominative for name (اسم), accusative for predicate (خبر)
KANA_VERBS = {"كان", "ليس", "صار", "أصبح", "أضحى", "أمسى", "أسى", "بات", "ظل", "مازال", "مادام", "مابرح"}

# Particles that govern jussive
JUSSIVE_PARTICLES = {"لم", "لما", "لا"}

# Particles that govern accusative mood (nasb)
NASB_PARTICLES = {"لن", "أن", "كي", "إذن", "حتى"}


@dataclass
class GoverningFactor:
    factor_id: str
    surface: str
    factor_type: str  # preposition|inna_particle|kana_verb|jussive_particle|nasb_particle|verb|conjunction
    governs_case: str  # nominative|accusative|genitive|jussive
    scope: str  # name|predicate|object|subject|mood
    certainty: float

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
        return cls(**d)


def load_governing_factors() -> list:
    """Load governing factors from JSON file."""
    path = _DATA_DIR / "governing_factors_ar.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [GoverningFactor.from_dict(d) for d in data]
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def detect_governing_factors(tokens: list) -> list:
    """Detect governing factors in a list of token strings."""
    factors = []
    for tok in tokens:
        stripped = _strip_diacritics(tok)
        if stripped in JUSSIVE_PARTICLES or tok in JUSSIVE_PARTICLES:
            factors.append(GoverningFactor(
                factor_id=f"jussive_{stripped}",
                surface=tok,
                factor_type="jussive_particle",
                governs_case="jussive",
                scope="mood",
                certainty=0.95,
            ))
        elif stripped in NASB_PARTICLES or tok in NASB_PARTICLES:
            factors.append(GoverningFactor(
                factor_id=f"nasb_{stripped}",
                surface=tok,
                factor_type="nasb_particle",
                governs_case="accusative",
                scope="mood",
                certainty=0.9,
            ))
        elif stripped in INNA_PARTICLES or tok in INNA_PARTICLES:
            factors.append(GoverningFactor(
                factor_id=f"inna_{stripped}",
                surface=tok,
                factor_type="inna_particle",
                governs_case="accusative",
                scope="name",
                certainty=0.9,
            ))
        elif stripped in KANA_VERBS or tok in KANA_VERBS:
            factors.append(GoverningFactor(
                factor_id=f"kana_{stripped}",
                surface=tok,
                factor_type="kana_verb",
                governs_case="accusative",
                scope="predicate",
                certainty=0.85,
            ))
        elif stripped in PREPOSITIONS or tok in PREPOSITIONS:
            factors.append(GoverningFactor(
                factor_id=f"prep_{stripped}",
                surface=tok,
                factor_type="preposition",
                governs_case="genitive",
                scope="object",
                certainty=0.95,
            ))
    return factors


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics (harakat) from text."""
    diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658\u0670')
    return ''.join(c for c in text if c not in diacritics)
