"""GraphemeTrace — groups Unicode units into grapheme clusters."""
from __future__ import annotations

import unicodedata
import uuid
from dataclasses import dataclass, field
from mcd.traceability.unicode_trace import UnicodeTraceUnit, _is_diacritic


@dataclass
class GraphemeTrace:
    grapheme_id: str
    unicode_trace_ids: list[str]
    surface: str
    base_char: str | None
    diacritics: list[str]
    normalized: str
    feature_vector: dict
    role_candidates: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "grapheme_id": self.grapheme_id,
            "unicode_trace_ids": self.unicode_trace_ids,
            "surface": self.surface,
            "base_char": self.base_char,
            "diacritics": self.diacritics,
            "normalized": self.normalized,
            "feature_vector": self.feature_vector,
            "role_candidates": self.role_candidates,
        }


def build_grapheme_traces(unicode_units: list[UnicodeTraceUnit]) -> list[GraphemeTrace]:
    """Cluster unicode units into grapheme clusters (base + combining marks)."""
    if not unicode_units:
        return []

    graphemes: list[GraphemeTrace] = []
    # Group: base char + following diacritics
    i = 0
    while i < len(unicode_units):
        unit = unicode_units[i]
        cluster_units = [unit]
        j = i + 1
        # Absorb following diacritics/combining marks
        while j < len(unicode_units) and unicode_units[j].is_diacritic:
            cluster_units.append(unicode_units[j])
            j += 1

        surface = "".join(u.char for u in cluster_units)
        base = None
        diacritics = []
        merged_fv: dict = {}
        merged_rc: dict[str, float] = {}

        for u in cluster_units:
            if not u.is_diacritic and base is None:
                base = u.char
                merged_fv = dict(u.feature_vector)
            elif u.is_diacritic:
                diacritics.append(u.char)
            # Merge role_candidates (max)
            for k, v in u.role_candidates.items():
                merged_rc[k] = max(merged_rc.get(k, 0.0), v)

        grapheme_id = f"G-{len(graphemes):06d}-{uuid.uuid4().hex[:8]}"
        graphemes.append(GraphemeTrace(
            grapheme_id=grapheme_id,
            unicode_trace_ids=[u.trace_id for u in cluster_units],
            surface=surface,
            base_char=base,
            diacritics=diacritics,
            normalized=unicodedata.normalize("NFC", surface),
            feature_vector=merged_fv,
            role_candidates=merged_rc,
        ))
        i = j

    return graphemes
