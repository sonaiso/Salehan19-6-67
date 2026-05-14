"""MorphosemanticTraceLinker — links Unicode traces to ConceptCenter via morphology.

This linker builds the full chain:
  UnicodeTrace → TokenTrace → RootCandidate → PatternCandidate
  → FoldedWordGraph → ConceptCenter

It provides a single `link(word)` call that produces a structured trace
bundle connecting all levels.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.folded_word_graph import FoldedWordGraph, build_folded_word_graph
from mcd.morphosemantics.concept_center import ConceptCenter
from mcd.morphosemantics.concept_center_mapper import ConceptCenterMapper
from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
from mcd.morphosemantics.root_ontology import load_root_ontology
from mcd.morphosemantics.morphophonological_normalizer import MorphophonologicalNormalizer


@dataclass
class MorphosemanticTraceBundle:
    trace_id: str
    word: str
    normalized_word: str
    token_trace: dict
    root_candidates: list[dict]
    pattern_candidates: list[dict]
    folded_word_graph: FoldedWordGraph
    concept_center: ConceptCenter
    link_depth: int  # how many levels were successfully linked

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "word": self.word,
            "normalized_word": self.normalized_word,
            "token_trace": self.token_trace,
            "root_candidates": self.root_candidates,
            "pattern_candidates": self.pattern_candidates,
            "folded_word_graph": self.folded_word_graph.to_dict(),
            "concept_center": self.concept_center.to_dict(),
            "link_depth": self.link_depth,
        }


# Built-in word → (root_id, pattern_id) lookup for known words
_KNOWN_WORDS: dict[str, tuple[str, str]] = {
    "كاتِب": ("ktb", "faail"),
    "كاتب": ("ktb", "faail"),
    "مَكتوب": ("ktb", "mafuul"),
    "مكتوب": ("ktb", "mafuul"),
    "مَكتَب": ("ktb", "mafal_place"),
    "مكتب": ("ktb", "mafal_place"),
    "مَكتَبة": ("ktb", "mafala_place"),
    "مكتبة": ("ktb", "mafala_place"),
    "كُتُب": ("ktb", "fuuul_plural"),
    "كتب": ("ktb", "fuuul_plural"),
    "كِتاب": ("ktb", "faiil_attr"),
    "كِتابة": ("ktb", "fiaala_masdar_craft"),
    "كتابة": ("ktb", "fiaala_masdar_craft"),
    "كُتَيِّب": ("ktb", "fuayyil_dim"),
    "كتيب": ("ktb", "fuayyil_dim"),
    "عالِم": ("alm", "faail"),
    "عالم": ("alm", "faail"),
    "مَعلوم": ("alm", "mafuul"),
    "معلوم": ("alm", "mafuul"),
    "عِلم": ("alm", "fiaala_masdar_craft"),
    "علم": ("alm", "fiaala_masdar_craft"),
    "زِراعة": ("zraa", "fiaala_masdar_craft"),
    "زراعة": ("zraa", "fiaala_masdar_craft"),
    "مُزارِع": ("zraa", "mufaail_agent"),
    "مزارع": ("zraa", "mufaail_agent"),
    "استَخرَجَ": ("xrj", "istafala_verb"),
    "استخرج": ("xrj", "istafala_verb"),
    "مُستَخرَج": ("xrj", "mustafl_patient"),
    "مستخرج": ("xrj", "mustafl_patient"),
    "عَرَبيّ": ("arb", "nisba_yaa"),
    "عربي": ("arb", "nisba_yaa"),
    "مَخرَج": ("xrj", "mafal_place"),
    "مخرج": ("xrj", "mafal_place"),
    "مَدخَل": ("dxl", "mafal_place"),
    "مدخل": ("dxl", "mafal_place"),
    # ── فعل / fal ─────────────────────────────────────────────────────────
    "فاعِل": ("fal", "faail"),
    "فاعل": ("fal", "faail"),
    "مَفعول": ("fal", "mafuul"),
    "مفعول": ("fal", "mafuul"),
    "فِعل": ("fal", "fiaala_masdar_craft"),
    "فعل": ("fal", "fiaala_masdar_craft"),
    "أفعال": ("fal", "afaal_plural"),
    # ── نور / nwr ─────────────────────────────────────────────────────────
    "نور": ("nwr", "faail"),
    "نُور": ("nwr", "faail"),
    "أنوار": ("nwr", "afaal_plural"),
    "مُنير": ("nwr", "mufaail_agent"),
    "منير": ("nwr", "mufaail_agent"),
    # ── رفع / rfa ─────────────────────────────────────────────────────────
    "مَرفوع": ("rfa", "mafuul"),
    "مرفوع": ("rfa", "mafuul"),
    "رَفع": ("rfa", "fiaala_masdar_craft"),
    "رفع": ("rfa", "fiaala_masdar_craft"),
    # ── حرم / hrm ─────────────────────────────────────────────────────────
    "حَرام": ("hrm", "faiil_attr"),
    "حرام": ("hrm", "faiil_attr"),
    "مُحرَّم": ("hrm", "mafuul"),
    "محرم": ("hrm", "mafuul"),
    "حُرمة": ("hrm", "fiaala_masdar_craft"),
    "حرمة": ("hrm", "fiaala_masdar_craft"),
    # ── قول / qwl ─────────────────────────────────────────────────────────
    "قائِل": ("qwl", "faail"),
    "قائل": ("qwl", "faail"),
    "مَقول": ("qwl", "mafuul"),
    "مقول": ("qwl", "mafuul"),
    "قَول": ("qwl", "fiaala_masdar_craft"),
    "قول": ("qwl", "fiaala_masdar_craft"),
    # ── عمل / aml ─────────────────────────────────────────────────────────
    "عامِل": ("aml", "faail"),
    "عامل": ("aml", "faail"),
    "مَعمول": ("aml", "mafuul"),
    "معمول": ("aml", "mafuul"),
    "عَمَل": ("aml", "fiaala_masdar_craft"),
    "عمل": ("aml", "fiaala_masdar_craft"),
    "أعمال": ("aml", "afaal_plural"),
    # ── ذهب / dhb ─────────────────────────────────────────────────────────
    "ذاهِب": ("dhb", "faail"),
    "ذاهب": ("dhb", "faail"),
    "مَذهَب": ("dhb", "mafal_place"),
    "مذهب": ("dhb", "mafal_place"),
    # ── سلم / slm ─────────────────────────────────────────────────────────
    "سالِم": ("slm", "faail"),
    "سالم": ("slm", "faail"),
    "مُسلِم": ("slm", "mufaail_agent"),
    "مسلم": ("slm", "mufaail_agent"),
    "سَلام": ("slm", "faiil_attr"),
    "سلام": ("slm", "faiil_attr"),
    "إسلام": ("slm", "istafala_verb"),
    "اسلام": ("slm", "istafala_verb"),
}

_ROOT_DOMAIN_MAP: dict[str, dict[str, float]] = {
    "ktb": {"literacy": 1.0, "knowledge": 0.8, "communication": 0.7},
    "alm": {"knowledge": 1.0, "science": 0.9, "education": 0.7},
    "zraa": {"agriculture": 1.0, "nature": 0.8, "economy": 0.5},
    "xrj": {"motion": 0.8, "extraction": 0.9, "production": 0.6},
    "dxl": {"motion": 0.8, "entry": 0.9},
    "arb": {"ethnicity": 1.0, "language": 0.9, "geography": 0.5},
    "snaa": {"craft": 1.0, "industry": 0.9, "economy": 0.6},
    "qwl": {"speech": 1.0, "communication": 0.9},
    "fth": {"motion": 0.5, "conquest": 0.9, "impact": 0.8},
    "nsr": {"social": 0.7, "support": 1.0},
    "hmd": {"social": 0.8, "praise": 1.0},
    "krm": {"social": 0.9, "virtue": 1.0},
    "hsn": {"beauty": 1.0, "virtue": 0.8},
    "bny": {"construction": 1.0, "craft": 0.7},
    "jma": {"collection": 1.0, "social": 0.6},
}


class MorphosemanticTraceLinker:
    """Builds a full morphosemantic trace from a surface word to ConceptCenter."""

    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()
        self._roots = {r.root_id: r for r in load_root_ontology()}
        self._normalizer = MorphophonologicalNormalizer()
        self._mapper = ConceptCenterMapper()

    def link(self, word: str) -> MorphosemanticTraceBundle:
        trace_id = f"MST-{uuid.uuid4().hex[:10]}"
        norm_result = self._normalizer.normalize(word)
        norm = norm_result.normalized

        # Look up root and pattern — try: original, normalised, article-stripped
        def _strip_article(w: str) -> str:
            return w[2:] if w.startswith("ال") and len(w) > 2 else w

        bare_word = _strip_article(word)
        bare_norm = _strip_article(norm)
        root_id, pattern_id = (
            _KNOWN_WORDS.get(word)
            or _KNOWN_WORDS.get(norm)
            or _KNOWN_WORDS.get(bare_word)
            or _KNOWN_WORDS.get(bare_norm)
            or ("unknown", "unknown")
        )

        # Token trace (simplified)
        token_trace = {
            "word": word,
            "normalized": norm,
            "char_count": len(word),
            "operations": norm_result.operations_applied,
        }

        # Root candidates
        root_candidates = [{"root_id": root_id, "confidence": 0.9}] if root_id != "unknown" else []

        # Pattern candidates
        pattern_op = self._registry.get(pattern_id)
        pattern_candidates = []
        if pattern_op:
            pattern_candidates = [{"pattern_id": pattern_id, "pattern_form": pattern_op.pattern_form, "confidence": 0.9}]

        # Role vector from pattern
        role_vector: dict[str, float] = {}
        if pattern_op:
            role_vector = {k: v for k, v in pattern_op.operator_vector.items()}

        # Domain vector from root
        domain_vector = dict(_ROOT_DOMAIN_MAP.get(root_id, {"general": 0.5}))

        # Event vector
        event_vector: dict[str, float] = {}
        root_obj = self._roots.get(root_id)
        if root_obj:
            event_vector = {ev: 0.7 for ev in root_obj.event_potential}

        # Build FoldedWordGraph
        fwg = build_folded_word_graph(
            word=word,
            root_id=root_id,
            pattern_id=pattern_id,
            role_vector=role_vector,
            domain_vector=domain_vector,
            event_vector=event_vector,
            certainty_policy=pattern_op.certainty_policy if pattern_op else "unknown",
            root_candidates=[c["root_id"] for c in root_candidates],
            pattern_candidates=[c["pattern_id"] for c in pattern_candidates],
        )

        # Build ConceptCenter
        cc = self._mapper.map(fwg)

        # Count link depth
        depth = 0
        if root_id != "unknown":
            depth += 1
        if pattern_op:
            depth += 1
        if root_obj:
            depth += 1
        if cc.event_axis:
            depth += 1

        return MorphosemanticTraceBundle(
            trace_id=trace_id,
            word=word,
            normalized_word=norm,
            token_trace=token_trace,
            root_candidates=root_candidates,
            pattern_candidates=pattern_candidates,
            folded_word_graph=fwg,
            concept_center=cc,
            link_depth=depth,
        )
