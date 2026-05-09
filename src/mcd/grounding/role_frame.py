"""RoleFrame — semantic role labeling for Arabic sentences."""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional

# Arabic diacritics (tashkeel) Unicode range
_DIACRITICS_RE = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670]")

# Time adverbs
_TIME_WORDS = {"أمس", "اليوم", "غدًا", "غدا", "صباحًا", "صباحا", "مساءً", "مساء"}

# Preposition prefixes
_BA_PREFIX = "بـ"
_FI_PREFIX = "في"


def strip_diacritics(text: str) -> str:
    return _DIACRITICS_RE.sub("", text)


def strip_article(word: str) -> str:
    """Remove the definite article ال from the beginning of a word."""
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word


def strip_ba_prefix(word: str) -> str:
    """Remove بـ / بال prefix and return core noun, or None if not present."""
    if word.startswith("بـ"):
        return strip_article(word[2:])
    if word.startswith("بال"):
        return word[3:]
    if word.startswith("بِ") or word.startswith("بِال"):
        return strip_article(word[1:])
    # Plain ب attached (like بالقلم without special char)
    if len(word) > 2 and word[0] == "ب" and word[1] == "ا" and word[2] == "ل":
        return word[3:]
    return ""


def strip_fi_prefix(word: str) -> str:
    """Remove في / فال prefix, return core noun or empty string."""
    if word == "في":
        return ""  # standalone preposition, next word is the place
    if word.startswith("في"):
        rest = word[2:]
        return strip_article(rest) if rest else ""
    if word.startswith("فال"):
        return word[3:]
    return ""


# Simple Arabic verb patterns (trilateral root forms starting with common verb-looking words)
# We use heuristic: word is a verb if it matches common verb morphology patterns
# or if it's the first word and ends with patterns typical for perfect tense verbs

_VERB_ENDINGS = {
    "كتب", "أكل", "شرب", "ذهب", "جاء", "قال", "رأى", "علم", "فعل",
    "دخل", "خرج", "نظر", "سمع", "أخذ", "وضع", "حمل", "ضرب", "عمل",
    "صنع", "بنى", "قرأ", "لعب", "سأل", "أجاب", "كسر", "فتح", "أغلق",
    "رفع", "وجد", "بحث", "طلب", "أرسل", "استقبل",
}

def _looks_like_verb(word: str, is_first: bool) -> bool:
    """Heuristic to detect Arabic verb."""
    clean = strip_diacritics(word)
    if clean in _VERB_ENDINGS:
        return True
    # Arabic perfect tense for trilateral verbs: فعل pattern (3 consonants)
    # Heuristic: first word of sentence, no definite article, 3-5 chars
    if is_first and not clean.startswith("ال") and 2 <= len(clean) <= 6:
        return True
    return False


@dataclass
class RoleFrame:
    frame_id: str
    raw_text: str
    event: Optional[str] = None
    agent: Optional[str] = None
    action: Optional[str] = None
    patient: Optional[str] = None
    instrument: Optional[str] = None
    place: Optional[str] = None
    time: Optional[str] = None
    cause: Optional[str] = None
    effect: Optional[str] = None
    condition: Optional[str] = None
    purpose: Optional[str] = None
    evidence: list = field(default_factory=list)
    certainty: float = 0.5


class RoleFrameBuilder:
    """Build RoleFrame from an Arabic sentence using rule-based heuristics."""

    def build(self, text: str) -> RoleFrame:
        frame_id = str(uuid.uuid4())[:8]
        tokens = strip_diacritics(text.strip()).split()

        action: Optional[str] = None
        agent: Optional[str] = None
        patient: Optional[str] = None
        instrument: Optional[str] = None
        place: Optional[str] = None
        time_word: Optional[str] = None
        event: Optional[str] = None

        nouns_found: list[str] = []
        i = 0
        skip_next = False  # used when في / بـ consume next token

        while i < len(tokens):
            token = tokens[i]

            # Time detection
            if token in _TIME_WORDS:
                time_word = token
                i += 1
                continue

            # بـ prefix → instrument
            ba_noun = strip_ba_prefix(token)
            if ba_noun:
                instrument = ba_noun
                i += 1
                continue

            # في standalone → next word is place
            if token == "في" and i + 1 < len(tokens):
                place = strip_article(strip_diacritics(tokens[i + 1]))
                i += 2
                continue

            # في attached (فيالمدرسة) — unusual but handle
            fi_noun = strip_fi_prefix(token)
            if fi_noun and token != "في":
                place = fi_noun
                i += 1
                continue

            # Verb detection (first position or explicit)
            if action is None and _looks_like_verb(token, i == 0):
                action = token
                event = token
                i += 1
                continue

            # Skip standalone prepositions we don't handle specially
            if token in {"على", "من", "إلى", "عن", "مع", "لـ", "ل", "كـ", "ك"}:
                i += 1
                continue

            # Everything else is a noun candidate
            nouns_found.append(strip_article(token))
            i += 1

        # Assign roles from noun list
        # Arabic VSO: verb → subject (agent) → object (patient)
        if len(nouns_found) >= 1:
            agent = nouns_found[0]
        if len(nouns_found) >= 2:
            patient = nouns_found[1]

        return RoleFrame(
            frame_id=frame_id,
            raw_text=text,
            event=event,
            agent=agent,
            action=action,
            patient=patient,
            instrument=instrument,
            place=place,
            time=time_word,
            certainty=0.6,
        )
