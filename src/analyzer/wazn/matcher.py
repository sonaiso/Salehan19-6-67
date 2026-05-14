"""Match fully vocalized words against awzān templates (فعل placeholders)."""

from __future__ import annotations

import unicodedata as _ud

from analyzer.utils.arabic_units import PLACEHOLDERS, split_units
from analyzer.wazn.wazn_data import WAZNS

SUKUN  = "ْ"
SHADDA = "ّ"
# Tanwīn (final noun case) counts as compatible with an unmarked template slot.
_TANWEEN = frozenset({"ً", "ٌ", "ٍ"})
# Triliteral verbal cores: require full diacritic agreement so particles like
# عَلَى / هَذَا do not spuriously match فَعَلَ.
_STRICT_TRILITERAL_WAZNS: frozenset[str] = frozenset(
    _ud.normalize("NFC", s)
    for s in {
        "فَعَلَ", "فَعِلَ", "فَعُلَ",
        "فَعَل", "فَعِل", "فَعُل",
        "فَعَّ",
    }
)

# Templates that require full-span + exact final-mark match.
_FULLSPAN_FINAL_STRICT_WAZNS: frozenset[str] = frozenset(
    _ud.normalize("NFC", s)
    for s in {
        "يَفْعُ", "تَفْعُ", "اِفْعُ",
        "يَفْعُوا", "تَفْعُوا", "اِفْعُوا",
        "يَفْعِ", "تَفْعِ", "نَفْعِ", "اِفْعِ",
        "فَعَلَا", "فَعَلُوا", "فَعَوْا",
        "فَعَلْتُ", "فَعَلْنَا",
        "يَفُل", "تَفُل", "أَفُل",
        "يُفِلُّ", "يَفِلُّ", "تُفِلُّ", "تَفِلُّ", "أُفِلُّ", "أَفِلُّ",
        "يُفِلَّ", "يَفِلَّ", "تُفِلَّ", "تَفِلَّ", "أُفِلَّ", "أَفِلَّ",
        "مُفِلّ", "فَالّ", "أَفَلُّ",
    }
)

_FF_STRICT_PIPELINE_GUARD: frozenset[str] = frozenset(
    _ud.normalize("NFC", s)
    for s in {
        "يُفِلُّ", "يَفِلُّ", "تُفِلُّ", "تَفِلُّ", "أُفِلُّ", "أَفِلُّ",
        "يُفِلَّ", "يَفِلَّ", "تُفِلَّ", "تَفِلَّ", "أُفِلَّ", "أَفِلَّ",
        "مُفِلّ", "فَالّ", "أَفَلُّ",
    }
)

_FAAL_NOUN_WAZNS: frozenset[str] = frozenset(
    _ud.normalize("NFC", s) for s in {"فِعْل", "فُعْل"}
)

_FULLSPAN_ONLY_WAZNS: frozenset[str] = frozenset(
    _ud.normalize("NFC", s)
    for s in {
        "فَعْلَة", "فِعْلَة", "فُعْلَة",
        "يُفِلُّوا", "يَفِلُّوا",
        "أَفَلُّوا",
    }
)

KASRA  = "ِ"
FATHA  = "َ"
DAMMA  = "ُ"
_VOWEL_MARKS  = frozenset({FATHA, KASRA, DAMMA})
ALIF          = "ا"
ALIF_MAQSURA  = "ى"
TA_MARBUTA    = "ة"
ALIF_FAMILY   = frozenset({"ا", "أ", "إ", "آ", "ٱ"})


