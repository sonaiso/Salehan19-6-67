"""RoleVectorizer — Ρ: AtomicFeatureVector × Context → RoleVector.

A character's morphological role cannot be determined from its features
alone; it depends on its **position** within the word, the surrounding
diacritics, the word's pattern, and the broader syntactic context.

This module infers a probability distribution over morphological roles for
each atomic symbol, given its feature vector and its position in context.

Roles modelled
--------------
root_radical          — جذري
prefix_derivational   — سابقة اشتقاقية (like م in مكتبة)
prefix_inflectional   — سابقة صرفية (like ي/ت/ن/أ in المضارع)
suffix_inflectional   — لاحقة صرفية (like ون/ان/ات)
suffix_case           — علامة إعراب
conjunction           — حرف عطف
preposition           — حرف جر
article               — أداة تعريف (ال)
interrogative         — أداة استفهام
weak_radical          — حرف علة جذري
long_vowel_extension  — مد
tanwin_marker         — تنوين
"""

from __future__ import annotations

from typing import Any, Dict, List

from bayani.cognitive.knowledge_node import KnowledgeNode, NodeLevel, CertaintyInfo


_ROLE_NAMES = [
    "root_radical",
    "prefix_derivational",
    "prefix_inflectional",
    "suffix_inflectional",
    "suffix_case",
    "conjunction",
    "preposition",
    "article",
    "interrogative",
    "weak_radical",
    "long_vowel_extension",
    "tanwin_marker",
]

# One-letter Arabic particles with fixed roles
_FIXED_PARTICLES: Dict[str, str] = {
    "و": "conjunction",    # when standalone word
    "ف": "conjunction",
    "ب": "preposition",
    "ل": "preposition",
    "ك": "preposition",   # ك التشبيه
    "أ": "interrogative",  # همزة الاستفهام
}

# Common prefixes that modify role probabilities when at word-start
_PREFIX_SIGNALS = {"م", "ت", "ي", "ن", "أ", "ا", "ست", "مت", "مس"}

# Common suffixes
_SUFFIX_SIGNALS = {"ة", "ات", "ون", "ين", "ان", "وا", "ي", "ها", "ه", "هم", "هن", "نا", "تم"}


