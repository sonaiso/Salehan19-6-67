"""Tests for Phase 7.3 — Arabic Morphosemantic Fractal Engine.

All tests are self-contained (no data files required). They rely only on the
built-in hardcoded data within each engine module.
"""
from __future__ import annotations

import importlib
import sys
import types


# ─── 1. Root Ontology ────────────────────────────────────────────────────────

def test_root_ontology_builtin_loads():
    from mcd.morphosemantics.root_ontology import load_root_ontology
    roots = load_root_ontology()
    assert len(roots) > 0
    root = roots[0]
    assert hasattr(root, "root_id")
    assert hasattr(root, "radicals")
    assert len(root.radicals) >= 3


def test_root_ontology_get_by_id():
    from mcd.morphosemantics.root_ontology import get_root_by_id
    root = get_root_by_id("ktb")
    assert root is not None
    assert root.root_id == "ktb"
    assert "ك" in root.radicals


def test_root_ontology_get_by_radicals():
    from mcd.morphosemantics.root_ontology import get_root_by_radicals
    root = get_root_by_radicals(["ع", "ل", "م"])
    assert root is not None
    assert root.root_id == "alm"


# ─── 2. Pattern Operator Registry ────────────────────────────────────────────

def test_pattern_registry_builtin():
    from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
    reg = PatternOperatorRegistry()
    ops = reg.all()
    assert len(ops) >= 16


def test_pattern_registry_get():
    from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
    reg = PatternOperatorRegistry()
    op = reg.get("faail")
    assert op is not None
    assert op.pattern_form == "فاعِل"
    assert op.operator_vector.get("agency", 0) > 0.5


def test_pattern_registry_find_by_form():
    from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
    reg = PatternOperatorRegistry()
    result = reg.find_by_form("مَفعول")
    assert result is not None
    assert result.pattern_id == "mafuul"


# ─── 3. Masdar Event Ontology ────────────────────────────────────────────────

def test_masdar_event_ontology_loads():
    from mcd.morphosemantics.masdar_event_ontology import load_masdar_events
    events = load_masdar_events()
    assert len(events) > 0


def test_masdar_event_by_root():
    from mcd.morphosemantics.masdar_event_ontology import get_masdars_by_root
    events = get_masdars_by_root("ktb")
    assert len(events) > 0
    assert events[0].root_id == "ktb"


# ─── 4. Folded Word Graph ────────────────────────────────────────────────────

def test_folded_word_graph_build():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("كاتِب")
    graph = bundle.folded_word_graph
    assert graph.word == "كاتِب"
    assert graph.selected_root is not None
    assert graph.selected_pattern is not None
    assert len(graph.folded_edges) > 0


def test_folded_word_graph_to_dict():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("عالِم")
    graph = bundle.folded_word_graph
    d = graph.to_dict()
    assert "word" in d
    assert "selected_root" in d
    assert "folded_edges" in d
    assert isinstance(d["folded_edges"], list)


# ─── 5. Folded Word Unfolder ─────────────────────────────────────────────────

def test_folded_word_unfolder():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    from mcd.morphosemantics.folded_word_unfolder import FoldedWordUnfolder
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("زارِع")
    graph = bundle.folded_word_graph
    unfolder = FoldedWordUnfolder()
    unfolded = unfolder.unfold(graph)
    assert unfolded.word == "زارِع"
    md = unfolded.to_markdown()
    assert "زارِع" in md
    assert "#" in md


# ─── 6. Concept Center ───────────────────────────────────────────────────────

def test_concept_center_mapper():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    from mcd.morphosemantics.concept_center_mapper import ConceptCenterMapper
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("صانِع")
    graph = bundle.folded_word_graph
    mapper = ConceptCenterMapper()
    cc = mapper.map(graph)
    assert "صانِع" in cc.surface_forms
    d = cc.to_dict()
    assert "agency_axis" in d
    assert "certainty_axis" in d


# ─── 7. Morphosemantic Trace Linker ──────────────────────────────────────────

