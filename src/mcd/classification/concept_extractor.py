"""ConceptExtractor — tokenizes and extracts concepts from Arabic prompts.

Rules-based, deterministic. No LLM required.
Steps:
  1. Normalize text (strip diacritics, normalise alef/ta-marbuta).
  2. Split into clauses on sentence boundaries.
  3. Tokenize Arabic words.
  4. Detect multi-word concepts using a fixed list.
  5. Return list of PromptConcept.
"""
from __future__ import annotations

import re
from typing import List

from mcd.classification.prompt_frame import PromptConcept


# ---------------------------------------------------------------------------
# Multi-word concept list (order matters: longer matches first)
# ---------------------------------------------------------------------------

MULTI_WORD_CONCEPTS: list[tuple[str, ...]] = [
    ("ذكاء", "اصطناعي"),
    ("نظام", "تعليمي"),
    ("درجة", "يقين"),
    ("معلومات", "سابقة"),
    ("دليل", "شرعي"),
    ("حكم", "معرفي"),
    ("حكم", "شرعي"),
    ("الدال", "والمدلول"),
    ("دال", "مدلول"),
    ("العقل", "المعرفي"),
    ("عقل", "معرفي"),
    ("علم", "الكلام"),
    ("علم", "الأصول"),
    ("نظام", "معرفي"),
    ("نظام", "شرعي"),
    ("وجهة", "نظر"),
]


# ---------------------------------------------------------------------------
# Text normalization helpers
# ---------------------------------------------------------------------------

_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]")
_TANWIN_RE = re.compile(r"[ًٌٍ]")  # tanwin fatha/damma/kasra
_ALEF_RE = re.compile(r"[أإآٱ]")
_TAMARB_RE = re.compile(r"ة$")
# Matches non-Arabic-letter, non-space characters, including Arabic punctuation like ؟ ، ؛
_PUNCT_RE = re.compile(r"[^\u0621-\u064A\u0660-\u0669\w\s]")


def _normalize(text: str) -> str:
    text = _DIACRITICS_RE.sub("", text)
    text = _TANWIN_RE.sub("", text)  # strip tanwin endings (نظامًا → نظاما → نظام after alif)
    text = _ALEF_RE.sub("ا", text)
    text = " ".join(_TAMARB_RE.sub("ه", w) for w in text.split())
    text = _PUNCT_RE.sub(" ", text)
    # Also strip trailing ا from words that had tanwin fatha (نظاما → نظام)
    words = []
    for w in text.split():
        if w.endswith("ا") and len(w) > 2 and not w.endswith("ها"):
            words.append(w[:-1])  # نظاما → نظام, تعليميا → تعليمي
        else:
            words.append(w)
    return " ".join(words)


def _tokenize(text: str) -> list[str]:
    """Split into tokens, filtering empties."""
    return [t for t in text.split() if t]


# ---------------------------------------------------------------------------
# ConceptExtractor
# ---------------------------------------------------------------------------

class ConceptExtractor:
    """Extract PromptConcept list from raw Arabic text."""

    def extract(self, raw_text: str) -> list[PromptConcept]:
        normalized = _normalize(raw_text)
        tokens = _tokenize(normalized)
        return self._build_concepts(tokens, raw_text)

    # ------------------------------------------------------------------

    def _build_concepts(self, tokens: list[str], raw_text: str) -> list[PromptConcept]:
        concepts: list[PromptConcept] = []
        i = 0
        while i < len(tokens):
            matched_len = self._match_multi_word(tokens, i)
            if matched_len > 1:
                surface = " ".join(tokens[i: i + matched_len])
                concept = PromptConcept(
                    surface=surface,
                    normalized=_normalize(surface),
                    span_start=i,
                    span_end=i + matched_len,
                )
                concepts.append(concept)
                i += matched_len
            else:
                w = tokens[i]
                if _is_content_word(w):
                    concept = PromptConcept(
                        surface=w,
                        normalized=_normalize(w),
                        span_start=i,
                        span_end=i + 1,
                    )
                    concepts.append(concept)
                i += 1
        return concepts

    def _match_multi_word(self, tokens: list[str], start: int) -> int:
        """Return length of multi-word match starting at `start`, else 1."""
        for mw in MULTI_WORD_CONCEPTS:
            if start + len(mw) > len(tokens):
                continue
            candidate = tuple(tokens[start: start + len(mw)])
            if candidate == mw:
                return len(mw)
        return 1


# ---------------------------------------------------------------------------
# Filter stop words
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset({
    "في", "من", "إلى", "على", "عن", "مع", "هو", "هي", "هم",
    "ما", "هل", "كيف", "لماذا", "أين", "متى", "الذي", "التي",
    "وهو", "وهي", "كان", "يكون", "قد", "لا", "لم",
    "لن", "ثم", "أو", "و", "أن", "إن", "إذا", "بعد", "قبل",
    "عند", "بين", "حتى", "لأن", "لكن", "فإن", "فهو",
})


def _is_content_word(word: str) -> bool:
    if word in _STOP_WORDS:
        return False
    if len(word) < 2:
        return False
    return True
