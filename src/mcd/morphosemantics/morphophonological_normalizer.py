"""MorphophonologicalNormalizer — normalizes Arabic surface forms for analysis.

Arabic text often appears with diacritics (تشكيل), hamza variants, alif
variations, and taa marbuta variations.  This normalizer strips/normalizes
these to a canonical form so that pattern matching can proceed reliably.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass
class NormalizationResult:
    original: str
    normalized: str
    stripped_diacritics: str
    canonical_hamza: str
    canonical_alif: str
    operations_applied: list[str]

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "normalized": self.normalized,
            "stripped_diacritics": self.stripped_diacritics,
            "canonical_hamza": self.canonical_hamza,
            "canonical_alif": self.canonical_alif,
            "operations_applied": self.operations_applied,
        }


# Arabic diacritic code points (harakat + tanwin + shadda + sukun)
_DIACRITICS = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670')

# Alif variants → canonical alif
_ALIF_MAP = {
    '\u0622': '\u0627',  # أ with madda → ا
    '\u0623': '\u0627',  # أ → ا
    '\u0625': '\u0627',  # إ → ا
    '\u0671': '\u0627',  # ٱ → ا
}

# Hamza variants → canonical hamza ء
_HAMZA_MAP = {
    '\u0624': '\u0648',  # ؤ → و
    '\u0626': '\u064a',  # ئ → ي
}


def _strip_diacritics(text: str) -> str:
    return ''.join(c for c in text if c not in _DIACRITICS)


def _canonicalize_alif(text: str) -> str:
    return ''.join(_ALIF_MAP.get(c, c) for c in text)


def _canonicalize_hamza(text: str) -> str:
    return ''.join(_HAMZA_MAP.get(c, c) for c in text)


class MorphophonologicalNormalizer:
    """Normalizes Arabic surface forms for morphological pattern matching."""

    def normalize(self, word: str) -> NormalizationResult:
        ops: list[str] = []

        nfc = unicodedata.normalize("NFC", word)
        if nfc != word:
            ops.append("nfc_normalization")

        stripped = _strip_diacritics(nfc)
        if stripped != nfc:
            ops.append("strip_diacritics")

        alif_norm = _canonicalize_alif(stripped)
        if alif_norm != stripped:
            ops.append("canonicalize_alif")

        hamza_norm = _canonicalize_hamza(alif_norm)
        if hamza_norm != alif_norm:
            ops.append("canonicalize_hamza")

        return NormalizationResult(
            original=word,
            normalized=hamza_norm,
            stripped_diacritics=stripped,
            canonical_hamza=hamza_norm,
            canonical_alif=alif_norm,
            operations_applied=ops,
        )

    def normalize_str(self, word: str) -> str:
        return self.normalize(word).normalized