def unit_match(
    word_unit: tuple[str, tuple[str, ...]],
    wazn_unit: tuple[str, tuple[str, ...]],
    *,
    template_len: int = 0,
    template_slot_idx: int = 0,
) -> bool:
    w_letter, w_marks = word_unit
    z_letter, z_marks = wazn_unit

    def marks_compatible_literals() -> bool:
        if w_marks == z_marks:
            return True
        if w_marks == () and z_marks == (SUKUN,):
            return True
        if w_marks == (SUKUN,) and z_marks == ():
            return True
        if z_letter == TA_MARBUTA:
            return True
        return False

    def marks_compatible_placeholders() -> bool:
        if w_marks == z_marks:
            return True
        if SHADDA not in z_marks:
            w_core = tuple(m for m in w_marks if m != SHADDA)
            if w_core == z_marks:
                if SHADDA in w_marks and template_slot_idx != 0:
                    return False
                return True
        if not w_marks or not z_marks:
            return True
        if template_len >= 6:
            return True
        return False

    def alif_family_marks_ok() -> bool:
        if w_marks == z_marks:
            return True
        if (w_marks == () and z_marks == (KASRA,)) or (w_marks == (KASRA,) and z_marks == ()):
            return True
        if (w_marks == () and z_marks == (FATHA,)) or (w_marks == (FATHA,) and z_marks == ()):
            return True
        return False

    if z_letter in PLACEHOLDERS:
        return marks_compatible_placeholders()

    if w_letter != z_letter:
        if {w_letter, z_letter} == {ALIF, ALIF_MAQSURA}:
            return marks_compatible_literals()
        if w_letter in ALIF_FAMILY and z_letter in ALIF_FAMILY:
            return alif_family_marks_ok()
        return False

    if w_letter == ALIF and z_letter == ALIF:
        if (w_marks == () and z_marks == (KASRA,)) or (w_marks == (KASRA,) and z_marks == ()):
            return True
        if (w_marks == (FATHA,) and z_marks == ()) or (w_marks == () and z_marks == (FATHA,)):
            return True

    HAMZA = "ء"
    if w_letter == HAMZA and z_letter == HAMZA:
        if not w_marks or not z_marks:
            return True

    return marks_compatible_literals()


def _try_match_at(
    word_units: list[tuple[str, tuple[str, ...]]],
    wazn_units: list[tuple[str, tuple[str, ...]]],
    start: int,
) -> tuple[dict | None, int, int, int]:
    n = len(word_units)
    m = len(wazn_units)
    if start < 0 or start + m > n:
        return None, 0, 0, 0
    mapping: dict[str, list[str]] = {"ف": [], "ع": [], "ل": []}
    exact_total = 0
    exact_literals = 0
    exact_ph = 0
    for i in range(m):
        wu = word_units[start + i]
        zu = wazn_units[i]
        _slot_guard = (m - 1) if i == m - 1 else 0
        if not unit_match(wu, zu, template_len=m, template_slot_idx=_slot_guard):
            return None, 0, 0, 0
        w_core = tuple(x for x in wu[1] if x != SHADDA)
        if wu[1] == zu[1]:
            exact_total += 1
        elif zu[0] in PLACEHOLDERS:
            if w_core == zu[1]:
                exact_total += 1
            elif (
                i == m - 1
                and not zu[1]
                and w_core
                and all(x in _TANWEEN for x in w_core)
            ):
                exact_total += 1
        if zu[0] not in PLACEHOLDERS and wu[1] == zu[1]:
            exact_literals += 1
        if zu[0] in PLACEHOLDERS:
            if (
                wu[1] == zu[1]
                or w_core == zu[1]
                or (
                    i == m - 1
                    and not zu[1]
                    and w_core
                    and all(x in _TANWEEN for x in w_core)
                )
            ):
                exact_ph += 1
            mapping[zu[0]].append(wu[0])
    hit = {"start": start, "end": start + m, "mapping": mapping}
    return hit, exact_literals, exact_total, exact_ph


def match_wazn(
    word_units: list[tuple[str, tuple[str, ...]]],
    wazn_units: list[tuple[str, tuple[str, ...]]],
) -> dict | None:
    n = len(word_units)
    m = len(wazn_units)
    if m > n:
        return None
    for start in range(0, n - m + 1):
        hit, _, _, _ = _try_match_at(word_units, wazn_units, start)
        if hit is not None:
            return hit
    return None


def _faeal_spurious_triliteral(word_units: list[tuple[str, tuple[str, ...]]]) -> bool:
    if len(word_units) != 3:
        return False
    last = word_units[-1][0]
    return last == ALIF or last == ALIF_MAQSURA


def _literal_letter_count(wazn_units: list[tuple[str, tuple[str, ...]]]) -> int:
    return sum(1 for zu in wazn_units if zu[0] not in PLACEHOLDERS)


def _maf3il_style_prefix_penalty(wazn_units: list[tuple[str, tuple[str, ...]]]) -> int:
    if len(wazn_units) < 2:
        return 0
    z0, z1 = wazn_units[0], wazn_units[1]
    if z0[0] == "م" and FATHA in z0[1] and z1[0] == "ف" and SUKUN in z1[1]:
        return 1
    return 0


