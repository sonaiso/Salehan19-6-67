"""UnicodeTraceUnit — atomic trace for a single Unicode code point."""
from __future__ import annotations

import unicodedata
import uuid
from dataclasses import dataclass, field
from mcd.core.symbols import (
    is_arabic_letter, is_diacritic as _is_diacritic,
    is_weak_letter, is_hamza,
)
from mcd.engines.unicode_vectorizer import UnicodeVectorizer

TRACE_STATUSES = [
    "classified",
    "unknown_but_tracked",
    "ignored_for_semantics_but_tracked",
]

_VECTORIZER = UnicodeVectorizer()

_NUMERIC_CATEGORIES = {"Nd", "No", "Nl"}
_EMOJI_CATEGORIES = {"So", "Sm"}


def _classify_char(ch: str) -> tuple[str, dict[str, float]]:
    """Return (trace_status, role_candidates)."""
    cat = unicodedata.category(ch)
    arabic = is_arabic_letter(ch)
    diac = _is_diacritic(ch)
    space = ch in (' ', '\t', '\n', '\r', '\u00a0', '\u200b', '\u200c', '\u200d', '\ufeff')
    punct = cat.startswith('P')
    numeric = cat in _NUMERIC_CATEGORIES
    emoji = cat in _EMOJI_CATEGORIES or (0x1F000 <= ord(ch) <= 0x1FFFF)

    if arabic and not diac:
        if is_hamza(ch):
            rc = {"root_candidate": 0.5, "affix_candidate": 0.0}
        elif is_weak_letter(ch):
            rc = {"root_candidate": 0.3, "weak_letter": 1.0}
        else:
            rc = {"root_candidate": 0.8, "affix_candidate": 0.0}
        # single-char affixes
        if ch in {'و', 'ف', 'ب', 'ل', 'ك'}:
            rc["affix_candidate"] = 0.7
        return "classified", rc
    if diac:
        return "classified", {"diacritic_role": 1.0, "phonological_signal": 0.8}
    if space:
        return "ignored_for_semantics_but_tracked", {"token_boundary": 1.0}
    if punct:
        return "ignored_for_semantics_but_tracked", {"discourse_boundary": 1.0}
    if numeric:
        return "classified", {"numeric_value": 1.0}
    if emoji:
        return "classified", {"pragmatic_marker": 0.5, "unsupported_symbol": 0.5}
    if ch.isalpha():
        # Latin or other script inside Arabic text
        return "classified", {"foreign_token_component": 1.0}
    return "unknown_but_tracked", {"unknown_symbol": 1.0}


@dataclass
class UnicodeTraceUnit:
    trace_id: str
    char: str
    unicode_code: int
    char_index: int
    unicode_name: str
    unicode_category: str
    bidi_class: str
    normalized_nfc: str
    normalized_nfd: str
    is_arabic: bool
    is_letter: bool
    is_diacritic: bool
    is_space: bool
    is_punctuation: bool
    feature_vector: dict[str, float | str | bool]
    role_candidates: dict[str, float]
    trace_status: str

    def __post_init__(self) -> None:
        if self.trace_status not in TRACE_STATUSES:
            raise ValueError(f"Invalid trace_status '{self.trace_status}'")

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "char": self.char,
            "unicode_code": self.unicode_code,
            "char_index": self.char_index,
            "unicode_name": self.unicode_name,
            "unicode_category": self.unicode_category,
            "bidi_class": self.bidi_class,
            "normalized_nfc": self.normalized_nfc,
            "normalized_nfd": self.normalized_nfd,
            "is_arabic": self.is_arabic,
            "is_letter": self.is_letter,
            "is_diacritic": self.is_diacritic,
            "is_space": self.is_space,
            "is_punctuation": self.is_punctuation,
            "feature_vector": self.feature_vector,
            "role_candidates": self.role_candidates,
            "trace_status": self.trace_status,
        }


def build_unicode_trace_unit(char: str, char_index: int) -> UnicodeTraceUnit:
    """Build a UnicodeTraceUnit for a single character. Never raises for unknown chars."""
    trace_id = f"U-{char_index:06d}-{uuid.uuid4().hex[:8]}"
    c = char[0] if char else '\x00'
    cp = ord(c)

    try:
        uname = unicodedata.name(c, f"UNKNOWN_U{cp:04X}")
    except Exception:
        uname = f"UNKNOWN_U{cp:04X}"
    try:
        ucat = unicodedata.category(c)
    except Exception:
        ucat = "Cn"
    try:
        bidi = unicodedata.bidirectional(c)
    except Exception:
        bidi = ""
    nfc = unicodedata.normalize("NFC", c)
    nfd = unicodedata.normalize("NFD", c)

    arabic = is_arabic_letter(c)
    diac = _is_diacritic(c)
    space = c in (' ', '\t', '\n', '\r', '\u00a0', '\u200b', '\u200c', '\u200d', '\ufeff')
    punct = ucat.startswith('P')
    letter = (arabic and not diac) or (c.isalpha() and not arabic)

    try:
        fv = _VECTORIZER.vectorize(c).to_dict()
    except Exception:
        fv = {
            "unicode_code": cp,
            "is_arabic": False,
            "is_letter": False,
            "is_diacritic": False,
            "is_space": space,
            "is_punctuation": punct,
            "root_candidate_score": 0.0,
            "affix_candidate_score": 0.0,
            "weak_letter_score": 0.0,
            "diacritic_role": "",
            "connects_right": False,
            "connects_left": False,
        }

    status, role_candidates = _classify_char(c)

    return UnicodeTraceUnit(
        trace_id=trace_id,
        char=c,
        unicode_code=cp,
        char_index=char_index,
        unicode_name=uname,
        unicode_category=ucat,
        bidi_class=bidi,
        normalized_nfc=nfc,
        normalized_nfd=nfd,
        is_arabic=arabic or diac,
        is_letter=letter,
        is_diacritic=diac,
        is_space=space,
        is_punctuation=punct,
        feature_vector=fv,
        role_candidates=role_candidates,
        trace_status=status,
    )
