"""UnicodeAtomicEncoder — Φ: UnicodeSymbol → AtomicFeatureVector.

This module implements the first step of the fractal cognitive pipeline.
Every Arabic character (letter, diacritic, digit, punctuation) is mapped
to a structured feature dictionary that captures:

* Orthographic class (consonant, short_vowel, long_vowel, shadda, tanwin …)
* Phonetic features (place of articulation, manner, voicing)
* Orthographic connectivity (joins left/right)
* Morphological potential scores (root radical, prefix, suffix, weak letter)
* Baseline certainty

No semantic meaning is assigned at this level — the character is a
**digital seed** (ذرة رقمية) from which higher-level roles and meanings
are composed fractally.
"""

from __future__ import annotations

import unicodedata
from typing import Any, Dict

from bayani.cognitive.knowledge_node import CertaintyInfo, KnowledgeNode, NodeLevel


# ---------------------------------------------------------------------------
# Arabic Unicode ranges
# ---------------------------------------------------------------------------

# Basic Arabic block U+0600–U+06FF
_ARABIC_LETTERS = set(chr(c) for c in range(0x0621, 0x063B))  # main consonants
_ARABIC_LETTERS |= set(chr(c) for c in range(0x0641, 0x064B))  # additional
_ARABIC_LETTERS.update("أإآةى")

# Harakat / diacritics
_DIACRITICS: Dict[str, str] = {
    "\u064E": "fatha",       # َ
    "\u064F": "damma",       # ُ
    "\u0650": "kasra",       # ِ
    "\u064B": "fathatan",    # ً
    "\u064C": "dammatan",    # ٌ
    "\u064D": "kasratan",    # ٍ
    "\u0651": "shadda",      # ّ
    "\u0652": "sukun",       # ْ
    "\u0653": "maddah",      # ٓ
    "\u0670": "superscript_alef",
}

# Long vowels
_LONG_VOWELS = {"ا", "و", "ي"}

# Sun letters (الحروف الشمسية) — the article ال assimilates into them
_SUN_LETTERS = set("تثدذرزسشصضطظلن")

# Weak letters (حروف العلة)
_WEAK_LETTERS = set("واي")

# Disconnected letters (لا يتصل بما بعده)
_NON_JOINING = set("ادذرزوأإآة")

# ---------------------------------------------------------------------------
# Phonetic feature tables
# ---------------------------------------------------------------------------

_PHONETIC: Dict[str, Dict[str, str]] = {
    "ب": {"place": "bilabial",      "manner": "stop",        "voicing": "voiced"},
    "ت": {"place": "dental",        "manner": "stop",        "voicing": "voiceless"},
    "ث": {"place": "dental",        "manner": "fricative",   "voicing": "voiceless"},
    "ج": {"place": "palatal",       "manner": "affricate",   "voicing": "voiced"},
    "ح": {"place": "pharyngeal",    "manner": "fricative",   "voicing": "voiceless"},
    "خ": {"place": "velar",         "manner": "fricative",   "voicing": "voiceless"},
    "د": {"place": "dental",        "manner": "stop",        "voicing": "voiced"},
    "ذ": {"place": "dental",        "manner": "fricative",   "voicing": "voiced"},
    "ر": {"place": "alveolar",      "manner": "trill",       "voicing": "voiced"},
    "ز": {"place": "alveolar",      "manner": "fricative",   "voicing": "voiced"},
    "س": {"place": "alveolar",      "manner": "fricative",   "voicing": "voiceless"},
    "ش": {"place": "palato-alveolar","manner": "fricative",  "voicing": "voiceless"},
    "ص": {"place": "alveolar",      "manner": "fricative",   "voicing": "voiceless", "emphatic": True},
    "ض": {"place": "dental",        "manner": "stop",        "voicing": "voiced",    "emphatic": True},
    "ط": {"place": "dental",        "manner": "stop",        "voicing": "voiceless", "emphatic": True},
    "ظ": {"place": "dental",        "manner": "fricative",   "voicing": "voiced",    "emphatic": True},
    "ع": {"place": "pharyngeal",    "manner": "fricative",   "voicing": "voiced"},
    "غ": {"place": "uvular",        "manner": "fricative",   "voicing": "voiced"},
    "ف": {"place": "labiodental",   "manner": "fricative",   "voicing": "voiceless"},
    "ق": {"place": "uvular",        "manner": "stop",        "voicing": "voiceless"},
    "ك": {"place": "velar",         "manner": "stop",        "voicing": "voiceless"},
    "ل": {"place": "alveolar",      "manner": "lateral",     "voicing": "voiced"},
    "م": {"place": "bilabial",      "manner": "nasal",       "voicing": "voiced"},
    "ن": {"place": "alveolar",      "manner": "nasal",       "voicing": "voiced"},
    "ه": {"place": "glottal",       "manner": "fricative",   "voicing": "voiceless"},
    "و": {"place": "bilabial",      "manner": "approximant", "voicing": "voiced"},
    "ي": {"place": "palatal",       "manner": "approximant", "voicing": "voiced"},
    "ا": {"place": "pharyngeal",    "manner": "vowel",       "voicing": "voiced"},
    "أ": {"place": "glottal",       "manner": "stop",        "voicing": "voiceless"},
    "إ": {"place": "glottal",       "manner": "stop",        "voicing": "voiceless"},
    "آ": {"place": "pharyngeal",    "manner": "vowel_long",  "voicing": "voiced"},
    "ة": {"place": "dental",        "manner": "stop",        "voicing": "voiceless", "taa_marbuta": True},
    "ى": {"place": "pharyngeal",    "manner": "vowel",       "voicing": "voiced",    "alef_maqsura": True},
    "ء": {"place": "glottal",       "manner": "stop",        "voicing": "voiceless"},
    "ئ": {"place": "glottal",       "manner": "stop",        "voicing": "voiceless"},
    "ؤ": {"place": "glottal",       "manner": "stop",        "voicing": "voiceless"},
}