def _placeholder_mark_weight(wazn_units: list[tuple[str, tuple[str, ...]]]) -> int:
    w = 0
    for zu in wazn_units:
        if zu[0] not in PLACEHOLDERS:
            continue
        marks = zu[1]
        slot = 0
        if SUKUN in marks:
            slot += 3
        slot += sum(1 for m in marks if m in _VOWEL_MARKS)
        w += min(slot, 3)
    return w


def _collect_candidates(
    word_units: list[tuple[str, tuple[str, ...]]],
    templates: list[str],
) -> list[tuple[str, dict, int, int, int]]:
    n = len(word_units)
    out: list[tuple[str, dict, int, int, int]] = []
    for t_idx, wz in enumerate(templates):
        wz_units = split_units(wz)
        m = len(wz_units)
        if m > n:
            continue
        for start in range(0, n - m + 1):
            hit, exact_literals, exact_total, exact_ph = _try_match_at(word_units, wz_units, start)
            if hit is None:
                continue
            if m == 1 and n > 2 and wz_units[0][0] in PLACEHOLDERS:
                continue
            if wz in _STRICT_TRILITERAL_WAZNS and exact_total < m:
                continue
            if wz == "فَعَل" and _faeal_spurious_triliteral(word_units):
                continue
            if wz in _FAAL_NOUN_WAZNS:
                mid_letter = word_units[start + 1][0]
                if mid_letter in ALIF_FAMILY or mid_letter == ALIF_MAQSURA:
                    continue
            if wz in _FULLSPAN_FINAL_STRICT_WAZNS:
                if hit["start"] != 0 or hit["end"] != n:
                    continue
                final_w_marks = word_units[n - 1][1]
                final_z_marks = wz_units[m - 1][1]
                if final_w_marks != final_z_marks:
                    continue
            if wz in _FULLSPAN_ONLY_WAZNS:
                if hit["start"] != 0 or hit["end"] != n:
                    continue
            out.append((wz, hit, exact_literals, exact_ph, t_idx))
    return out


def _sort_key(
    word_len: int,
    wazn_units: list[tuple[str, tuple[str, ...]]],
    hit: dict,
    exact_literal_marks: int,
    exact_placeholder_marks: int,
    template_index: int,
) -> tuple[int, int, int, int, int, int, int, int, int, int]:
    full       = 1 if hit["start"] == 0 and hit["end"] == word_len else 0
    m          = len(wazn_units)
    literals   = _literal_letter_count(wazn_units)
    degenerate = 1 if (word_len >= 4 and m <= 2 and not full) else 0
    ph_weight  = _placeholder_mark_weight(wazn_units)
    maf_pen    = _maf3il_style_prefix_penalty(wazn_units)
    return (
        full,
        1 - degenerate,
        m,
        literals,
        exact_literal_marks,
        -maf_pen,
        ph_weight,
        exact_placeholder_marks,
        -hit["start"],
        -template_index,
    )


def best_wazn(
    word: str,
    wazns: list[str] | None = None,
) -> tuple[str | None, dict | None, list[tuple[str, tuple[str, ...]]]]:
    """
    Return (best_wazn_string_or_None, match_dict_or_None, word_units).

    Among all template/window hits, prefer (in order):
    - full-span match over substring window
    - non-degenerate short windows on long words
    - longer templates
    - more fixed (non-placeholder) letters in the template
    - more exact diacritic matches
    - earlier window start
    - earlier position in the template list
    """
    templates  = WAZNS if wazns is None else wazns
    word_units = split_units(word)
    n = len(word_units)
    if not templates or not word_units:
        return None, None, word_units

    candidates = _collect_candidates(word_units, templates)
    if not candidates:
        return None, None, word_units

    scored: list[tuple[tuple[int, ...], str, dict]] = []
    for wz, hit, exact_literals, exact_ph, t_idx in candidates:
        wz_u = split_units(wz)
        key  = _sort_key(n, wz_u, hit, exact_literals, exact_ph, t_idx)
        scored.append((key, wz, hit))

    scored.sort(key=lambda x: x[0], reverse=True)
    _, best_wz, best_hit = scored[0]
    return best_wz, best_hit, word_units
