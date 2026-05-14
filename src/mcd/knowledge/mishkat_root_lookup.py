"""mishkat_root_lookup -- general Arabic root extractor.

Four-layer approach:
  1.  Mishkat golden set (Quranic corpus) with subsequence validation
  1b. Audited verb→root database (Lisan al-Arab, ~4800 entries)
  1c. Segmenter-stripped stem retry (NAA conservative → Huda v1 fallback)
  2.  PatternMatcher morphological analysis (fa3il, maf3ul, ...)
  3.  Consonant skeleton with morphological suffix awareness

Segmenter priority (Layer 1c and skeleton):
  PRIMARY  — NAA conservative (analyzer.segmentation.conservative.segment_token)
             Bundled at Salehan19-6-67/src/analyzer/ — always importable.
             wazn-validated peels, works on vocalized text, production-tested on Quran.
  FALLBACK — Huda v1 (mcd.knowledge.arabic_segmenter.extract_stem)
             simple prefix/suffix lists, unvocalized text, no external dependency.
"""
from __future__ import annotations
import csv, pathlib, re
from functools import lru_cache
from mcd.knowledge.arabic_segmenter import is_mabni          # mabni guard (kept)
from mcd.knowledge.arabic_segmenter import extract_stem as _huda_extract_stem  # fallback
from mcd.knowledge.diacritizer_adapter import diacritize as _diacritize       # GPT-52 (optional)

_MISHKAT_CSV = pathlib.Path(
    "/Users/husseinhiyassat/fractal/new_arabic_analyzer/data/mishkat_word_root.csv"
)

# Audited verb→root database (Lisan al-Arab, ~4800 entries)
_AUDITED_CSV = (
    pathlib.Path(__file__).parent.parent.parent.parent / "data" / "knowledge" / "audited_roots.csv"
)

# Diacritics regex — U+0610-061A, U+064B-065F, U+0670, U+06D6-06ED
# Built with chr() to avoid RTL byte-order corruption when Arabic chars are
# embedded literally in source (the same fix applied in arabic_segmenter.py).
_DIACRITICS_RE = re.compile(
    "["
    + chr(0x0610) + "-" + chr(0x061A)
    + chr(0x064B) + "-" + chr(0x065F)
    + chr(0x0670)
    + chr(0x06D6) + "-" + chr(0x06ED)
    + "]"
)

_WEAK_VALIDATION = {"ا", "و", "ي", "ى"}
_MEDIAL_VOWELS   = {"ا", "ى"}
_SUFFIXES        = {"ة", "ى"}
_ALEF_NORM       = str.maketrans("أإآ", "ااا")


def _strip(text: str) -> str:
    return _DIACRITICS_RE.sub("", text.strip())

def _norm_alef(text: str) -> str:
    return text.translate(_ALEF_NORM)

def _strip_article(word: str) -> str:
    if word.startswith("ال") and len(word) > 2:
        return word[2:]
    return word

def _normalize(word: str) -> str:
    return _strip_article(_strip(word))

def _consonants_for_validation(stem: str) -> list[str]:
    return [c for c in stem if c not in _WEAK_VALIDATION and c not in _SUFFIXES]

def _root_in_stem(root: str, stem: str) -> bool:
    sc = _consonants_for_validation(stem)
    rc = _consonants_for_validation(root)
    si = 0
    for r in rc:
        while si < len(sc) and sc[si] != r:
            si += 1
        if si >= len(sc):
            return False
        si += 1
    return True


# ── NAA segmenter loader ───────────────────────────────────────────────────
_naa_segment_token = None   # None = not yet tried; False = unavailable


def _load_naa() -> object | None:
    """Return NAA segment_token callable, or None if unavailable.

    The analyzer package is bundled at Salehan19-6-67/src/analyzer/ so it is
    always importable when the project's src/ directory is on sys.path.
    """
    global _naa_segment_token
    if _naa_segment_token is not None:
        return _naa_segment_token if _naa_segment_token is not False else None
    try:
        from analyzer.segmentation import segment_token  # type: ignore
        _naa_segment_token = segment_token
        return segment_token
    except ImportError:
        _naa_segment_token = False
        return None


def _get_seg_stem(original_word: str, stripped_stem: str) -> str | None:
    """Extract the bare stem using NAA (primary) or Huda (fallback).

    NAA receives the vocalized original word; its stem output is then
    diacritic-stripped for DB lookups.  Huda receives the already-stripped stem.

    Returns None if no stripping was possible, or if the word is mabni.
    """
    naa = _load_naa()
    if naa is not None:
        try:
            result = naa(original_word)
            naa_stem = _strip(result.get("stem") or "")
            # NAA returns the full word as stem when nothing was stripped;
            # normalise and compare to detect genuine stripping.
            naa_stem_norm = _strip_article(naa_stem)
            if naa_stem_norm and naa_stem_norm != stripped_stem:
                return naa_stem_norm
            # Nothing stripped by NAA; still return the normalised stem so
            # callers can use it uniformly (even if unchanged).
            return naa_stem_norm or None
        except Exception:
            pass  # fall through to Huda

    # Huda fallback
    return _huda_extract_stem(stripped_stem)


