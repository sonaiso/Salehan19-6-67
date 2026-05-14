"""mabniyat_loader — loads Arabic indeclinables (مبنيات) from the
new_arabic_analyzer JSON database into PriorKnowledgeStore.

No core code is changed. Uses store.add_thing() only.
Reads from: /Users/husseinhiyassat/fractal/new_arabic_analyzer/data/02_mabniyat/
"""
from __future__ import annotations

import json
import pathlib
import re
import uuid

from mcd.knowledge.things import Thing
from mcd.core.evidence import Evidence, EvidenceType
from mcd.core.certainty import Certainty

_MABNIYAT_DIR = pathlib.Path(
    "/Users/husseinhiyassat/fractal/new_arabic_analyzer/data/02_mabniyat"
)

_EV_MABNIY = Evidence(
    source_id="src_mabniyat",
    source_type=EvidenceType.LINGUISTIC.value,
    description="مُحمَّل من قاعدة بيانات المبنيات",
    strength=0.95,
    reliability=0.95,
)

_DIACRITICS_RE = re.compile(
    r"[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۤۧۨ-ۭ]"
)


def _strip(text: str) -> str:
    return _DIACRITICS_RE.sub("", text.strip())


def _load_json(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if isinstance(raw, dict) and "data" in raw:
        return raw["data"]
    if isinstance(raw, list):
        return raw
    return []


def _load_pronouns(store) -> int:
    """Load pronouns_classification.json — all Arabic pronouns."""
    rows = _load_json(_MABNIYAT_DIR / "pronouns_classification.json")
    count = 0
    seen: set[str] = set()
    for row in rows:
        surface = (row.get("pronoun_form") or row.get("pronoun") or "").strip()
        if not surface:
            continue
        clean = _strip(surface)
        if not clean or clean in seen:
            continue
        seen.add(clean)

        category = row.get("category", "ضمير")
        meaning  = row.get("meaning", "")
        form     = row.get("form", "")
        example  = row.get("example", "")
        haqiqa   = f"{category} — {meaning} — {form}"

        thing = Thing(
            thing_id=f"mabniy_pronoun_{row.get('id', uuid.uuid4().hex[:6])}",
            names={"ar": clean, "ar_vocalized": surface},
            haqiqa=haqiqa,
            properties=[],
            effects=[],
            affordances=[],
            relations=[],
            evidence=[_EV_MABNIY],
            certainty=Certainty.from_score(0.95, "linguistic"),
        )
        store.add_thing(thing)
        count += 1
    return count


def _load_prepositions(store) -> int:
    """Load preposition_meanings.json — Arabic prepositions with meanings."""
    rows = _load_json(_MABNIYAT_DIR / "preposition_meanings.json")
    count = 0
    seen: set[str] = set()
    for row in rows:
        surface = (row.get("preposition") or "").strip()
        if not surface:
            continue
        clean = _strip(surface)
        if not clean or clean in seen:
            continue
        seen.add(clean)

        meaning = row.get("meaning", "حرف جر")
        haqiqa  = f"حرف جر — {meaning.strip('*').strip()}"

        thing = Thing(
            thing_id=f"mabniy_prep_{row.get('id', uuid.uuid4().hex[:6])}",
            names={"ar": clean, "ar_vocalized": surface},
            haqiqa=haqiqa,
            properties=[],
            effects=[],
            affordances=[],
            relations=[],
            evidence=[_EV_MABNIY],
            certainty=Certainty.from_score(0.95, "linguistic"),
        )
        store.add_thing(thing)
        count += 1
    return count


def _load_file_generic(store, filename: str, word_key: str,
                        category_label: str, id_prefix: str) -> int:
    """Generic loader for simple JSON files with a single word field."""
    rows = _load_json(_MABNIYAT_DIR / filename)
    count = 0
    seen: set[str] = set()
    for i, row in enumerate(rows):
        surface = (row.get(word_key) or "").strip()
        if not surface:
            continue
        clean = _strip(surface)
        if not clean or clean in seen:
            continue
        seen.add(clean)

        # Build haqiqa from all string fields
        parts = [f"{k}: {v}" for k, v in row.items()
                 if isinstance(v, str) and k != word_key and v.strip()]
        haqiqa = f"{category_label} — " + " | ".join(parts) if parts else category_label

        thing = Thing(
            thing_id=f"{id_prefix}_{i}",
            names={"ar": clean, "ar_vocalized": surface},
            haqiqa=haqiqa,
            properties=[],
            effects=[],
            affordances=[],
            relations=[],
            evidence=[_EV_MABNIY],
            certainty=Certainty.from_score(0.95, "linguistic"),
        )
        store.add_thing(thing)
        count += 1
    return count


def load_mabniyat(store) -> dict[str, int]:
    """Load all mabniyas files into the store. Returns count per file."""
    if not _MABNIYAT_DIR.exists():
        return {}

    counts: dict[str, int] = {}
    counts["pronouns"]      = _load_pronouns(store)
    counts["prepositions"]  = _load_prepositions(store)

    # Remaining files using generic loader
    generic_files = [
        ("relative_pronouns.json",         "pronoun",     "اسم موصول",      "mabniy_rel"),
        ("demonstrative_pronouns.json",     "pronoun",     "اسم إشارة",      "mabniy_dem"),
        ("interrogative_letters_tools.json","tool",        "أداة استفهام",   "mabniy_istf"),
        ("conditional_letters_tools.json",  "tool",        "أداة شرط",       "mabniy_shart"),
        ("coordinating_conjunctions.json",  "conjunction", "حرف عطف",        "mabniy_atf"),
        ("vocative_particles.json",         "particle",    "حرف نداء",       "mabniy_nida"),
        ("jazm_tools.json",                 "tool",        "أداة جزم",       "mabniy_jazm"),
        ("present_naseb_tools.json",        "tool",        "أداة نصب مضارع", "mabniy_nasb"),
        ("copulative_particle.json",        "particle",    "حرف ربط",        "mabniy_rabt"),
        ("letters_answers.json",            "letter",      "حرف جواب",       "mabniy_jawab"),
    ]
    for filename, word_key, label, prefix in generic_files:
        counts[filename] = _load_file_generic(store, filename, word_key, label, prefix)

    return counts
