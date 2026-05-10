"""CaseResolver — resolves Arabic I'rab case from surface form and context."""
from __future__ import annotations
from typing import Optional
from mcd.murab.murab_schema import MurabUnit
from mcd.murab.governing_factor import detect_governing_factors

# Arabic diacritics
FATHA = '\u064e'
DAMMA = '\u064f'
KASRA = '\u0650'
SUKUN = '\u0652'
FATHATAN = '\u064b'
DAMMATAN = '\u064c'
KASRATAN = '\u064d'
SHADDA = '\u0651'

DIACRITIC_TO_CASE = {
    DAMMA: ("nominative", "damma"),
    DAMMATAN: ("nominative", "dammatan"),
    FATHA: ("accusative", "fatha"),
    FATHATAN: ("accusative", "fathatan"),
    KASRA: ("genitive", "kasra"),
    KASRATAN: ("genitive", "kasratan"),
    SUKUN: ("jussive", "sukun"),
}


def _strip_diacritics(text: str) -> str:
    diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0653\u0654\u0655\u0670')
    return ''.join(c for c in text if c not in diacritics)


def _detect_last_diacritic(surface: str) -> Optional[tuple]:
    """Return (case, marker) from last diacritic character, or None."""
    for ch in reversed(surface):
        if ch in DIACRITIC_TO_CASE:
            return DIACRITIC_TO_CASE[ch]
        if ch.isalpha():
            break
    return None


class CaseResolver:
    """Resolves Arabic I'rab case for a token given context."""

    def resolve(self, surface: str, token_id: str, context_tokens: list) -> MurabUnit:
        """Resolve I'rab for a surface token in context."""
        normalized = _strip_diacritics(surface)

        # Detect case from diacritics
        diacritic_result = _detect_last_diacritic(surface)

        # Detect governing factors from context
        gov_factors = detect_governing_factors(context_tokens)
        gov_factor_id = gov_factors[0].factor_id if gov_factors else None

        # Determine case
        if diacritic_result:
            irab_case, irab_marker = diacritic_result
            marker_visibility = "apparent"
        else:
            irab_case, irab_marker = self._infer_from_context(surface, normalized, context_tokens)
            marker_visibility = "estimated" if irab_case != "unknown" else "prevented"

        # Resolve roles
        syntactic_role = self._resolve_syntactic_role(irab_case, surface, context_tokens)
        semantic_role = self._resolve_semantic_role(syntactic_role, irab_case)

        # Determine word type
        word_type = self._detect_word_type(surface, normalized)

        # Certainty policy
        if marker_visibility == "apparent" and gov_factor_id:
            certainty_policy = "syntactic_certain"
        elif marker_visibility == "apparent":
            certainty_policy = "syntactic_probable"
        elif marker_visibility == "estimated":
            certainty_policy = "syntactic_hypothesis"
        else:
            certainty_policy = "unknown"

        warnings = []
        if irab_case == "unknown":
            warnings.append("undetermined_case")

        return MurabUnit(
            unit_id=f"murab_{token_id}",
            surface=surface,
            normalized=normalized,
            token_id=token_id,
            word_type=word_type,
            irab_case=irab_case,
            irab_marker=irab_marker,
            marker_visibility=marker_visibility,
            governing_factor_id=gov_factor_id,
            syntactic_role=syntactic_role,
            semantic_role=semantic_role,
            relation_edges=[],
            certainty_policy=certainty_policy,
            warnings=warnings,
            trace_ids=[token_id],
        )

    def _infer_from_context(self, surface: str, normalized: str, context_tokens: list) -> tuple:
        """Infer case from context when no diacritics."""
        idx = None
        for i, tok in enumerate(context_tokens):
            if tok == surface or _strip_diacritics(tok) == normalized:
                idx = i
                break

        if idx is None:
            return ("unknown", "none")

        if idx > 0:
            prev = _strip_diacritics(context_tokens[idx - 1])
            if prev in {"لم", "لما"}:
                return ("jussive", "sukun")
            if prev in {"لن"}:
                return ("accusative", "fatha")
            if prev in {"في", "من", "إلى", "على", "عن"}:
                return ("genitive", "kasra")
            if prev in {"إنّ", "إن", "أنّ", "أن"}:
                return ("accusative", "fatha")

        return ("unknown", "none")

    def _resolve_syntactic_role(self, irab_case: str, surface: str, context_tokens: list) -> str:
        if irab_case == "nominative":
            return "agent"
        elif irab_case == "accusative":
            return "object"
        elif irab_case == "genitive":
            return "object_of_preposition"
        elif irab_case == "jussive":
            return "jussive_verb"
        return "unknown"

    def _resolve_semantic_role(self, syntactic_role: str, irab_case: str) -> str:
        role_map = {
            "agent": "agent",
            "object": "patient",
            "object_of_preposition": "oblique",
            "predicate": "predicate",
            "subject": "subject",
            "jussive_verb": "action",
            "unknown": "unknown",
        }
        return role_map.get(syntactic_role, "unknown")

    def _detect_word_type(self, surface: str, normalized: str) -> str:
        if surface.endswith('\u064f') or surface.endswith('\u064c'):
            return "noun"
        if surface.endswith('\u064e') or surface.endswith('\u064b'):
            return "noun"
        if surface.startswith('يَ') or surface.startswith('تَ') or surface.startswith('أَ') or surface.startswith('نَ'):
            return "imperfect_verb"
        return "noun"