# ── Skeleton (Layer 3) ────────────────────────────────────────────────────
def _skeleton_root(original_word: str, stripped_stem: str) -> str | None:
    """Consonant-skeleton root extraction.

    Uses the segmenter (NAA → Huda) to strip affixes, then applies
    morphological rules to extract the trilateral root from what remains.
    """
    seg = _get_seg_stem(original_word, stripped_stem)
    s = seg if seg is not None else stripped_stem

    # Rule 1: strip ta marbuta (always a suffix, never a root letter)
    if s.endswith("ة") and len(s) > 1:
        s = s[:-1]

    # Rule 2: strip accusative alef residue
    if s.endswith("ا") and len(s) > 2:
        s = s[:-1]

    # Rule 3: strip past-tense personal ت
    if s.endswith("ت") and len(s) > 2:
        candidate = s[:-1]
        ends_weak = candidate.endswith("ي") or candidate.endswith("و")
        if ends_weak or len(candidate) >= 2:
            s = candidate

    # Rule 4: consonants (keep و/ي as potential root radicals)
    cons = [c for c in s if c not in _MEDIAL_VOWELS and c not in _SUFFIXES]

    # Rule 5: root length
    if len(cons) >= 3:
        return "".join(cons[:3])
    if len(cons) == 2:
        return cons[0] + "و" + cons[1]   # hollow C-و-C
    return None


# ── DB loaders ────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load():
    mapping: dict[str, str] = {}
    if not _MISHKAT_CSV.exists():
        return mapping
    with open(_MISHKAT_CSV, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            root = row.get("root", "").strip()
            word = row.get("word", "").strip()
            if not root or not word:
                continue
            for key in (_normalize(word), _strip(word)):
                if key and key not in mapping:
                    mapping[key] = root
    return mapping


@lru_cache(maxsize=1)
def _load_audited():
    """Audited verb→root (Lisan al-Arab). Key = stripped+alef-normalised verb form."""
    mapping: dict[str, str] = {}
    if not _AUDITED_CSV.exists():
        return mapping
    with open(_AUDITED_CSV, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            root = row.get("الجذر", "").strip()
            verb = row.get("الفعل الماضي", "").strip()
            if not root or not verb:
                continue
            key = _norm_alef(_strip(verb))
            if key and key not in mapping:
                mapping[key] = root
    return mapping


# ── Public API ────────────────────────────────────────────────────────────
def lookup_root(word: str) -> str | None:
    """General Arabic root extractor — four layers with morphological awareness.

    Returns the trilateral (or quadrilateral) root string, or None if the
    word is a mabni particle or the root cannot be determined.
    """
    stem = _normalize(word)   # diacritics stripped, ال removed

    # ── Mabni guard ──────────────────────────────────────────────────────
    if is_mabni(stem) or is_mabni(_strip(word)):
        return None

    mapping  = _load()
    audited  = _load_audited()

    # ── Layer 1: Mishkat golden set ──────────────────────────────────────
    mishkat_root = mapping.get(stem) or mapping.get(_strip(word))
    if mishkat_root and _root_in_stem(mishkat_root, stem):
        return mishkat_root

    # ── Layer 1b: Audited verb→root (Lisan al-Arab) ──────────────────────
    bare = _norm_alef(_strip(stem))
    audited_root = audited.get(bare) or audited.get(_norm_alef(_strip(word)))
    if audited_root:
        return audited_root

    # ── Layer 1c: Segmenter retry (NAA primary → Huda fallback) ──────────
    # If the caller didn't supply diacritics, try the GPT-52 diacritizer so
    # NAA can use harakat for wazn-validated peels.  If the word already has
    # diacritics (e.g. from a Quranic decoder), skip the extra call.
    word_for_seg = word
    if not _DIACRITICS_RE.search(word):
        vocalized = _diacritize(word)
        if vocalized:
            word_for_seg = vocalized

    seg_stem = _get_seg_stem(word_for_seg, stem)
    if seg_stem and seg_stem != stem:
        mishkat_root = mapping.get(seg_stem)
        if mishkat_root and _root_in_stem(mishkat_root, seg_stem):
            return mishkat_root
        # Only retry audited DB when seg_stem is long enough to be a verb form
        if len(seg_stem) >= 3:
            seg_bare = _norm_alef(seg_stem)
            audited_root = audited.get(seg_bare)
            if audited_root:
                return audited_root

    # ── Layer 2: PatternMatcher ───────────────────────────────────────────
    # Use the ORIGINAL stripped stem (not seg_stem) so ة / مَفْعَل shapes
    # are preserved for pattern recognition.  Only strip past-tense ت,
    # which PatternMatcher cannot distinguish from a root-final ت.
    pm_stem = stem
    if pm_stem.endswith("ت") and len(pm_stem) > 2:
        candidate = pm_stem[:-1]
        ends_weak = candidate.endswith("ي") or candidate.endswith("و")
        if ends_weak or len(candidate) >= 2:
            pm_stem = candidate
    try:
        from mcd.engines.pattern_matcher import PatternMatcher
        match = PatternMatcher().best_match(pm_stem)
        if match and match.get("root") and match.get("certainty", 0) >= 0.45:
            root = match["root"]
            if root.endswith("ة"):
                root = root[:-1]
                if len(root) == 2:
                    root = root[0] + "و" + root[1]
            if root and len(root) >= 2:
                return root
    except Exception:
        pass

    # ── Layer 3: Consonant skeleton ───────────────────────────────────────
    return _skeleton_root(word_for_seg, stem)
