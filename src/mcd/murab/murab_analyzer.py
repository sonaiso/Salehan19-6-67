"""MurabAnalyzer — main entry point for Arabic I'rab analysis.

Tokenizes text, detects harakat/governing factors,
and builds MurabUnit objects for each token.

Example:
    كَتَبَ زَيْدٌ الدَّرْسَ بِالْقَلَمِ
    → [كَتَبَ (verb), زَيْدٌ (فاعل/nominative), الدَّرْسَ (مفعول به/accusative),
       بِالْقَلَمِ (مجرور/genitive)]
"""
from __future__ import annotations

import re
import uuid

from mcd.murab.murab_schema import MurabUnit
from mcd.murab.case_resolver import CaseResolver, _strip_harakat, _HARAKA_TO_CASE
from mcd.murab.syntactic_role_resolver import SyntacticRoleResolver
from mcd.murab.nominative_resolver import NominativeResolver
from mcd.murab.accusative_resolver import AccusativeResolver
from mcd.murab.genitive_resolver import GenitiveResolver
from mcd.murab.jussive_resolver import JussiveResolver
from mcd.murab.governing_factor import GOVERNING_FACTOR_REGISTRY
from mcd.murab.estimated_irab_engine import EstimatedIrabEngine
from mcd.murab.irregular_irab_registry import IRREGULAR_IRAB_REGISTRY
from mcd.murab.murab_certainty_policy import MurabCertaintyPolicy

# Arabic diacritics
_DAMMA   = "\u064f"   # ُ
_FATHA   = "\u064e"   # َ
_KASRA   = "\u0650"   # ِ
_SUKUN   = "\u0652"   # ْ
_HARAKAT = re.compile(r"[\u064b-\u065f]")

# Tokenizer: split on whitespace and Arabic punctuation
_PUNCT = re.compile(r"[\s،,\.؟?!\u060c\u061b\u061f]+")


class MurabAnalyzer:
    """Analyzes Arabic text and returns a list of MurabUnit objects."""

    def __init__(self) -> None:
        self._case_resolver = CaseResolver()
        self._syntactic_resolver = SyntacticRoleResolver()
        self._nom_resolver = NominativeResolver()
        self._acc_resolver = AccusativeResolver()
        self._gen_resolver = GenitiveResolver()
        self._juss_resolver = JussiveResolver()
        self._estimated_engine = EstimatedIrabEngine()
        self._certainty_policy = MurabCertaintyPolicy()

    def analyze(self, text: str) -> list[MurabUnit]:
        tokens = [t for t in _PUNCT.split(text) if t]
        units: list[MurabUnit] = []

        for i, token in enumerate(tokens):
            context_before = tokens[:i]
            unit = self._analyze_token(token, i, context_before, tokens)
            units.append(unit)

        # Second pass: resolve syntactic roles with full context
        for unit in units:
            if unit.word_type not in ("verb", "imperfect_verb"):
                role = self._syntactic_resolver.resolve(unit, units)
                unit.syntactic_role = role

        return units

    # ------------------------------------------------------------------ #
    def _analyze_token(
        self,
        surface: str,
        position: int,
        context_before: list[str],
        all_tokens: list[str],
    ) -> MurabUnit:
        unit_id = str(uuid.uuid4())[:8]
        normalized = _strip_harakat(surface)

        # Detect word type
        word_type = self._detect_word_type_full(surface, normalized, context_before)

        if word_type in ("verb",):
            return MurabUnit(
                unit_id=unit_id,
                surface=surface,
                normalized=normalized,
                token_id=f"tok_{position}",
                word_type=word_type,
                irab_case="indeclinable_local",
                irab_marker="local",
                marker_visibility="local",
                governing_factor_id=None,
                syntactic_role="فعل",
                semantic_role="unknown",
                certainty_policy="certain_syntactic",
            )

        # Resolve case
        irab_case, irab_marker, gf_id, certainty, warnings = (
            self._case_resolver.resolve(surface, context_before)
        )

        # Check estimated marker
        est = self._estimated_engine.resolve(surface, irab_case)
        if est["has_estimated_marker"]:
            irab_marker = "estimated"
            marker_visibility = "estimated"
            warnings.append(f"estimated_marker: {est['reason']}")
        else:
            marker_visibility = "apparent" if irab_marker != "none" else "apparent"

        # Get governing factor object
        gf = GOVERNING_FACTOR_REGISTRY.get(gf_id) if gf_id else None
        gf_type = gf.factor_type if gf else None

        # Resolve semantic role from case
        semantic_role = self._resolve_semantic_role(
            irab_case, gf_type, position, surface
        )

        # Certainty policy
        cp = self._certainty_policy.evaluate(
            MurabUnit(
                unit_id=unit_id,
                surface=surface,
                normalized=normalized,
                token_id=f"tok_{position}",
                word_type=word_type,
                irab_case=irab_case,
                irab_marker=irab_marker,
                marker_visibility=marker_visibility,
                governing_factor_id=gf_id,
                syntactic_role="",
                semantic_role=semantic_role,
                certainty_policy=certainty,
                warnings=warnings,
            ),
            gf,
        )
        warnings.extend(cp["warnings"])

        return MurabUnit(
            unit_id=unit_id,
            surface=surface,
            normalized=normalized,
            token_id=f"tok_{position}",
            word_type=word_type,
            irab_case=irab_case,
            irab_marker=irab_marker,
            marker_visibility=marker_visibility,
            governing_factor_id=gf_id,
            syntactic_role="",  # filled in second pass
            semantic_role=semantic_role,
            certainty_policy=cp["syntactic_certainty"],
            warnings=list(dict.fromkeys(warnings)),  # deduplicate
        )

    def _detect_word_type_full(
        self,
        surface: str,
        normalized: str,
        context: list[str],
    ) -> str:
        # Find the last case-bearing haraka
        last_haraka = None
        for ch in reversed(surface):
            if ch in _HARAKA_TO_CASE:
                last_haraka = ch
                break

        bare_len = len(normalized)
        no_article = not normalized.startswith("ال")

        # Past tense verb: 3 bare letters, no article, ends in fatha (َ)
        if no_article and bare_len == 3 and last_haraka == _FATHA:
            return "verb"

        if normalized and normalized[0] in "يتنأ" and no_article and bare_len >= 3:
            return "imperfect_verb"

        if IRREGULAR_IRAB_REGISTRY.is_irregular(surface):
            if normalized.endswith("ان") or normalized.endswith("ين"):
                return "dual"
            if normalized.endswith("ون"):
                return "sound_plural"
            if normalized.endswith("ات"):
                return "sound_plural"

        return "noun"

    def _resolve_semantic_role(
        self,
        irab_case: str,
        gf_type: str | None,
        position: int,
        surface: str,
    ) -> str:
        if irab_case == "nominative":
            if gf_type == "verb" or position > 0:
                return "agent"
            return "subject"
        if irab_case == "accusative":
            return "patient"
        if irab_case == "genitive":
            if gf_type == "preposition":
                return "possessed"
            return "possessor"
        return "unknown"
