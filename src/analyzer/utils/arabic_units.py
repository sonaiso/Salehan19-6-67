"""Letter + haraka units (NFC) for wazn matching."""

from __future__ import annotations

import unicodedata

HARAKAT = frozenset(
    {
        "َ",  # FATHA
        "ُ",  # DAMMA
        "ِ",  # KASRA
        "ْ",  # SUKUN
        "ّ",  # SHADDA
        "ً",  # TANWIN FATH
        "ٌ",  # TANWIN DAMM
        "ٍ",  # TANWIN KASR
    }
)

# Template radicals in Arabic morphological teaching (فعل)
PLACEHOLDERS = frozenset({"ف", "ع", "ل"})


def split_units(text: str) -> list[tuple[str, tuple[str, ...]]]:
    """Split NFC Arabic into (base_letter, tuple_of_diacritics_in_order)."""
    units: list[tuple[str, tuple[str, ...]]] = []
    current_letter: str | None = None
    current_marks: list[str] = []

    for ch in unicodedata.normalize("NFC", text):
        if unicodedata.category(ch).startswith("L"):
            if current_letter is not None:
                units.append((current_letter, tuple(current_marks)))
            current_letter = ch
            current_marks = []
        elif ch in HARAKAT:
            current_marks.append(ch)

    if current_letter is not None:
        units.append((current_letter, tuple(current_marks)))

    return units