class RoleVectorizer:
    """Infer role probability distributions for atom nodes in context.

    Usage::

        rv = RoleVectorizer()
        atoms = [...]   # list of KnowledgeNode at NodeLevel.ATOM
        rv.assign_roles(atoms, word_surface="مكتوب", position_in_sentence=3)
    """

    def assign_roles(
        self,
        atoms: List[KnowledgeNode],
        word_surface: str = "",
        position_in_sentence: int = 0,
        preceding_diacritics: str = "",
        is_standalone_particle: bool = False,
    ) -> List[KnowledgeNode]:
        """Assign role vectors to each atom node in *atoms* in-place.

        Parameters
        ----------
        atoms:
            List of atom-level :class:`KnowledgeNode` objects for one word.
        word_surface:
            Full stripped surface form of the word (no diacritics).
        position_in_sentence:
            0-indexed position of the word in the sentence.
        preceding_diacritics:
            Concatenated diacritics found on preceding characters.
        is_standalone_particle:
            True when the word is a single-character particle (و، ف، ب …).
        """
        n = len(atoms)
        for i, node in enumerate(atoms):
            if node.level != NodeLevel.ATOM:
                continue

            sym = node.surface
            features = node.features
            sym_class = features.get("class", "other")

            role_vec = self._base_role_from_class(sym, sym_class, features)
            role_vec = self._adjust_for_position(
                role_vec, sym, i, n, word_surface, is_standalone_particle
            )
            role_vec = self._adjust_for_diacritics(
                role_vec, sym, sym_class, preceding_diacritics
            )

            # Normalise so values stay in [0, 1] (they are probabilities)
            role_vec = {k: round(min(1.0, max(0.0, v)), 4) for k, v in role_vec.items()}

            node.role_vector = role_vec

            # Update certainty: role inference is morphological, lower than orthographic
            node.certainty = CertaintyInfo(
                score=0.70,
                evidence_type="morphological",
                status="probable",
            )

        return atoms

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _base_role_from_class(
        self, sym: str, sym_class: str, features: Dict[str, Any]
    ) -> Dict[str, float]:
        """Build initial role vector from character class and morph potential."""
        rv: Dict[str, float] = {r: 0.0 for r in _ROLE_NAMES}

        if sym_class == "diacritic":
            diac_name = features.get("diacritic_name", "")
            if diac_name in ("fathatan", "dammatan", "kasratan"):
                rv["tanwin_marker"] = 0.95
            elif diac_name == "shadda":
                rv["root_radical"] = 0.50
                rv["prefix_derivational"] = 0.20
            return rv

        if sym_class == "shadda":
            rv["root_radical"] = 0.50
            rv["prefix_derivational"] = 0.20
            return rv

        morph = features.get("morphological_potential", {})
        rv["root_radical"] = morph.get("root_candidate", 0.50)
        rv["prefix_derivational"] = morph.get("prefix_candidate", 0.10)
        rv["prefix_inflectional"] = morph.get("prefix_candidate", 0.10) * 0.6
        rv["suffix_inflectional"] = morph.get("suffix_candidate", 0.10)
        rv["weak_radical"] = morph.get("weak_letter", 0.00)
        rv["long_vowel_extension"] = morph.get("weak_letter", 0.00) * 0.50

        # Taa marbuta is almost always a suffix
        if features.get("phonetic", {}).get("taa_marbuta"):
            rv["suffix_inflectional"] = 0.95
            rv["root_radical"] = 0.05

        return rv

    def _adjust_for_position(
        self,
        rv: Dict[str, float],
        sym: str,
        index: int,
        total: int,
        word_surface: str,
        is_standalone: bool,
    ) -> Dict[str, float]:
        """Adjust role probabilities based on character position in word."""
        if is_standalone and sym in _FIXED_PARTICLES:
            fixed_role = _FIXED_PARTICLES[sym]
            rv = {r: 0.0 for r in _ROLE_NAMES}
            rv[fixed_role] = 0.95
            return rv

        # First character of a multi-char word
        if index == 0 and total > 1:
            if sym == "ا" and total >= 2:
                rv["article"] = 0.55  # ال التعريف
            elif sym in _PREFIX_SIGNALS:
                rv["prefix_derivational"] = min(1.0, rv.get("prefix_derivational", 0) + 0.25)
                rv["prefix_inflectional"] = min(1.0, rv.get("prefix_inflectional", 0) + 0.20)
                rv["root_radical"] = max(0.0, rv.get("root_radical", 0) - 0.25)

        # Last character
        if index == total - 1 and total > 1:
            if sym in {"ة", "ى"}:
                rv["suffix_inflectional"] = 0.95
                rv["root_radical"] = 0.05
            elif sym == "ن" and total >= 3:
                rv["suffix_inflectional"] = min(1.0, rv.get("suffix_inflectional", 0) + 0.30)

        # Middle: higher root probability
        if 0 < index < total - 1:
            rv["root_radical"] = min(1.0, rv.get("root_radical", 0) + 0.10)

        return rv

    def _adjust_for_diacritics(
        self,
        rv: Dict[str, float],
        sym: str,
        sym_class: str,
        preceding_diacritics: str,
    ) -> Dict[str, float]:
        """Adjust role probabilities based on surrounding diacritics."""
        if not preceding_diacritics:
            return rv

        # ّ (shadda) on a letter often signals a doubled root radical
        if "\u0651" in preceding_diacritics:
            rv["root_radical"] = min(1.0, rv.get("root_radical", 0) + 0.20)

        # Tanwin signals end of a definite-lacking nominal
        if any(d in preceding_diacritics for d in "\u064B\u064C\u064D"):
            rv["suffix_case"] = min(1.0, rv.get("suffix_case", 0) + 0.40)

        return rv
