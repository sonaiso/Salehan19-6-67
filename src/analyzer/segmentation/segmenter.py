# -*- coding: utf-8 -*-
"""
Arabic token segmenter — conservative prefix + suffix peeling.

Peels common clitics (و/ف, ب+ال/ك+ال/ل+ال, ال, and single ب/ك/ل with
wazn-aware checks).  Optionally peels a finite-verb suffix from the end when
the remainder is morphologically plausible (wazn-aware probe, or a narrow فِعْ
two-unit hollow stem).

Public API:
    segment_token(surface: str) -> dict
    stem_surfaces_for_wazn(segmentation: dict) -> list[str]
"""

from __future__ import annotations

import unicodedata
from typing import Any, Optional

from analyzer.utils.arabic_units import split_units
from analyzer.wazn.matcher import best_wazn

# ── Type aliases ──────────────────────────────────────────────────────────────
_Unit       = tuple[str, tuple[str, ...]]
_UnitList   = list[_Unit]
_PeelResult = tuple[_UnitList, list[str]]

# ── Global constants ──────────────────────────────────────────────────────────

_MIN_STEM_UNITS = 2

FATHA   = "َ"
DAMMA   = "ُ"
KASRA   = "ِ"
SUKUN   = "ْ"
_SHADDA = "ّ"

_SUN_LETTERS  = frozenset("تثدذرزسشصضطظلن")
_ALIF_FAMILY  = frozenset({"ا", "أ", "إ", "آ", "ٱ"})
_ARTICLE_ALIF = frozenset({"ا", "ٱ"})

_VERB_SUFFIX_PATTERNS: tuple[str, ...] = (
    "تُمُو", "تُنَّ", "تُمْ",
    "نَا", "وا", "تُ", "تَ", "تِ",
    "نَ", "تْ",
)

_FI3L_ALLOWED_SUFFIXES = frozenset({
    "تُ", "تَ", "تِ",
    "نَا", "نَ", "تُمْ",
    "تُنَّ", "وا",
})

_PRONOUN_SUFFIX_PATTERNS: tuple[str, ...] = (
    "هُمَا", "هِمَا", "كُمَا",
    "كُمُ", "كُمْ", "كُنَّ",
    "هُمُ", "هُمْ", "هِمُ", "هِمْ", "هُنَّ",
    "هَا", "نَا", "نِي",
    "كَ", "كِ", "هُ", "هِ",
)

_RESTORE_PREFIXES = frozenset([
    "كَ", "كِ", "كُ",
    "بَ", "بِ", "بُ",
    "فِ", "وِ", "لُ",
])


# ── Low-level unit helpers ────────────────────────────────────────────────────

def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def _unit_str(unit: _Unit) -> str:
    letter, marks = unit
    return letter + "".join(marks)


def _units_str(units: _UnitList) -> str:
    return "".join(_unit_str(u) for u in units)


def _suffix_matches_end(working: _UnitList, suffix_str: str) -> bool:
    su = split_units(_nfc(suffix_str))
    if not su or len(su) > len(working):
        return False
    return working[-len(su):] == su


def _strip_trailing_combining_marks(s: str) -> str:
    """Remove trailing Unicode combining marks (e.g. iʿrāb after the last letter)."""
    s = _nfc(s)
    while s and unicodedata.combining(s[-1]):
        s = s[:-1]
    return s


# ── Morphological shape helpers ───────────────────────────────────────────────

def _is_fi3l_two_unit_stem(stem_units: _UnitList) -> bool:
    """Hollow/jussive stem shape فِعْ: kasra on first radical, sukun on second."""
    if len(stem_units) != 2:
        return False
    _, m0 = stem_units[0]
    _, m1 = stem_units[1]
    return KASRA in m0 and SUKUN in m1


def _relax_last_radical_to_fatha(stem_units: _UnitList) -> _UnitList | None:
    """Last radical sukun or damma → fatha for wazn probe (كَتَبْ → كَتَبَ)."""
    if len(stem_units) < 3:
        return None
    letter, marks = stem_units[-1]
    if marks == (SUKUN,) or marks == (DAMMA,):
        return list(stem_units[:-1]) + [(letter, (FATHA,))]
    return None


def _try_append_alif_for_past_plural(stem_units: _UnitList) -> _UnitList | None:
    """Append ا to bare-و stem to reconstruct فَعَلُوا shape for wazn probe."""
    if len(stem_units) < 3:
        return None
    last_letter, last_marks = stem_units[-1]
    if last_letter != "و" or last_marks:
        return None
    return list(stem_units) + [("ا", ())]


# ── Stem validation after peeling ────────────────────────────────────────────