def test_trace_linker_known_word():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("كاتِب")
    assert bundle.word == "كاتِب"
    assert bundle.folded_word_graph is not None
    assert bundle.concept_center is not None


def test_trace_linker_unknown_word_graceful():
    from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
    linker = MorphosemanticTraceLinker()
    bundle = linker.link("XYZ_not_arabic_999")
    assert bundle.word == "XYZ_not_arabic_999"
    assert bundle.folded_word_graph is not None  # falls back to generic


# ─── 8. Contextual Pattern Resolver ──────────────────────────────────────────

def test_contextual_resolver_ambiguous_word():
    from mcd.morphosemantics.contextual_pattern_resolver import ContextualPatternResolver
    resolver = ContextualPatternResolver()
    result = resolver.resolve("عين", context_tokens=["تدمع", "جميلة"])
    assert result is not None
    assert len(result.candidate_meanings) > 0


# ─── 9. Morphophonological Normalizer ────────────────────────────────────────

def test_morphophonological_normalizer():
    from mcd.morphosemantics.morphophonological_normalizer import MorphophonologicalNormalizer
    norm = MorphophonologicalNormalizer()
    result = norm.normalize("كَاتِبٌ")
    # normalize returns a NormalizationResult; check normalized field
    normalized = result.normalized if hasattr(result, "normalized") else str(result)
    assert "ً" not in normalized
    assert "ٌ" not in normalized
    assert "كاتب" in normalized


# ─── 10. Broken Plural Transformer ───────────────────────────────────────────

def test_broken_plural_transformer():
    from mcd.morphosemantics.broken_plural_transformer import BrokenPluralTransformer
    bt = BrokenPluralTransformer()
    result = bt.transform("كِتاب")
    assert result is not None
    assert result.plural_form is not None


# ─── 11. Nisba Engine ────────────────────────────────────────────────────────

def test_nisba_engine_builtin():
    from mcd.morphosemantics.nisba_engine import NisbaEngine
    engine = NisbaEngine()
    result = engine.derive("عَرَب")
    assert result is not None
    # The nisba form should contain عرب
    nisba = result.nisba_form
    assert "عرب" in nisba or "عَرَب" in nisba


# ─── 12. Diminutive Operator ─────────────────────────────────────────────────

def test_diminutive_operator():
    from mcd.morphosemantics.diminutive_operator import DiminutiveOperator
    op = DiminutiveOperator()
    result = op.derive("كِتاب")
    assert result is not None
    assert result.diminutive_form is not None


# ─── 13. Pattern Certainty Scorer ────────────────────────────────────────────

def test_pattern_certainty_scorer():
    from mcd.morphosemantics.pattern_certainty import PatternCertaintyScorer
    scorer = PatternCertaintyScorer()
    result = scorer.score("faail", "ktb")
    assert 0.0 <= result.certainty_score <= 1.0


# ─── 14. Root Family Graph ───────────────────────────────────────────────────

def test_root_family_graph_build():
    from mcd.morphosemantics.root_family_graph import RootFamilyGraphBuilder
    builder = RootFamilyGraphBuilder()
    graph = builder.build("ktb")
    assert graph.root_id == "ktb"
    d = graph.to_dict()
    assert "members" in d
    assert "masdar_events" in d


# ─── 15. No Network Calls ────────────────────────────────────────────────────

def test_no_network_calls():
    """Verify no network-accessing module is imported by morphosemantics."""
    import mcd.morphosemantics  # noqa: F401 — force import

    network_modules = {"socket", "urllib", "requests", "httpx", "aiohttp", "http.client"}
    morph_modules = {
        name for name in sys.modules
        if name.startswith("mcd.morphosemantics")
    }
    # Walk each morphosemantics module's globals for network imports
    for mod_name in morph_modules:
        mod = sys.modules[mod_name]
        if not isinstance(mod, types.ModuleType):
            continue
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name, None)
            if isinstance(attr, types.ModuleType):
                if attr.__name__ in network_modules:
                    raise AssertionError(
                        f"Network module '{attr.__name__}' found in {mod_name}.{attr_name}"
                    )
