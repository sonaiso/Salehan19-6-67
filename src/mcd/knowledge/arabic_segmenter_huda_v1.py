"""arabic_segmenter.py — lightweight Arabic stem extractor.

Prefix/suffix data adapted from fractal/Huda/src/segmenter.py (ArabicSegmenter class),
stripped of masaq_engine / clean_code dependencies and re-packaged as a standalone
helper for mishkat_root_lookup.py.

Public API
----------
extract_stem(word: str) -> str | None
    Returns the stem after stripping one prefix and one suffix.
    Returns None if the word is a mabni particle (no root).

is_mabni(word: str) -> bool
    True if the word is a particle / stop-word that has no trilateral root.
"""
from __future__ import annotations
import re

#  Explicit Unicode-escape regex: avoids RTL rendering bugs in char class literals.
# U+0610-061A: Arabic honorific signs  U+064B-065F: harakat
# U+0670: superscript alef  U+06D6-06ED: Quranic annotation marks
# prone to byte-order issues when embedded as literals.
_DIACRITICS_RE = re.compile('[ؐ-ًؚ-ٰٟۖ-ۭ]')
_ALEF_NORM = str.maketrans("أإآ", "ااا")

def _clean(text: str) -> str:
    """Strip diacritics and leading/trailing whitespace."""
    return _DIACRITICS_RE.sub("", text.strip())


# ── Mabni / stop-words ────────────────────────────────────────────────────────
# These are حروف (particles), مبنيات (invariables), and common pronouns that
# carry no derivable Arabic trilateral root.  lookup_root() returns None for them.
MABNI_WORDS: frozenset[str] = frozenset({
    # حروف الجر
    "في", "من", "إلى", "الى", "على", "عن", "عند", "لدى", "لدن", "بين",
    "فوق", "تحت", "قبل", "بعد", "مع", "نحو", "حول", "خلال",
    "حتى", "منذ", "رب", "مذ",
    # حروف ناسخة / شرط / مصدرية
    "إن", "ان", "أن", "كأن", "لكن", "لعل", "ليت", "إذ", "إذا", "لو",
    "لولا", "لوما", "أما", "أو", "أم", "بل", "لا", "كلا",
    # أدوات نفي / جزم / نصب
    "لم", "لن", "لما", "ما", "هل", "قد", "سوف",
    # حروف عطف بسيطة
    "ف", "و", "ثم",
    # ضمائر منفصلة
    "أنا", "نحن", "أنت", "أنتَ", "أنتِ", "أنتما", "أنتم", "أنتن",
    "هو", "هي", "هما", "هم", "هن",
    # أسماء موصول
    "الذي", "التي", "اللذان", "اللتان", "الذين", "اللواتي", "اللاتي",
    "من", "ما", "مَن",
    # أسماء إشارة
    "هذا", "هذه", "هذان", "هاتان", "هؤلاء",
    "ذلك", "تلك", "ذانك", "تانك", "أولئك",
    # استفهام
    "كيف", "أين", "متى", "أيان", "كم", "أنى",
    # ظروف مبنية
    "حيث", "إذ", "الآن", "أمس", "غد",
    # حروف التحضير / التفسير
    "ألا", "أما", "إما", "هلا",
})


# ── Prefixes (longest first) — from Huda ArabicSegmenter.PREFIXES ─────────────
# Each entry: (prefix_string, morph_tag)
_PREFIXES: list[tuple[str, str]] = [
    # compound prefixes
    ("وال", "CONJ+DET"),
    ("فال", "CONJ+DET"),
    ("بال", "PREP+DET"),
    ("كال", "PREP+DET"),
    ("لل",  "PREP+DET"),
    ("ول",  "CONJ+PREP"),
    ("فل",  "CONJ+PREP"),
    ("وب",  "CONJ+PREP"),
    ("فب",  "CONJ+PREP"),
    ("وس",  "CONJ+FUTURE"),
    ("فس",  "CONJ+FUTURE"),
    # simple prefixes
    ("ال",  "DET"),
    ("و",   "CONJ"),
    ("ف",   "CONJ"),
    ("ب",   "PREP"),
    ("ل",   "PREP"),
    ("س",   "FUTURE"),
    # imperfect verb prefixes (ي / ت / ن) — strip conservatively
    # only when remaining stem >= 3 chars (MIN_VERB_STEM below)
    ("ي",   "IMPERF_PREF"),
    ("ت",   "IMPERF_PREF"),
    ("ن",   "IMPERF_PREF"),
]

