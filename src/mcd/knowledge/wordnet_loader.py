"""wordnet_loader — WordNet fallback grounding with CSV disambiguation map.

No core code is changed. This module provides ground_with_wordnet()
which is called only when Layers 1 (seed) and 2 (CSV) both miss.

Disambiguation: wordnet_map.csv tells us which synset to prefer for
each Arabic word, preventing wrong first-synset selection (e.g.
كتب → write.v.01 not read.v.08).
"""
from __future__ import annotations

import csv
import pathlib
import uuid
from typing import Optional

from mcd.grounding.grounded_frame import GroundedLexeme, GroundingStatus

_DATA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "data" / "knowledge"
_MAP_CSV  = _DATA_DIR / "wordnet_map.csv"

# Words explicitly marked as missing from Arabic OMW — skip WordNet lookup
_KNOWN_MISSING: set[str] = set()

# preferred synset map: normalized_arabic → synset_id
_SYNSET_MAP: dict[str, str] = {}

_loaded = False


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    if not _MAP_CSV.exists():
        _loaded = True
        return

    with open(_MAP_CSV, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            word     = row.get("word_normalized", "").strip()
            synset   = row.get("synset_id", "").strip()
            preferred = row.get("preferred", "yes").strip().lower()
            if not word:
                continue
            if not synset:
                # explicitly flagged as missing from OMW
                _KNOWN_MISSING.add(word)
                continue
            if preferred == "yes" and word not in _SYNSET_MAP:
                _SYNSET_MAP[word] = synset

    _loaded = True


def _strip_article(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word


def ground_with_wordnet(surface: str, normalized: Optional[str] = None) -> Optional[GroundedLexeme]:
    """Try to ground an Arabic word via WordNet + the disambiguation map.

    Returns a GroundedLexeme if WordNet finds a match, None otherwise.
    Certainty is capped at 0.65 (linguistic source, not empirical).
    """
    _ensure_loaded()

    norm = normalized or _strip_article(surface.strip())

    # Skip words we know are missing
    if norm in _KNOWN_MISSING or surface in _KNOWN_MISSING:
        return None

    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        return None

    lexeme_id = str(uuid.uuid4())[:8]

    # Determine which synset to use
    preferred_id = _SYNSET_MAP.get(norm) or _SYNSET_MAP.get(surface)

    if preferred_id:
        # Use the preferred synset directly
        try:
            synset = wn.synset(preferred_id)
            return GroundedLexeme(
                lexeme_id=lexeme_id,
                surface=surface,
                normalized=norm,
                dal=norm,
                madlul=synset.definition(),
                grounding_status=GroundingStatus.GROUNDED,
                reality_ref=synset.name(),
                prior_knowledge_refs=[synset.name()],
                certainty=0.65,
                notes=f"WordNet:{synset.name()} (preferred via wordnet_map.csv)",
            )
        except Exception:
            pass

    # No preferred synset — query Arabic OMW directly, take first result
    synsets = wn.synsets(norm, lang="arb") or wn.synsets(surface, lang="arb")
    if synsets:
        s = synsets[0]
        return GroundedLexeme(
            lexeme_id=lexeme_id,
            surface=surface,
            normalized=norm,
            dal=norm,
            madlul=s.definition(),
            grounding_status=GroundingStatus.PARTIALLY_GROUNDED,
            reality_ref=s.name(),
            prior_knowledge_refs=[s.name()],
            certainty=0.55,
            notes=f"WordNet:{s.name()} (first match — add to wordnet_map.csv to fix if wrong)",
        )

    return None