def _stem_validates_after_verb_suffix_peel(
    stem_units: _UnitList,
    stem_str: str,
    suffix_str: str,
) -> bool:
    if len(stem_units) < _MIN_STEM_UNITS:
        return False
    wz, _, _ = best_wazn(stem_str)
    if wz is not None:
        return True
    relaxed = _relax_last_radical_to_fatha(stem_units)
    if relaxed is not None:
        wz2, _, _ = best_wazn(_units_str(relaxed))
        if wz2 is not None:
            return True
    if (
        len(stem_units) == 2
        and _is_fi3l_two_unit_stem(stem_units)
        and suffix_str in _FI3L_ALLOWED_SUFFIXES
    ):
        return True
    return False


def _stem_validates_after_pronoun_peel(stem_units: _UnitList) -> bool:
    """
    True when the pronoun-stripped stem has a plausible morphological shape.

    Tries (in order):
      1. best_wazn on the stem as-is.
      2. Past-3pl alif append.
      3. Strip trailing iʿrāb (3+ units only).
      4. Peel one verb suffix then wazn ± relaxed probe.
      5. Hollow فِعْ two-unit shape.
      6. Shadda-final 2-unit particle stem (إنّ, كنّ, منّ…).
    """
    if len(stem_units) < _MIN_STEM_UNITS:
        return False

    stem_str = _units_str(stem_units)

    wz, _, _ = best_wazn(stem_str)
    if wz is not None:
        return True

    appended = _try_append_alif_for_past_plural(stem_units)
    if appended is not None:
        wz_a, _, _ = best_wazn(_units_str(appended))
        if wz_a is not None:
            return True

    if len(stem_units) >= 3:
        no_irab = _strip_trailing_combining_marks(stem_str)
        if no_irab != stem_str:
            wz_ni, _, _ = best_wazn(no_irab)
            if wz_ni is not None:
                return True

    for vsuf in _VERB_SUFFIX_PATTERNS:
        vsu = split_units(_nfc(vsuf))
        if not vsu or len(stem_units) - len(vsu) < _MIN_STEM_UNITS:
            continue
        if not _suffix_matches_end(stem_units, vsuf):
            continue
        sub = stem_units[: -len(vsu)]
        sub_str = _units_str(sub)
        wz3, _, _ = best_wazn(sub_str)
        if wz3 is not None:
            return True
        rel2 = _relax_last_radical_to_fatha(sub)
        if rel2 is not None:
            wz4, _, _ = best_wazn(_units_str(rel2))
            if wz4 is not None:
                return True

    if len(stem_units) == 2 and _is_fi3l_two_unit_stem(stem_units):
        return True

    if len(stem_units) == 2 and _SHADDA in stem_units[-1][1]:
        return True

    return False


# ── Suffix peeling ────────────────────────────────────────────────────────────

def _try_shadda_fusion_pronoun_peel(working: _UnitList) -> _PeelResult:
    """Shadda-fusion نَا: إِنَّا / كُنَّا / مِنَّا → keep shadda-ن in stem, peel نَا."""
    if len(working) < _MIN_STEM_UNITS + 1:
        return working, []
    last_letter, last_marks = working[-1]
    if last_letter != "ا":
        return working, []
    if last_marks and set(last_marks) - {FATHA}:
        return working, []
    second_letter, second_marks = working[-2]
    if second_letter != "ن" or _SHADDA not in second_marks:
        return working, []
    stem_units = working[:-1]
    if len(stem_units) < _MIN_STEM_UNITS:
        return working, []
    return stem_units, ["نَا"]


def _pronoun_suffix_matches_end(working: _UnitList, suffix_str: str) -> bool:
    """Pausal-tolerant match: final diacritic of the pronoun may be absent."""
    su = split_units(_nfc(suffix_str))
    if not su or len(su) > len(working):
        return False
    tail = working[-len(su):]
    if tail[:-1] != su[:-1]:
        return False
    tl, tm = tail[-1]
    sl, sm = su[-1]
    if tl != sl:
        return False
    return tm == sm or tm == ()


def _try_pronoun_peel(working: _UnitList) -> _PeelResult:
    """Peel one attached pronoun suffix if the remaining stem validates."""
    stem, suffix = _try_shadda_fusion_pronoun_peel(working)
    if suffix:
        return stem, suffix

    for pron in _PRONOUN_SUFFIX_PATTERNS:
        pu = split_units(_nfc(pron))
        if not pu or len(working) - len(pu) < _MIN_STEM_UNITS:
            continue
        if not _pronoun_suffix_matches_end(working, pron):
            continue
        stem_units = working[: -len(pu)]
        if _stem_validates_after_pronoun_peel(stem_units):
            return stem_units, [_units_str(split_units(_nfc(pron)))]

    return working, []


