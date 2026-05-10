"""TokenTrace — groups graphemes into tokens."""
from __future__ import annotations

import re
import uuid
import unicodedata
from dataclasses import dataclass, field
from mcd.traceability.unicode_trace import UnicodeTraceUnit
from mcd.traceability.grapheme_trace import GraphemeTrace

TOKEN_TYPES = ["word", "number", "punctuation", "whitespace", "mixed", "unknown"]

_RE_WHITESPACE = re.compile(r'^\s+$')
_RE_NUMBER = re.compile(r'^[\d٠-٩]+$')
_RE_PUNCTUATION = re.compile(r'^[^\w\s]+$', re.UNICODE)


def _detect_token_type(surface: str) -> str:
    if _RE_WHITESPACE.match(surface):
        return "whitespace"
    if _RE_NUMBER.match(surface):
        return "number"
    if _RE_PUNCTUATION.match(surface):
        return "punctuation"
    # Check if mixed (contains both letters and non-letters)
    has_alpha = any(c.isalpha() for c in surface)
    has_non_alpha = any(not c.isalpha() and not c.isspace() for c in surface)
    if has_alpha and has_non_alpha:
        return "mixed"
    if has_alpha:
        return "word"
    return "unknown"


def _build_role_vector(surface: str, graphemes: list[GraphemeTrace]) -> dict[str, float]:
    rv: dict[str, float] = {}
    for g in graphemes:
        for k, v in g.role_candidates.items():
            rv[k] = max(rv.get(k, 0.0), v)
    return rv


@dataclass
class TokenTrace:
    token_id: str
    surface: str
    unicode_trace_ids: list[str]
    grapheme_ids: list[str]
    token_type: str
    normalized: str
    role_vector: dict[str, float]
    domain_hint_vector: dict[str, float]
    metadata: dict

    def __post_init__(self) -> None:
        if self.token_type not in TOKEN_TYPES:
            raise ValueError(f"Invalid token_type '{self.token_type}'")

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "surface": self.surface,
            "unicode_trace_ids": self.unicode_trace_ids,
            "grapheme_ids": self.grapheme_ids,
            "token_type": self.token_type,
            "normalized": self.normalized,
            "role_vector": self.role_vector,
            "domain_hint_vector": self.domain_hint_vector,
            "metadata": self.metadata,
        }


def build_token_traces(
    text: str,
    unicode_units: list[UnicodeTraceUnit],
    graphemes: list[GraphemeTrace],
) -> list[TokenTrace]:
    """Split text into tokens and link each token to its unicode trace IDs and grapheme IDs."""
    if not text:
        return []

    # Build index: char_index -> UnicodeTraceUnit
    idx_to_unit: dict[int, UnicodeTraceUnit] = {u.char_index: u for u in unicode_units}
    # Build index: char -> GraphemeTrace (use base_char of grapheme)
    # We need grapheme_id by position; link via unicode_trace_ids
    uid_to_grapheme: dict[str, GraphemeTrace] = {}
    for g in graphemes:
        for uid in g.unicode_trace_ids:
            uid_to_grapheme[uid] = g

    tokens: list[TokenTrace] = []

    # Use simple whitespace-aware tokenizer that preserves whitespace tokens
    # Split by Arabic/non-Arabic boundaries and whitespace
    # Tokenize character by character, grouping consecutive non-whitespace chars
    i = 0
    current_chars: list[int] = []  # char indices

    def flush_token(char_indices: list[int]) -> None:
        if not char_indices:
            return
        surface = "".join(idx_to_unit[ci].char for ci in char_indices if ci in idx_to_unit)
        if not surface:
            return
        u_ids = [idx_to_unit[ci].trace_id for ci in char_indices if ci in idx_to_unit]
        g_ids_seen: list[str] = []
        g_ids_set: set[str] = set()
        for uid in u_ids:
            if uid in uid_to_grapheme:
                gid = uid_to_grapheme[uid].grapheme_id
                if gid not in g_ids_set:
                    g_ids_set.add(gid)
                    g_ids_seen.append(gid)
        glist = [g for g in graphemes if g.grapheme_id in g_ids_set]
        tok_type = _detect_token_type(surface)
        role_vec = _build_role_vector(surface, glist)
        norm = unicodedata.normalize("NFC", surface).strip()
        tid = f"T-{len(tokens):06d}-{uuid.uuid4().hex[:8]}"
        tokens.append(TokenTrace(
            token_id=tid,
            surface=surface,
            unicode_trace_ids=u_ids,
            grapheme_ids=g_ids_seen,
            token_type=tok_type,
            normalized=norm,
            role_vector=role_vec,
            domain_hint_vector={},
            metadata={},
        ))

    for ci, unit in enumerate(unicode_units):
        if unit.is_space:
            # flush current token
            flush_token(current_chars)
            current_chars = []
            # emit whitespace token
            flush_token([unit.char_index])
        else:
            current_chars.append(unit.char_index)

    flush_token(current_chars)
    return tokens
