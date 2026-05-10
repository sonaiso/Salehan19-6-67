"""Tests for mcd.murab — Arabic I'rab Relational Engineering Layer (Phase 7.5).

Run with:  PYTHONPATH=src python -m pytest tests/test_murab.py -v
"""
from __future__ import annotations

import json
import pytest

from mcd.murab import (
    MurabAnalyzer,
    MurabUnit,
    IrabCase,
    IrabCaseRegistry,
    IRAB_CASE_REGISTRY,
    IrabMarker,
    IrabMarkerRegistry,
    IRAB_MARKER_REGISTRY,
    GoverningFactor,
    GoverningFactorRegistry,
    GOVERNING_FACTOR_REGISTRY,
    CaseResolver,
    NominativeResolver,
    AccusativeResolver,
    GenitiveResolver,
    JussiveResolver,
    MoodResolver,
    AgreementEngine,
    DependencyResolver,
    IdafaEngine,
    TawabiEngine,
    HalTamyizEngine,
    ZarfEngine,
    EstimatedIrabEngine,
    IrregularIrabRegistry,
    IRREGULAR_IRAB_REGISTRY,
    MurabGraphBuilder,
    MurabGraph,
    MurabTraceLinker,
    MurabCertaintyPolicy,
    MurabReport,
    murab_units_to_json,
    murab_units_to_markdown,
    murab_graph_to_json,
    murab_graph_to_markdown,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EXAMPLE_SENTENCE = "كَتَبَ زَيْدٌ الدَّرْسَ بِالْقَلَمِ"


@pytest.fixture
def analyzer():
    return MurabAnalyzer()


@pytest.fixture
def example_units(analyzer):
    return analyzer.analyze(EXAMPLE_SENTENCE)


# ---------------------------------------------------------------------------
# MurabSchema
# ---------------------------------------------------------------------------

class TestMurabUnit:
    def test_to_dict_roundtrip(self):
        unit = MurabUnit(
            unit_id="u1",
            surface="زَيْدٌ",
            normalized="زيد",
            token_id="tok_1",
            word_type="noun",
            irab_case="nominative",
            irab_marker="damma",
            marker_visibility="apparent",
            governing_factor_id=None,
            syntactic_role="فاعل",
            semantic_role="agent",
        )
        d = unit.to_dict()
        restored = MurabUnit.from_dict(d)
        assert restored.unit_id == unit.unit_id
        assert restored.irab_case == "nominative"
        assert restored.semantic_role == "agent"

    def test_from_dict_defaults(self):
        unit = MurabUnit.from_dict({"unit_id": "x", "surface": "قلم", "normalized": "قلم",
                                    "irab_case": "genitive", "irab_marker": "kasra",
                                    "marker_visibility": "apparent",
                                    "syntactic_role": "", "semantic_role": "unknown"})
        assert unit.warnings == []
        assert unit.trace_ids == []


# ---------------------------------------------------------------------------
# IrabCase Registry
# ---------------------------------------------------------------------------

class TestIrabCaseRegistry:
    def test_all_six_cases_present(self):
        cases = IRAB_CASE_REGISTRY.all()
        ids = {c.case_id for c in cases}
        assert {"nominative", "accusative", "genitive", "jussive",
                "indeclinable_local", "estimated"} == ids

    def test_get_nominative(self):
        case = IRAB_CASE_REGISTRY.get("nominative")
        assert case is not None
        assert case.name_ar == "رفع"
        assert "damma" in case.possible_markers

    def test_to_dict(self):
        case = IRAB_CASE_REGISTRY.get("genitive")
        d = case.to_dict()
        assert d["case_id"] == "genitive"
        assert "kasra" in d["possible_markers"]


# ---------------------------------------------------------------------------
# IrabMarker Registry
# ---------------------------------------------------------------------------

class TestIrabMarkerRegistry:
    def test_all_twelve_markers(self):
        markers = IRAB_MARKER_REGISTRY.all()
        ids = {m.marker_id for m in markers}
        required = {"damma", "fatha", "kasra", "sukun", "alif", "waw", "ya",
                    "nun", "deleted_nun", "estimated", "local", "none"}
        assert required == ids

    def test_damma_marks_nominative(self):
        m = IRAB_MARKER_REGISTRY.get("damma")
        assert "nominative" in m.cases_marked

    def test_to_dict_roundtrip(self):
        m = IRAB_MARKER_REGISTRY.get("kasra")
        assert m.to_dict()["marker_id"] == "kasra"


# ---------------------------------------------------------------------------
# GoverningFactor Registry
# ---------------------------------------------------------------------------

class TestGoverningFactorRegistry:
    def test_preposition_bi_governs_genitive(self):
        gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("ب")
        assert gf is not None
        assert "genitive" in gf.governs_case

    def test_inna_governs_accusative(self):
        gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("إنّ")
        assert gf is not None
        assert "accusative" in gf.governs_case

    def test_lam_governs_jussive(self):
        gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("لم")
        assert "jussive" in gf.governs_case

    def test_lan_governs_accusative(self):
        gf = GOVERNING_FACTOR_REGISTRY.get_by_surface("لن")
        assert "accusative" in gf.governs_case

    def test_to_dict(self):
        gf = GOVERNING_FACTOR_REGISTRY.get("gf_fi")
        d = gf.to_dict()
        assert d["surface"] == "في"


# ---------------------------------------------------------------------------
# CaseResolver
# ---------------------------------------------------------------------------

class TestCaseResolver:
    def setup_method(self):
        self.resolver = CaseResolver()

    def test_damma_nominative(self):
        case, marker, _, certainty, _ = self.resolver.resolve("زَيْدٌ", [])
        assert case == "nominative"
        assert marker == "damma"
        assert certainty == "certain_syntactic"

    def test_fatha_accusative(self):
        case, marker, _, _, _ = self.resolver.resolve("الدَّرْسَ", [])
        assert case == "accusative"
        assert marker == "fatha"

    def test_kasra_genitive(self):
        case, marker, _, _, _ = self.resolver.resolve("بِالْقَلَمِ", ["ب"])
        assert case == "genitive"
        assert marker == "kasra"

    def test_sukun_jussive(self):
        case, marker, _, _, _ = self.resolver.resolve("يَكْتُبْ", ["لم"])
        assert case == "jussive"

    def test_tanwin_damma_nominative(self):
        # ٌ = tanwin damma
        case, marker, _, _, _ = self.resolver.resolve("كِتَابٌ", [])
        assert case == "nominative"
        assert marker == "damma"

    def test_no_haraka_no_gf_unknown(self):
        case, marker, _, certainty, warnings = self.resolver.resolve("كتاب", [])
        assert case == "unknown"
        assert certainty == "hypothesis"
        assert len(warnings) > 0

    def test_governing_factor_detected_from_context(self):
        case, _, gf_id, _, _ = self.resolver.resolve("زيد", ["في"])
        assert gf_id is not None


# ---------------------------------------------------------------------------
# Nominative Resolver
# ---------------------------------------------------------------------------

class TestNominativeResolver:
    def setup_method(self):
        self.r = NominativeResolver()

    def test_nominative_after_verb_resolves_to_fael(self):
        result = self.r.resolve("زَيْدٌ", "verb", 1)
        assert result["syntactic_role"] == "فاعل"
        assert result["semantic_role"] == "agent"

    def test_first_position_no_gf_is_mubtada(self):
        result = self.r.resolve("زَيْدٌ", None, 0)
        assert result["syntactic_role"] == "مبتدأ"

    def test_nasikh_gf(self):
        result = self.r.resolve("زَيْدٌ", "nasikh", 1)
        assert "اسم ناسخ" in result["syntactic_role"]


# ---------------------------------------------------------------------------
# Accusative Resolver
# ---------------------------------------------------------------------------

class TestAccusativeResolver:
    def setup_method(self):
        self.r = AccusativeResolver()

    def test_verb_governed_is_mafool(self):
        result = self.r.resolve("الدَّرْسَ", "verb", 2)
        assert result["syntactic_role"] == "مفعول به"
        assert result["semantic_role"] == "patient"

    def test_nasib_particle_is_mudari_mansub(self):
        result = self.r.resolve("يَذْهَبَ", "nasib", 1)
        assert "منصوب" in result["syntactic_role"]


# ---------------------------------------------------------------------------
# Genitive Resolver
# ---------------------------------------------------------------------------

class TestGenitiveResolver:
    def setup_method(self):
        self.r = GenitiveResolver()

    def test_preposition_governed(self):
        result = self.r.resolve("الْقَلَمِ", "preposition")
        assert result["syntactic_role"] == "اسم مجرور بحرف جر"

    def test_idafa(self):
        result = self.r.resolve("الرَّجُلِ", "idafa")
        assert result["syntactic_role"] == "مضاف إليه"


# ---------------------------------------------------------------------------
# Jussive Resolver
# ---------------------------------------------------------------------------

class TestJussiveResolver:
    def setup_method(self):
        self.r = JussiveResolver()

    def test_jazim_governed(self):
        result = self.r.resolve("يَكْتُبْ", "jazim")
        assert "مجزوم" in result["syntactic_role"]


# ---------------------------------------------------------------------------
# MoodResolver
# ---------------------------------------------------------------------------

class TestMoodResolver:
    def setup_method(self):
        self.r = MoodResolver()

    def test_jazim_jussive(self):
        assert self.r.resolve_mood("يَكْتُبْ", "jazim") == "jussive"

    def test_nasib_subjunctive(self):
        assert self.r.resolve_mood("يَذْهَبَ", "nasib") == "subjunctive"

    def test_no_factor_indicative(self):
        assert self.r.resolve_mood("يَكْتُبُ", None) == "indicative"

    def test_imperative(self):
        assert self.r.resolve_mood("اكتب", None) == "imperative"


# ---------------------------------------------------------------------------
# AgreementEngine
# ---------------------------------------------------------------------------

class TestAgreementEngine:
    def setup_method(self):
        self.engine = AgreementEngine()

    def _make_unit(self, uid, case, marker):
        return MurabUnit(uid, "س", "س", "t", "noun", case, marker, "apparent",
                         None, "", "unknown")

    def test_matching_case_agrees(self):
        h = self._make_unit("h", "nominative", "damma")
        d = self._make_unit("d", "nominative", "damma")
        result = self.engine.check_agreement(h, d)
        assert result["agrees"] is True

    def test_mismatched_case_disagrees(self):
        h = self._make_unit("h", "nominative", "damma")
        d = self._make_unit("d", "accusative", "fatha")
        result = self.engine.check_agreement(h, d)
        assert result["agrees"] is False
        assert any("case_mismatch" in m for m in result["mismatches"])


# ---------------------------------------------------------------------------
# EstimatedIrabEngine
# ---------------------------------------------------------------------------

class TestEstimatedIrabEngine:
    def setup_method(self):
        self.engine = EstimatedIrabEngine()

    def test_maqsur_alif(self):
        result = self.engine.resolve("الفتى", "nominative")
        assert result["has_estimated_marker"] is True
        assert "maqsur" in result["reason"]

    def test_manqus_ya_nominative(self):
        result = self.engine.resolve("القاضي", "nominative")
        assert result["has_estimated_marker"] is True
        assert "manqus" in result["reason"]

    def test_visible_marker(self):
        result = self.engine.resolve("الكتاب", "nominative")
        assert result["has_estimated_marker"] is False


# ---------------------------------------------------------------------------
# IrregularIrabRegistry
# ---------------------------------------------------------------------------

class TestIrregularIrabRegistry:
    def test_five_nouns_waw_nominative(self):
        marker = IRREGULAR_IRAB_REGISTRY.get_marker_for_case("five_nouns", "nominative")
        assert marker == "waw"

    def test_dual_alif_nominative(self):
        marker = IRREGULAR_IRAB_REGISTRY.get_marker_for_case("dual", "nominative")
        assert marker == "alif"

    def test_smp_ya_genitive(self):
        marker = IRREGULAR_IRAB_REGISTRY.get_marker_for_case("sound_plural", "genitive")
        assert marker == "ya"

    def test_is_irregular_dual(self):
        assert IRREGULAR_IRAB_REGISTRY.is_irregular("المعلمان") is True

    def test_is_irregular_false(self):
        assert IRREGULAR_IRAB_REGISTRY.is_irregular("الكتاب") is False


# ---------------------------------------------------------------------------
# IdafaEngine
# ---------------------------------------------------------------------------

class TestIdafaEngine:
    def setup_method(self):
        self.engine = IdafaEngine()

    def _unit(self, uid, surface):
        return MurabUnit(uid, surface, surface, "t", "noun", "genitive", "kasra",
                         "apparent", None, "مضاف إليه", "possessor")

    def test_returns_idafa_type(self):
        mudaf = self._unit("u1", "بيت")
        mudaf_ilayh = self._unit("u2", "الرجل")
        result = self.engine.resolve(mudaf, mudaf_ilayh)
        assert "idafa_type" in result
        assert result["mudaf_id"] == "u1"


# ---------------------------------------------------------------------------
# TawabiEngine
# ---------------------------------------------------------------------------

class TestTawabiEngine:
    def setup_method(self):
        self.engine = TawabiEngine()

    def _unit(self, uid, case, marker):
        return MurabUnit(uid, "س", "س", "t", "noun", case, marker, "apparent",
                         None, "", "unknown")

    def test_inherits_case(self):
        matboo = self._unit("m", "nominative", "damma")
        tabi = self._unit("t", "nominative", "damma")
        result = self.engine.resolve(matboo, tabi, [])
        assert result["inherited_case"] == "nominative"
        assert result["tabi_type"] == "naat"

    def test_atf_particle_detected(self):
        matboo = self._unit("m", "accusative", "fatha")
        tabi = self._unit("t", "accusative", "fatha")
        result = self.engine.resolve(matboo, tabi, ["و"])
        assert result["tabi_type"] == "atf"


# ---------------------------------------------------------------------------
# HalTamyizEngine
# ---------------------------------------------------------------------------

class TestHalTamyizEngine:
    def setup_method(self):
        self.engine = HalTamyizEngine()

    def test_quantity_word_context_gives_tamyiz(self):
        result = self.engine.classify("ذهبًا", "verb", ["كثير"])
        assert result["classification"] == "tamyiz"

    def test_verb_context_suggests_hal(self):
        result = self.engine.classify("راكبًا", "verb", [])
        assert result["classification"] == "hal"

    def test_unknown_without_context(self):
        result = self.engine.classify("شيئًا", None, [])
        assert result["classification"] == "unknown"


# ---------------------------------------------------------------------------
# ZarfEngine
# ---------------------------------------------------------------------------

class TestZarfEngine:
    def setup_method(self):
        self.engine = ZarfEngine()

    def test_yawm_is_zaman(self):
        result = self.engine.resolve("يوم", [])
        assert result["zarf_type"] == "zaman"

    def test_amam_is_makan(self):
        result = self.engine.resolve("أمام", [])
        assert result["zarf_type"] == "makan"

    def test_pp_context_shibh_jumla(self):
        result = self.engine.resolve("المسجد", ["في"])
        assert result["zarf_type"] == "shibh_jumla"


# ---------------------------------------------------------------------------
# MurabGraph
# ---------------------------------------------------------------------------

class TestMurabGraph:
    def test_build_produces_nodes_and_edges(self, example_units):
        builder = MurabGraphBuilder()
        graph = builder.build(example_units, EXAMPLE_SENTENCE)
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

    def test_to_dict_roundtrip(self, example_units):
        builder = MurabGraphBuilder()
        graph = builder.build(example_units, EXAMPLE_SENTENCE)
        d = graph.to_dict()
        assert d["sentence"] == EXAMPLE_SENTENCE
        assert isinstance(d["nodes"], list)
        assert isinstance(d["edges"], list)

    def test_from_dict(self, example_units):
        builder = MurabGraphBuilder()
        graph = builder.build(example_units, EXAMPLE_SENTENCE)
        d = graph.to_dict()
        restored = MurabGraph.from_dict(d)
        assert restored.sentence == EXAMPLE_SENTENCE


# ---------------------------------------------------------------------------
# MurabTraceLinker
# ---------------------------------------------------------------------------

class TestMurabTraceLinker:
    def test_link(self, example_units):
        linker = MurabTraceLinker()
        unit = example_units[1]  # زيد
        trace = linker.link(unit, "tok_1", 7, 12)
        assert trace["unit_id"] == unit.unit_id
        assert trace["char_range"] == [7, 12]
        assert "estimated" in trace

    def test_link_estimated(self, example_units):
        linker = MurabTraceLinker()
        unit = example_units[1]
        trace = linker.link_estimated(unit, "maqsur_alif_end")
        assert trace["estimated"] is True
        assert trace["reason"] == "maqsur_alif_end"


# ---------------------------------------------------------------------------
# MurabCertaintyPolicy
# ---------------------------------------------------------------------------

class TestMurabCertaintyPolicy:
    def test_certain_syntactic_with_clear_gf(self, example_units):
        policy = MurabCertaintyPolicy()
        unit = example_units[3]  # بالقلم — genitive, has governing factor
        gf = GOVERNING_FACTOR_REGISTRY.get(unit.governing_factor_id)
        result = policy.evaluate(unit, gf)
        assert result["evidence_effect"] == "syntactic_only"
        assert "syntactic_certainty" in result

    def test_no_gf_gives_warning(self, example_units):
        policy = MurabCertaintyPolicy()
        unit = example_units[1]  # زيد
        unit.governing_factor_id = None
        result = policy.evaluate(unit, None)
        assert result["syntactic_certainty"] in ("probable_syntactic", "hypothesis")


# ---------------------------------------------------------------------------
# MurabReport
# ---------------------------------------------------------------------------

class TestMurabReport:
    def test_to_dict(self, example_units):
        report = MurabReport()
        d = report.to_dict(example_units, EXAMPLE_SENTENCE)
        assert d["sentence"] == EXAMPLE_SENTENCE
        assert d["token_count"] == len(example_units)

    def test_to_markdown_contains_sentence(self, example_units):
        report = MurabReport()
        md = report.to_markdown(example_units, EXAMPLE_SENTENCE)
        assert EXAMPLE_SENTENCE in md
        assert "الإعراب" in md

    def test_generate_returns_dict(self, example_units):
        report = MurabReport()
        result = report.generate(example_units, EXAMPLE_SENTENCE)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class TestSerializers:
    def test_units_to_json(self, example_units):
        js = murab_units_to_json(example_units)
        data = json.loads(js)
        assert len(data) == len(example_units)
        assert "irab_case" in data[0]

    def test_units_to_markdown(self, example_units):
        md = murab_units_to_markdown(example_units, EXAMPLE_SENTENCE)
        assert isinstance(md, str)
        assert "الإعراب" in md

    def test_graph_to_json(self, example_units):
        builder = MurabGraphBuilder()
        graph = builder.build(example_units, EXAMPLE_SENTENCE)
        js = murab_graph_to_json(graph)
        d = json.loads(js)
        assert "nodes" in d and "edges" in d

    def test_graph_to_markdown(self, example_units):
        builder = MurabGraphBuilder()
        graph = builder.build(example_units, EXAMPLE_SENTENCE)
        md = murab_graph_to_markdown(graph)
        assert "MurabGraph" in md


# ---------------------------------------------------------------------------
# MurabAnalyzer — full integration
# ---------------------------------------------------------------------------

class TestMurabAnalyzer:
    def test_example_sentence_token_count(self, example_units):
        assert len(example_units) == 4

    def test_kataba_is_verb(self, example_units):
        kataba = example_units[0]
        assert kataba.word_type == "verb"
        assert kataba.irab_case == "indeclinable_local"

    def test_zayd_is_nominative_fael(self, example_units):
        zayd = example_units[1]
        assert zayd.irab_case == "nominative"
        assert zayd.irab_marker == "damma"
        assert zayd.syntactic_role == "فاعل"
        assert zayd.semantic_role == "agent"

    def test_aldars_is_accusative_mafool(self, example_units):
        dars = example_units[2]
        assert dars.irab_case == "accusative"
        assert dars.irab_marker == "fatha"
        assert dars.syntactic_role == "مفعول به"

    def test_bialqalam_is_genitive(self, example_units):
        qalam = example_units[3]
        assert qalam.irab_case == "genitive"
        assert qalam.irab_marker == "kasra"

    def test_all_units_have_ids(self, example_units):
        for u in example_units:
            assert u.unit_id
            assert u.token_id

    def test_units_serializable(self, example_units):
        for u in example_units:
            d = u.to_dict()
            assert isinstance(d, dict)
            MurabUnit.from_dict(d)