# ── Suffixes (longest first) — from Huda ArabicSegmenter.SUFFIXES ─────────────
# Compound pronoun / plural suffixes first, then simple inflectional ones.
_SUFFIXES: list[tuple[str, str]] = [
    # compound verb suffixes (subject pronoun + object pronoun)
    ("تموهم", "SUBJ+OBJ"),
    ("تموها", "SUBJ+OBJ"),
    ("تموهن", "SUBJ+OBJ"),
    ("ناهم",  "SUBJ+OBJ"),
    ("ناها",  "SUBJ+OBJ"),
    ("ناه",   "SUBJ+OBJ"),
    # feminine plural + possessive
    ("اتنا",  "FEM_PL+POSS"),
    ("اتهم",  "FEM_PL+POSS"),
    ("اتها",  "FEM_PL+POSS"),
    ("اتكم",  "FEM_PL+POSS"),
    ("اتهن",  "FEM_PL+POSS"),
    ("تنا",   "FEM_SG+POSS"),
    # جماعة + مفعول
    ("وهم",   "SUBJ+OBJ"),
    ("وها",   "SUBJ+OBJ"),
    ("ونه",   "SUBJ+OBJ"),
    ("ونا",   "SUBJ+OBJ"),
    ("وني",   "SUBJ+OBJ"),
    ("وه",    "SUBJ+OBJ"),
    ("ونكم",  "SUBJ+OBJ"),
    ("ونهم",  "SUBJ+OBJ"),
    ("ونها",  "SUBJ+OBJ"),
    # possessive / subject plural pronouns
    ("كم",    "POSS"),
    ("هم",    "POSS"),
    ("ها",    "POSS"),
    ("هن",    "POSS"),
    ("تمو",   "SUBJ"),
    ("نا",    "POSS"),
    ("وا",    "SUBJ"),
    # plural/dual suffixes
    ("يون",   "MASC_PL_NOM"),
    ("ون",    "SUBJ_PRON"),
    ("ين",    "MASC_PL"),
    ("ان",    "DU"),
    ("ات",    "FEM_PL"),
    # singular
    ("ة",     "FEM_SG"),
    ("ت",     "FEM/SUBJ"),   # tā' marbūṭa open form or past-tense suffix
    ("ه",     "POSS"),
    ("ك",     "POSS"),
    ("ي",     "POSS"),
    ("ا",     "ALIF"),       # accusative / dual alif
    ("ن",     "SUBJ_PRON"),  # nūn al-niswah
]

# Minimum remaining length after stripping a nominal/conjunction prefix (ال، و، ف…)
_MIN_STEM = 2
# Minimum remaining length after stripping a verb-related prefix (ي، ت، ن، س)
# These prefixes can look like root-initial letters; require >= 3-char remainder
# so we never carve into a short root (e.g. "سرت" must not → "رت").
_MIN_VERB_STEM = 3
# Tags that require the stricter verb-stem minimum
_VERB_LIKE_TAGS = {"IMPERF_PREF", "FUTURE"}


def extract_stem(word: str) -> str | None:
    """Strip one prefix and one suffix from *word*, returning the bare stem.

    Applies the PREFIXES and SUFFIXES tables (longest match first) from the
    Huda ArabicSegmenter, without any masaq_engine dependency.

    Returns
    -------
    str | None
        The stem after stripping, or None if the word is a recognised mabni
        particle (is_mabni() is True) or if no valid stem could be extracted.
    """
    w = _clean(word)
    if not w:
        return None
    if w in MABNI_WORDS:
        return None

    # ── 1. Strip one prefix (longest match) ──────────────────────────────────
    stem = w
    for prefix, tag in _PREFIXES:
        if not w.startswith(prefix):
            continue
        remaining = w[len(prefix):]
        min_len = _MIN_VERB_STEM if tag in _VERB_LIKE_TAGS else _MIN_STEM
        if len(remaining) >= min_len:
            stem = remaining
            break   # strip at most one prefix

    # ── 2. Strip one suffix (longest match) ──────────────────────────────────
    for suffix, _ in _SUFFIXES:
        if not stem.endswith(suffix):
            continue
        remaining = stem[: -len(suffix)]
        if len(remaining) >= _MIN_STEM:
            stem = remaining
            break   # strip at most one suffix

    return stem if stem else None


def is_mabni(word: str) -> bool:
    """Return True if *word* (after diacritic removal) is a mabni particle."""
    return _clean(word) in MABNI_WORDS