def _try_verb_suffix_peel(working: _UnitList) -> _PeelResult:
    """Peel one finite-verb suffix if units match and the remaining stem validates."""
    for suf in _VERB_SUFFIX_PATTERNS:
        su = split_units(_nfc(suf))
        if not su or len(working) - len(su) < _MIN_STEM_UNITS:
            continue
        if not _suffix_matches_end(working, suf):
            continue
        stem_units = working[: -len(su)]
        stem_str   = _units_str(stem_units)
        suf_str    = _units_str(su)
        if _stem_validates_after_verb_suffix_peel(stem_units, stem_str, suf_str):
            return stem_units, [suf_str]

    return working, []


# ── Prefix peeling — one function per case ───────────────────────────────────

def _peel_conjunctions(working: _UnitList) -> _PeelResult:
    """Step 1 — strip leading و / ف conjunctions (greedy loop)."""
    prefixes: list[str] = []
    while len(working) >= _MIN_STEM_UNITS + 1 and working[0][0] in ("و", "ف"):
        prefixes.append(_unit_str(working[0]))
        working = working[1:]
    return working, prefixes


def _peel_prep_plus_article(working: _UnitList) -> _PeelResult | None:
    """Step 2 — ب/ك/ل + ال."""
    if (
        len(working) >= 3 + _MIN_STEM_UNITS
        and working[0][0] in ("ب", "ك", "ل")
        and working[1][0] in _ARTICLE_ALIF
        and working[2][0] == "ل"
    ):
        return working[3:], [_unit_str(working[0]), _unit_str(working[1]) + _unit_str(working[2])]
    return None


def _peel_lam_sun_assimilation(working: _UnitList) -> _PeelResult | None:
    """Step 2b — ل + sun-letter-with-shadda (article alef elided).

    Case A: الذي-style (U2 is ل-shadda, U3 is sun letter without shadda) → stem at U3.
    Case B: regular assimilation → keep U2 with shadda stripped.
    """
    if not (
        len(working) >= 2 + _MIN_STEM_UNITS
        and working[0][0] == "ل"
        and working[1][0] in _SUN_LETTERS
        and _SHADDA in working[1][1]
    ):
        return None

    prefixes = [_unit_str(working[0]), "ال"]

    if (
        working[1][0] == "ل"
        and len(working) >= 3
        and working[2][0] in _SUN_LETTERS
        and _SHADDA not in working[2][1]
    ):
        return list(working[2:]), prefixes   # Case A

    first_letter, first_marks = working[1]
    new_marks   = tuple(m for m in first_marks if m != _SHADDA)
    return [(first_letter, new_marks)] + list(working[2:]), prefixes   # Case B


def _peel_lam_lam_sun_assimilation(working: _UnitList) -> _PeelResult | None:
    """Step 2c — ل + ل(sukun) + sun-letter(shadda) — e.g. لِلنَّاسِ."""
    if not (
        len(working) >= 3 + _MIN_STEM_UNITS
        and working[0][0] == "ل"
        and working[1][0] == "ل"
        and (SUKUN in working[1][1] or not working[1][1])
        and working[2][0] in _SUN_LETTERS
        and _SHADDA in working[2][1]
    ):
        return None

    third_letter, third_marks = working[2]
    new_marks   = tuple(m for m in third_marks if m != _SHADDA)
    return [(third_letter, new_marks)] + list(working[3:]), [_unit_str(working[0]), "ال"]


def _peel_lam_lam_moon(working: _UnitList) -> _PeelResult | None:
    """Step 2d — ل + ل(sukun) + moon-letter — e.g. لِلْكَافِرِينَ."""
    if not (
        len(working) >= 2 + _MIN_STEM_UNITS
        and working[0][0] == "ل"
        and working[1][0] == "ل"
        and SUKUN in working[1][1]
        and not (
            len(working) >= 3
            and working[2][0] in _SUN_LETTERS
            and _SHADDA in working[2][1]
        )
    ):
        return None

    return list(working[2:]), [_unit_str(working[0]), "ال"]


def _peel_bare_article(working: _UnitList) -> _PeelResult | None:
    """Step 3 — strip ال (hamzat wasl only)."""
    if (
        len(working) >= 2 + _MIN_STEM_UNITS
        and working[0][0] in _ARTICLE_ALIF
        and working[1][0] == "ل"
    ):
        return list(working[2:]), [_unit_str(working[0]) + _unit_str(working[1])]
    return None


def _full_span_wazn_hit(hit: Optional[dict[str, Any]], n_units: int) -> bool:
    if not hit or n_units <= 0:
        return False
    return hit.get("start") == 0 and hit.get("end") == n_units