# ---------------------------------------------------------------------------
# Morphological potential scores per letter
# ---------------------------------------------------------------------------

# root_candidate: how likely is this letter to be a root radical?
# prefix_candidate: how likely to function as a derivational/inflectional prefix?
# suffix_candidate: how likely to function as a suffix?
# weak_letter: is it an illat letter?

_MORPH_POTENTIAL: Dict[str, Dict[str, float]] = {
    # High root, low prefix
    "ب": {"root_candidate": 0.92, "prefix_candidate": 0.10, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ت": {"root_candidate": 0.70, "prefix_candidate": 0.55, "suffix_candidate": 0.40, "weak_letter": 0.00},
    "ث": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ج": {"root_candidate": 0.92, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ح": {"root_candidate": 0.92, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "خ": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "د": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ذ": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ر": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ز": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "س": {"root_candidate": 0.88, "prefix_candidate": 0.20, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ش": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ص": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ض": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ط": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ظ": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ع": {"root_candidate": 0.92, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "غ": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ف": {"root_candidate": 0.90, "prefix_candidate": 0.10, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ق": {"root_candidate": 0.90, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.00},
    "ك": {"root_candidate": 0.88, "prefix_candidate": 0.25, "suffix_candidate": 0.20, "weak_letter": 0.00},
    "ل": {"root_candidate": 0.80, "prefix_candidate": 0.50, "suffix_candidate": 0.15, "weak_letter": 0.00},
    "م": {"root_candidate": 0.65, "prefix_candidate": 0.75, "suffix_candidate": 0.15, "weak_letter": 0.00},
    "ن": {"root_candidate": 0.78, "prefix_candidate": 0.40, "suffix_candidate": 0.50, "weak_letter": 0.00},
    "ه": {"root_candidate": 0.80, "prefix_candidate": 0.20, "suffix_candidate": 0.60, "weak_letter": 0.00},
    "و": {"root_candidate": 0.55, "prefix_candidate": 0.60, "suffix_candidate": 0.40, "weak_letter": 0.85},
    "ي": {"root_candidate": 0.55, "prefix_candidate": 0.45, "suffix_candidate": 0.50, "weak_letter": 0.85},
    "ا": {"root_candidate": 0.30, "prefix_candidate": 0.20, "suffix_candidate": 0.30, "weak_letter": 0.75},
    "أ": {"root_candidate": 0.30, "prefix_candidate": 0.15, "suffix_candidate": 0.10, "weak_letter": 0.60},
    "إ": {"root_candidate": 0.25, "prefix_candidate": 0.10, "suffix_candidate": 0.05, "weak_letter": 0.60},
    "آ": {"root_candidate": 0.25, "prefix_candidate": 0.10, "suffix_candidate": 0.05, "weak_letter": 0.70},
    "ة": {"root_candidate": 0.15, "prefix_candidate": 0.05, "suffix_candidate": 0.90, "weak_letter": 0.00},
    "ى": {"root_candidate": 0.25, "prefix_candidate": 0.05, "suffix_candidate": 0.70, "weak_letter": 0.65},
    "ء": {"root_candidate": 0.50, "prefix_candidate": 0.05, "suffix_candidate": 0.05, "weak_letter": 0.40},
}

_DEFAULT_MORPH = {"root_candidate": 0.50, "prefix_candidate": 0.10, "suffix_candidate": 0.10, "weak_letter": 0.00}


# ---------------------------------------------------------------------------
# Main encoder class
# ---------------------------------------------------------------------------

class UnicodeAtomicEncoder:
    """Encode a single Unicode symbol into an atomic feature dictionary.

    Usage::

        enc = UnicodeAtomicEncoder()
        features = enc.encode("ك")
        node = enc.to_node("ك", node_id="N-001")
    """

    # ------------------------------------------------------------------
    # Symbol-class detection
    # ------------------------------------------------------------------

    @staticmethod
    def _symbol_class(symbol: str) -> str:
        if symbol in _DIACRITICS:
            name = _DIACRITICS[symbol]
            return "shadda" if name == "shadda" else "diacritic"
        if symbol in _LONG_VOWELS:
            return "long_vowel"
        if symbol in _ARABIC_LETTERS or symbol in {"ة", "ى", "ء", "ئ", "ؤ"}:
            return "consonant"
        cp = ord(symbol)
        if 0x0030 <= cp <= 0x0039 or 0x0660 <= cp <= 0x0669:
            return "digit"
        if unicodedata.category(symbol).startswith("P"):
            return "punctuation"
        return "other"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, symbol: str) -> Dict[str, Any]:
        """Return the atomic feature dictionary for *symbol*."""
        sym_class = self._symbol_class(symbol)
        cp = ord(symbol)

        features: Dict[str, Any] = {
            "symbol": symbol,
            "unicode": f"U+{cp:04X}",
            "class": sym_class,
            "script": "arabic" if 0x0600 <= cp <= 0x06FF else "other",
            "semantic_status": "no_direct_meaning",
            "certainty": 1.0,  # orthographic certainty: we know exactly what symbol this is
        }

        # Diacritic-specific features
        if sym_class in ("diacritic", "shadda"):
            diac_name = _DIACRITICS.get(symbol, "unknown")
            features["diacritic_name"] = diac_name
            features["phonological_role"] = self._diacritic_phonological_role(symbol)
            features["morphological_potential"] = self._diacritic_morph_potential(symbol)
            return features

        # Consonant / long-vowel features
        phonetic = _PHONETIC.get(symbol, {})
        features["phonetic"] = phonetic

        connects_right = symbol not in _NON_JOINING
        features["orthographic"] = {
            "connects_right": connects_right,
            "connects_left": True,
            "sun_letter": symbol in _SUN_LETTERS,
            "weak_letter": symbol in _WEAK_LETTERS,
        }

        morph = _MORPH_POTENTIAL.get(symbol, _DEFAULT_MORPH)
        features["morphological_potential"] = morph

        return features

    def to_node(self, symbol: str, node_id: str = "") -> KnowledgeNode:
        """Return a :class:`KnowledgeNode` at ``NodeLevel.ATOM`` for *symbol*."""
        features = self.encode(symbol)
        return KnowledgeNode(
            node_id=node_id or f"atom-{ord(symbol):04X}",
            level=NodeLevel.ATOM,
            surface=symbol,
            features=features,
            certainty=CertaintyInfo(
                score=1.0,
                evidence_type="orthographic",
                status="certain",
            ),
            metadata={"unicode_codepoint": ord(symbol)},
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _diacritic_phonological_role(symbol: str) -> Dict[str, float]:
        roles = {
            "\u064E": {"opens_syllable": 0.90, "marks_case_or_pattern": 0.70},
            "\u064F": {"opens_syllable": 0.75, "marks_case_or_pattern": 0.80},
            "\u0650": {"opens_syllable": 0.70, "marks_case_or_pattern": 0.80},
            "\u064B": {"opens_syllable": 0.85, "tanwin": 0.90, "accusative_marker": 0.70},
            "\u064C": {"opens_syllable": 0.75, "tanwin": 0.90, "nominative_marker": 0.70},
            "\u064D": {"opens_syllable": 0.70, "tanwin": 0.90, "genitive_marker": 0.70},
            "\u0651": {"opens_syllable": 0.00, "gemination_marker": 0.98},
            "\u0652": {"closes_syllable": 0.90, "sukun_marker": 0.98},
        }
        return roles.get(symbol, {})

    @staticmethod
    def _diacritic_morph_potential(symbol: str) -> Dict[str, float]:
        potentials = {
            "\u064E": {"past_verb_pattern_marker": 0.75, "accusative_marker": 0.50},
            "\u064F": {"nominative_marker": 0.65, "present_verb_marker": 0.55},
            "\u0650": {"genitive_marker": 0.70, "jussive_marker": 0.40},
            "\u064B": {"indefinite_accusative": 0.85},
            "\u064C": {"indefinite_nominative": 0.85},
            "\u064D": {"indefinite_genitive": 0.85},
            "\u0651": {"doubled_root_radical": 0.80, "pattern_intensifier": 0.70},
            "\u0652": {"consonant_final": 0.85},
        }
        return potentials.get(symbol, {})
