"""ArabicMorphologyAnalyzer — root extraction, pattern matching, syllabification.

This module provides rule-based Arabic morphological analysis:

1. **Strip diacritics** — normalise the surface form.
2. **Prefix/suffix segmentation** — remove known prefixes and suffixes.
3. **Root candidate extraction** — identify the likely tri-literal root.
4. **Pattern matching** — match the word against known morphological weights (أوزان).
5. **Syllable decomposition** — split into CV/CVC syllables.

All outputs carry certainty scores because morphological analysis is
probabilistic — the same surface form can have multiple analyses.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Diacritics strip helper
# ---------------------------------------------------------------------------

_ARABIC_DIACRITICS_RE = re.compile(
    "[\u064B-\u065F\u0670]"  # harakat and shadda range
)


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritical marks from *text*."""
    return _ARABIC_DIACRITICS_RE.sub("", text)


def normalize_arabic(text: str) -> str:
    """Normalise Arabic script: strip diacritics and unify alef forms."""
    text = strip_diacritics(text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")
    return text


# ---------------------------------------------------------------------------
# Known prefixes and suffixes (ordered longest-first for greedy matching)
# ---------------------------------------------------------------------------

_PREFIXES: List[Tuple[str, str, float]] = [
    # (surface, role_label, certainty)
    ("ال", "definite_article", 0.97),
    ("وال", "conj+article", 0.95),
    ("فال", "conj+article", 0.95),
    ("بال", "prep+article", 0.95),
    ("كال", "prep+article", 0.90),
    ("لل", "prep+article", 0.90),
    ("است", "stem_form_X_prefix", 0.85),
    ("مست", "stem_form_X_prefix", 0.85),
    ("مت", "form_V_VI_prefix", 0.80),
    ("تت", "form_V_VI_prefix", 0.78),
    ("ست", "future_prefix", 0.80),
    ("سي", "future_prefix", 0.75),
    ("وت", "conj+pres_prefix", 0.72),
    ("وي", "conj+pres_prefix", 0.72),
    ("ف", "conj", 0.60),
    ("و", "conj", 0.60),
    ("ب", "prep", 0.65),
    ("ل", "prep", 0.65),
    ("ك", "prep", 0.60),
    ("أ", "hamza_wasl", 0.70),
    ("ا", "hamza_wasl", 0.65),
    ("م", "noun_pattern_prefix", 0.60),
    ("ت", "pres_verb_prefix", 0.60),
    ("ي", "pres_verb_prefix", 0.60),
    ("ن", "pres_verb_prefix", 0.55),
]

_SUFFIXES: List[Tuple[str, str, float]] = [
    ("ات", "plural_fem", 0.90),
    ("ون", "plural_masc_nom", 0.92),
    ("ين", "plural_masc_acc_gen", 0.92),
    ("ان", "dual_nom", 0.88),
    ("ين", "dual_acc_gen", 0.88),
    ("ته", "verb_3ms_suffix", 0.75),
    ("تها", "verb_3fs_suffix", 0.75),
    ("وا", "verb_3mpl_suffix", 0.82),
    ("تم", "verb_2mpl_suffix", 0.85),
    ("نا", "verb_1pl_suffix", 0.85),
    ("ني", "verb_1sg_object", 0.80),
    ("هم", "3mpl_pronoun", 0.88),
    ("هن", "3fpl_pronoun", 0.88),
    ("ها", "3fs_pronoun", 0.85),
    ("ه", "3ms_pronoun", 0.75),
    ("ك", "2sg_pronoun", 0.75),
    ("ي", "1sg_pronoun", 0.70),
    ("ة", "fem_marker", 0.90),
    ("ى", "alef_maqsura", 0.70),
    ("ا", "alef_extension", 0.60),
    ("ن", "tanwin_light", 0.55),
]


# ---------------------------------------------------------------------------
# Known morphological patterns (أوزان)
# ---------------------------------------------------------------------------

# Pattern: abstract root template using ف ع ل notation mapped to slot lengths
# Stored as (pattern_label, root_consonants, description, certainty)
_PATTERNS: List[Tuple[str, str, str, float]] = [
    # Verb patterns (أفعال)
    ("فَعَلَ",   "فعل", "past_verb_form_I",           0.88),
    ("فَعِلَ",   "فعل", "past_verb_form_I_kasra",     0.85),
    ("فَعُلَ",   "فعل", "past_verb_form_I_damma",     0.85),
    ("فَعَّلَ",  "فعل", "past_verb_form_II",           0.90),
    ("فَاعَلَ",  "فاعل","past_verb_form_III",          0.88),
    ("أَفْعَلَ", "افعل","past_verb_form_IV",           0.87),
    ("تَفَعَّلَ","تفعل","past_verb_form_V",            0.88),
    ("تَفَاعَلَ","تفاعل","past_verb_form_VI",          0.87),
    ("اِنْفَعَلَ","انفعل","past_verb_form_VII",        0.87),
    ("اِفْتَعَلَ","افتعل","past_verb_form_VIII",       0.88),
    ("اِفْعَلَّ","افعل","past_verb_form_IX",           0.82),
    ("اِسْتَفْعَلَ","استفعل","past_verb_form_X",      0.90),
    # Noun patterns (أسماء)
    ("فَاعِل",  "فاعل",  "ism_fail_agent_noun",       0.90),
    ("مَفْعُول","مفعول", "ism_mafool_patient_noun",   0.92),
    ("فَعَّال", "فعال",  "ism_mubalaghah",            0.88),
    ("فَعِيل",  "فعيل",  "sifah_mushabahah",          0.86),
    ("مَفْعَل", "مفعل",  "ism_makan_zaman",           0.85),
    ("مَفْعَلَة","مفعلة","ism_makan_taa",             0.87),
    ("فُعَّال", "فعال",  "jam_takseer_1",             0.80),
    ("فِعَال",  "فعال",  "jam_takseer_2",             0.78),
    ("أَفْعَال","افعال", "jam_takseer_3",             0.82),
    ("فُعُول",  "فعول",  "jam_takseer_4",             0.78),
    ("فَعْل",   "فعل",   "masdar_I",                  0.75),
    ("فُعُولَة","فعولة", "masdar_sifa",               0.78),
    ("تَفْعِيل","تفعيل", "masdar_form_II",            0.88),
    ("إِفْعَال","افعال", "masdar_form_IV",            0.87),
    ("اِسْتِفْعَال","استفعال","masdar_form_X",        0.90),
]


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MorphSegmentation:
    """Segmentation of a word into prefix, stem, and suffix."""
    surface: str
    prefix: str = ""
    prefix_role: str = ""
    stem: str = ""
    suffix: str = ""
    suffix_role: str = ""
    certainty: float = 0.0


@dataclass
class RootCandidate:
    """A probable root extracted from a stem."""
    root: str               # e.g. "كتب"
    letters: List[str] = field(default_factory=list)   # e.g. ["ك", "ت", "ب"]
    certainty: float = 0.0
    notes: str = ""


@dataclass
class PatternMatch:
    """A matched morphological pattern for a word."""
    pattern_label: str          # e.g. "فَاعِل"
    description: str            # e.g. "agent_noun"
    certainty: float = 0.0


@dataclass
class MorphAnalysis:
    """Full morphological analysis of one word."""
    surface: str
    normalized: str
    segmentation: Optional[MorphSegmentation] = None
    root_candidates: List[RootCandidate] = field(default_factory=list)
    pattern_matches: List[PatternMatch] = field(default_factory=list)
    syllables: List[str] = field(default_factory=list)
    best_root: Optional[str] = None
    best_pattern: Optional[str] = None
    morphological_certainty: float = 0.0


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class ArabicMorphologyAnalyzer:
    """Rule-based Arabic morphological analyzer.

    Usage::

        ana = ArabicMorphologyAnalyzer()
        result = ana.analyze("مكتوب")
        print(result.best_root)    # → كتب
        print(result.best_pattern) # → مَفْعُول
    """

    def analyze(self, word: str) -> MorphAnalysis:
        """Return a full :class:`MorphAnalysis` for *word*."""
        normalized = normalize_arabic(strip_diacritics(word))
        seg = self._segment(normalized)
        stem = seg.stem or normalized

        root_candidates = self._extract_roots(stem)
        # Pattern matching uses the full normalized word (the م in مكتوب is part
        # of the مفعول pattern, not a separable prefix for this purpose).
        pattern_matches = self._match_patterns(normalized)
        syllables = self._syllabify(word)

        best_root = root_candidates[0].root if root_candidates else None
        best_pattern = pattern_matches[0].pattern_label if pattern_matches else None

        morph_cert = 0.0
        if root_candidates:
            morph_cert = max(morph_cert, root_candidates[0].certainty)
        if pattern_matches:
            morph_cert = max(morph_cert, pattern_matches[0].certainty * 0.8)

        return MorphAnalysis(
            surface=word,
            normalized=normalized,
            segmentation=seg,
            root_candidates=root_candidates,
            pattern_matches=pattern_matches,
            syllables=syllables,
            best_root=best_root,
            best_pattern=best_pattern,
            morphological_certainty=round(morph_cert, 4),
        )

    def analyze_sentence(self, sentence: str) -> List[MorphAnalysis]:
        """Analyse each word token in *sentence* and return analyses."""
        tokens = sentence.split()
        return [self.analyze(tok) for tok in tokens]

    # ------------------------------------------------------------------
    # Prefix/suffix segmentation
    # ------------------------------------------------------------------

    def _segment(self, normalized: str) -> MorphSegmentation:
        seg = MorphSegmentation(surface=normalized)

        # Try to strip a prefix (longest match first).
        # For single-char prefixes: require ≥ 4 remaining chars (prevents
        # mis-stripping root radicals like ك in كاتب).
        # For multi-char prefixes: require ≥ 3 remaining chars.
        for prefix, role, cert in _PREFIXES:
            pfx_norm = normalize_arabic(prefix)
            pfx_len = len(pfx_norm)
            min_remaining = 4 if pfx_len == 1 else 3
            if normalized.startswith(pfx_norm) and (len(normalized) - pfx_len) >= min_remaining:
                seg.prefix = prefix
                seg.prefix_role = role
                normalized = normalized[len(pfx_norm):]
                seg.certainty = cert
                break

        # Try to strip a suffix (longest match first)
        for suffix, role, cert in _SUFFIXES:
            sfx_norm = normalize_arabic(suffix)
            if normalized.endswith(sfx_norm) and len(normalized) > len(sfx_norm) + 1:
                seg.suffix = suffix
                seg.suffix_role = role
                normalized = normalized[: -len(sfx_norm)]
                seg.certainty = min(seg.certainty or cert, cert)
                break

        seg.stem = normalized
        return seg

    # ------------------------------------------------------------------
    # Root extraction
    # ------------------------------------------------------------------

    def _extract_roots(self, stem: str) -> List[RootCandidate]:
        """Heuristic tri-literal root extraction from a stemmed form."""
        candidates: List[RootCandidate] = []

        # Remove long vowels (ا و ي) that are likely pattern insertions
        consonants = [c for c in stem if c not in "اوي"]

        if len(consonants) == 3:
            root = "".join(consonants)
            candidates.append(RootCandidate(
                root=root,
                letters=list(root),
                certainty=0.82,
                notes="direct_triliteral",
            ))
        elif len(consonants) == 4:
            # Quadri-literal or first consonant is an added letter
            root4 = "".join(consonants)
            candidates.append(RootCandidate(
                root=root4,
                letters=list(root4),
                certainty=0.70,
                notes="quadriliteral_candidate",
            ))
            # Also try dropping first consonant if it matches common prefixes
            if consonants[0] in "متنا":
                root3 = "".join(consonants[1:])
                candidates.append(RootCandidate(
                    root=root3,
                    letters=list(root3),
                    certainty=0.65,
                    notes="triliteral_minus_prefix",
                ))
        elif len(consonants) >= 5:
            # Take last three as most likely root (rough heuristic)
            root = "".join(consonants[-3:])
            candidates.append(RootCandidate(
                root=root,
                letters=list(root),
                certainty=0.55,
                notes="last_three_consonants",
            ))

        return candidates

    # ------------------------------------------------------------------
    # Pattern matching
    # ------------------------------------------------------------------

    def _match_patterns(self, normalized: str) -> List[PatternMatch]:
        """Match *normalized* word against the known pattern list."""
        matches: List[PatternMatch] = []

        # Map each pattern to its abstract skeleton using radical slots
        for pat_label, _pat_scheme, description, cert in _PATTERNS:
            if self._fits_pattern(normalized, pat_label):
                matches.append(PatternMatch(
                    pattern_label=pat_label,
                    description=description,
                    certainty=cert,
                ))

        # Sort by certainty descending
        matches.sort(key=lambda x: x.certainty, reverse=True)
        return matches

    def _fits_pattern(self, word: str, pattern: str) -> bool:
        """Structural check: does *word* fit the syllable shape of *pattern*?

        The approach:
        1. Compare stripped lengths — both word and pattern (after stripping
           diacritics) should have the same character count.
        2. Check structural markers (common prefix letters م، ت، است…).
        """
        word_stripped = strip_diacritics(word)
        pat_stripped = strip_diacritics(pattern)

        # Primary criterion: same character count
        if len(word_stripped) != len(pat_stripped):
            return False

        # Secondary criterion: structural prefix/suffix markers
        pat_norm = normalize_arabic(pat_stripped)
        word_norm = normalize_arabic(word_stripped)

        # If pattern starts with a fixed letter, word must too
        for marker in ("است", "مت", "ست", "سي", "ان", "ات"):
            if pat_norm.startswith(marker):
                return word_norm.startswith(marker)

        for marker in ("م", "ت"):
            if pat_norm.startswith(marker):
                if not word_norm.startswith(marker):
                    return False

        return True

    # ------------------------------------------------------------------
    # Syllabification
    # ------------------------------------------------------------------

    def _syllabify(self, word: str) -> List[str]:
        """Very simple syllable splitter for Arabic (CV / CVC model)."""
        # Remove diacritics for letter-counting purposes
        stripped = strip_diacritics(word)
        syllables = []
        i = 0
        while i < len(stripped):
            ch = stripped[i]
            if ch in "اوي":
                if syllables:
                    syllables[-1] += ch
                else:
                    syllables.append(ch)
                i += 1
            else:
                syl = ch
                i += 1
                if i < len(stripped) and stripped[i] in "اوي":
                    syl += stripped[i]
                    i += 1
                syllables.append(syl)
        return syllables or [word]