def _peel_single_prep(working: _UnitList) -> _PeelResult:
    """Step 4 — single ب / ك / ل (wazn-aware loop)."""
    prefixes: list[str] = []
    while working and working[0][0] in ("ب", "ك", "ل") and len(working) > _MIN_STEM_UNITS:
        full_surface = _units_str(working)
        wz_full, hit_full, u_full = best_wazn(full_surface)
        n_full = len(u_full)

        if wz_full is not None and hit_full is not None and _full_span_wazn_hit(hit_full, n_full):
            break

        if hit_full is not None and hit_full.get("start") == 1 and working[0][0] == "ك":
            break

        candidate_stem = _units_str(working[1:])
        if not candidate_stem:
            break

        wz_stem, _, _ = best_wazn(candidate_stem)
        if wz_stem is None:
            if working[0][0] != "ب" or len(working) - 1 < 3:
                break

        prefixes.append(_unit_str(working[0]))
        working = working[1:]

    return working, prefixes


# ── Public API ────────────────────────────────────────────────────────────────

def segment_token(surface: str) -> dict:
    """
    Segment one Arabic surface form into prefixes, stem, and suffixes.

    Uses wazn-validated conservative prefix/suffix peeling.

    Output keys (stable):
        original, prefixes, stem, suffixes, segmented, notes
    """
    original = _nfc(surface)
    notes: list[str] = []

    units = split_units(original)
    if not units:
        return {
            "original":  original,
            "prefixes":  [],
            "stem":      original,
            "suffixes":  [],
            "segmented": False,
            "notes": (["empty_after_normalize"] if not original.strip() else ["no_letter_units"]),
        }

    working: _UnitList = list(units)
    prefixes: list[str] = []

    # ── Prefix pipeline ───────────────────────────────────────────────────────
    working, conj = _peel_conjunctions(working)
    prefixes.extend(conj)

    for _peel_fn in (
        _peel_prep_plus_article,
        _peel_lam_sun_assimilation,
        _peel_lam_lam_sun_assimilation,
        _peel_lam_lam_moon,
    ):
        result = _peel_fn(working)
        if result is not None:
            working, new_p = result
            prefixes.extend(new_p)
            break

    result = _peel_bare_article(working)
    if result is not None:
        working, new_p = result
        prefixes.extend(new_p)

    working, single = _peel_single_prep(working)
    prefixes.extend(single)

    # ── Suffix pipeline ───────────────────────────────────────────────────────
    working, pronoun_suf = _try_pronoun_peel(working)
    working, verb_suf    = _try_verb_suffix_peel(working)
    suffixes = verb_suf + pronoun_suf

    stem      = _units_str(working)
    segmented = bool(prefixes or suffixes)

    return {
        "original":  original,
        "prefixes":  prefixes,
        "stem":      stem,
        "suffixes":  suffixes,
        "segmented": segmented,
        "notes":     notes,
    }


# ── Wazn probe surface generator ─────────────────────────────────────────────

def stem_surfaces_for_wazn(segmentation: dict) -> list[str]:
    """
    Build candidate surfaces to try with best_wazn after segmentation.

    Candidates (in priority order):
      1. Restored-prefix stem (when a root-initial radical was stripped).
      2. Segmented stem as-is.
      3. Relaxed last-radical probe (sukun/damma → fatha).
      4. Past-3pl alif-append (bare-و stem → append ا).
      5. Trailing iʿrāb stripped.
      6. Solar-assimilation deshadda (when ال was present).
    """
    stem = _nfc(segmentation.get("stem") or "")
    if not stem:
        return []

    prefixes = segmentation.get("prefixes") or []

    stripped_pref = next(
        (p for p in reversed(prefixes) if _nfc(p) in _RESTORE_PREFIXES), None
    )
    out: list[str] = ([_nfc(stripped_pref) + stem, stem] if stripped_pref is not None
                      else [stem])

    units = split_units(stem)

    relaxed = _relax_last_radical_to_fatha(units)
    if relaxed is not None:
        r = _units_str(relaxed)
        if r not in out:
            out.append(r)

    appended_units = _try_append_alif_for_past_plural(units)
    if appended_units is not None:
        a = _units_str(appended_units)
        if a not in out:
            out.append(a)

    no_irab = _strip_trailing_combining_marks(stem)
    if no_irab != stem and no_irab not in out:
        out.append(no_irab)

    has_al = any("ال" in p for p in prefixes)
    if has_al and units and _SHADDA in units[0][1] and units[0][0] in _SUN_LETTERS:
        new_marks     = tuple(m for m in units[0][1] if m != _SHADDA)
        deshadda_stem = _units_str([(units[0][0], new_marks)] + units[1:])
        if deshadda_stem not in out:
            out.append(deshadda_stem)

    return out
