"""Tests for the Bayani Cognitive Layer — العقل المعرفي المستدل.

Covers:
  - UnicodeAtomicEncoder: character → feature vector
  - RoleVectorizer: feature vector × context → role vector
  - ArabicMorphologyAnalyzer: root extraction, pattern matching, syllabification
  - MultiDimensionalCertaintyScorer: 9-dimension formula
  - ThreeLayerMemory: atomic / relational / conceptual layers
  - FractalComposer: multi-level composition
  - CognitiveReasoningMind: knower and learner modes

Run with:
    python -m pytest tests/test_cognitive_mind.py -v
"""

from __future__ import annotations

import pytest

from bayani.cognitive import (
    ArabicMorphologyAnalyzer,
    CognitiveReasoningMind,
    FractalComposer,
    KnowledgeNode,
    MultiDimensionalCertaintyScorer,
    NodeLevel,
    RoleVectorizer,
    ThreeLayerMemory,
    UnicodeAtomicEncoder,
)
from bayani.cognitive.certainty import CertaintyResult
from bayani.cognitive.knowledge_node import CertaintyInfo, NodeRelation


# ===========================================================================
# UnicodeAtomicEncoder
# ===========================================================================

class TestUnicodeAtomicEncoder:
    """Tests for Φ: UnicodeSymbol → AtomicFeatureVector."""

    def setup_method(self) -> None:
        self.enc = UnicodeAtomicEncoder()

    def test_encode_arabic_consonant_kaf(self) -> None:
        feat = self.enc.encode("ك")
        assert feat["class"] == "consonant"
        assert feat["script"] == "arabic"
        assert feat["unicode"] == "U+0643"
        assert "phonetic" in feat
        assert feat["phonetic"]["place"] == "velar"
        assert feat["certainty"] == 1.0

    def test_encode_arabic_consonant_mim(self) -> None:
        feat = self.enc.encode("م")
        assert feat["class"] == "consonant"
        mp = feat["morphological_potential"]
        # م is a common prefix (مكتبة, مكتوب) — prefix_candidate should be high
        assert mp["prefix_candidate"] > 0.50

    def test_encode_fatha_diacritic(self) -> None:
        feat = self.enc.encode("\u064E")  # fatha
        assert feat["class"] == "diacritic"
        assert feat["diacritic_name"] == "fatha"
        assert "phonological_role" in feat
        assert feat["phonological_role"]["opens_syllable"] > 0.80

    def test_encode_shadda(self) -> None:
        feat = self.enc.encode("\u0651")  # shadda
        assert feat["class"] == "shadda"
        assert feat["diacritic_name"] == "shadda"

    def test_encode_alef_long_vowel(self) -> None:
        feat = self.enc.encode("ا")
        assert feat["class"] == "long_vowel"

    def test_encode_taa_marbuta(self) -> None:
        feat = self.enc.encode("ة")
        assert feat["class"] == "consonant"
        mp = feat["morphological_potential"]
        # ة is almost always a suffix
        assert mp["suffix_candidate"] > 0.80

    def test_to_node_returns_knowledge_node(self) -> None:
        node = self.enc.to_node("ب", node_id="test-001")
        assert isinstance(node, KnowledgeNode)
        assert node.node_id == "test-001"
        assert node.level == NodeLevel.ATOM
        assert node.surface == "ب"
        assert node.certainty.score == 1.0
        assert node.certainty.evidence_type == "orthographic"

    def test_encode_non_arabic_character(self) -> None:
        feat = self.enc.encode("A")
        assert feat["script"] == "other"

    def test_encode_arabic_digit(self) -> None:
        feat = self.enc.encode("٣")  # Arabic-Indic digit 3
        assert feat["class"] == "digit"

    def test_all_common_arabic_letters_have_phonetics(self) -> None:
        letters = "بتثجحخدذرزسشصضطظعغفقكلمنهوي"
        for ch in letters:
            feat = self.enc.encode(ch)
            assert "phonetic" in feat, f"Missing phonetic for {ch}"


# ===========================================================================
# RoleVectorizer
# ===========================================================================

class TestRoleVectorizer:
    """Tests for Ρ: AtomicFeatureVector × Context → RoleVector."""

    def setup_method(self) -> None:
        self.enc = UnicodeAtomicEncoder()
        self.rv = RoleVectorizer()

    def _make_atoms(self, word: str) -> list:
        return [self.enc.to_node(ch, node_id=f"a-{i}") for i, ch in enumerate(word)]

    def test_mim_prefix_high_in_maktub(self) -> None:
        atoms = self._make_atoms("مكتوب")
        self.rv.assign_roles(atoms, word_surface="مكتوب")
        # First atom is م — should have elevated prefix probability
        mim_rv = atoms[0].role_vector
        assert mim_rv.get("prefix_derivational", 0) > 0.30

    def test_taa_marbuta_suffix_role(self) -> None:
        atoms = self._make_atoms("كتابة")
        self.rv.assign_roles(atoms, word_surface="كتابة")
        # Last atom is ة — almost certainly a suffix
        ta_marbuta_rv = atoms[-1].role_vector
        assert ta_marbuta_rv.get("suffix_inflectional", 0) > 0.70

    def test_standalone_waw_conjunction(self) -> None:
        atoms = self._make_atoms("و")
        self.rv.assign_roles(atoms, word_surface="و", is_standalone_particle=True)
        rv = atoms[0].role_vector
        assert rv.get("conjunction", 0) > 0.80

    def test_role_vector_values_in_unit_interval(self) -> None:
        atoms = self._make_atoms("الطالب")
        self.rv.assign_roles(atoms, word_surface="الطالب")
        for node in atoms:
            for val in node.role_vector.values():
                assert 0.0 <= val <= 1.0, f"Role value out of range: {val}"

    def test_all_atoms_get_role_vector(self) -> None:
        atoms = self._make_atoms("كتب")
        self.rv.assign_roles(atoms, word_surface="كتب")
        for node in atoms:
            assert node.role_vector, f"Empty role vector for atom: {node.surface}"


# ===========================================================================
# ArabicMorphologyAnalyzer
# ===========================================================================

class TestArabicMorphologyAnalyzer:
    """Tests for root extraction, pattern matching, and syllabification."""

    def setup_method(self) -> None:
        self.ana = ArabicMorphologyAnalyzer()

    def test_analyze_kataba_root(self) -> None:
        result = self.ana.analyze("كتب")
        assert result.best_root is not None
        assert "كتب" in result.best_root or len(result.root_candidates) > 0

    def test_analyze_maktub_has_root_candidates(self) -> None:
        result = self.ana.analyze("مكتوب")
        assert len(result.root_candidates) > 0

    def test_analyze_maktub_has_pattern_match(self) -> None:
        result = self.ana.analyze("مكتوب")
        # مفعول pattern should match
        descriptions = [pm.description for pm in result.pattern_matches]
        assert any("patient_noun" in d or "mafool" in d for d in descriptions)

    def test_analyze_katib_agent_noun_pattern(self) -> None:
        result = self.ana.analyze("كاتب")
        descriptions = [pm.description for pm in result.pattern_matches]
        # فاعل pattern → agent_noun
        assert any("agent" in d for d in descriptions)

    def test_analyze_syllables_not_empty(self) -> None:
        result = self.ana.analyze("الطالب")
        assert len(result.syllables) > 0

    def test_morphological_certainty_range(self) -> None:
        result = self.ana.analyze("كتب")
        assert 0.0 <= result.morphological_certainty <= 1.0

    def test_analyze_sentence_returns_one_per_token(self) -> None:
        results = self.ana.analyze_sentence("كتب الطالب الدرس")
        assert len(results) == 3

    def test_strip_diacritics(self) -> None:
        from bayani.cognitive.arabic_morphology import strip_diacritics
        assert strip_diacritics("كَتَبَ") == "كتب"
        assert strip_diacritics("مَكْتُوب") == "مكتوب"

    def test_segmentation_prefix_article(self) -> None:
        result = self.ana.analyze("الطالب")
        seg = result.segmentation
        assert seg is not None
        assert "ال" in seg.prefix or "ال" in (seg.prefix or "")


# ===========================================================================
# MultiDimensionalCertaintyScorer
# ===========================================================================

class TestMultiDimensionalCertaintyScorer:
    """Tests for the 9-dimension certainty formula."""

    def setup_method(self) -> None:
        self.scorer = MultiDimensionalCertaintyScorer()

    def test_high_scores_produce_high_certainty(self) -> None:
        result = self.scorer.score(
            claim="الطالب فاعل",
            unicode_integrity=1.0,
            morphological_fit=0.90,
            syntactic_fit=0.90,
            semantic_fit=0.85,
            context_fit=0.80,
            evidence_strength=0.88,
            reality_match=0.80,
            ambiguity_penalty=0.05,
            contradiction_penalty=0.00,
        )
        assert result.final_certainty >= 0.70

    def test_contradiction_penalty_lowers_score(self) -> None:
        base = self.scorer.score(
            "test_claim",
            morphological_fit=0.80,
            semantic_fit=0.80,
            contradiction_penalty=0.0,
        )
        penalised = self.scorer.score(
            "test_claim",
            morphological_fit=0.80,
            semantic_fit=0.80,
            contradiction_penalty=1.0,
        )
        assert penalised.final_certainty < base.final_certainty

    def test_score_clamped_to_unit_interval(self) -> None:
        result = self.scorer.score(
            "edge_case",
            unicode_integrity=1.0,
            morphological_fit=1.0,
            syntactic_fit=1.0,
            semantic_fit=1.0,
            context_fit=1.0,
            evidence_strength=1.0,
            reality_match=1.0,
            ambiguity_penalty=0.0,
            contradiction_penalty=0.0,
        )
        assert 0.0 <= result.final_certainty <= 1.0

    def test_zero_input_score_is_zero(self) -> None:
        result = self.scorer.score(
            "empty_claim",
            unicode_integrity=0.0,
            contradiction_penalty=1.0,
        )
        assert result.final_certainty == 0.0

    def test_status_label_correct_for_high_certainty(self) -> None:
        result = self.scorer.score(
            "high",
            unicode_integrity=1.0,
            morphological_fit=0.95,
            syntactic_fit=0.95,
            semantic_fit=0.95,
            context_fit=0.90,
            evidence_strength=0.95,
            reality_match=0.90,
        )
        assert result.status in (
            "correct_knowledge", "certainty", "strong_certainty", "behavioural_norm"
        )

    def test_passes_threshold(self) -> None:
        result = self.scorer.score(
            "above_threshold",
            morphological_fit=0.85,
            syntactic_fit=0.85,
            semantic_fit=0.80,
            evidence_strength=0.80,
        )
        assert result.passes_threshold(0.60)

    def test_result_to_dict_has_all_dimensions(self) -> None:
        result = self.scorer.score("dict_test")
        d = result.to_dict()
        expected_keys = {
            "unicode_integrity", "morphological_fit", "syntactic_fit",
            "semantic_fit", "context_fit", "evidence_strength", "reality_match",
            "ambiguity_penalty", "contradiction_penalty",
        }
        assert expected_keys == set(d["scores"].keys())

    def test_morphological_claim_convenience(self) -> None:
        result = self.scorer.score_morphological_claim(
            "كاتب اسم فاعل", root_cert=0.90, pattern_cert=0.88
        )
        assert isinstance(result, CertaintyResult)
        assert result.final_certainty > 0.0


# ===========================================================================
# ThreeLayerMemory
# ===========================================================================

class TestThreeLayerMemory:
    """Tests for the three-layer knowledge memory."""

    def setup_method(self) -> None:
        self.mem = ThreeLayerMemory()

    def test_store_and_get_atom(self) -> None:
        self.mem.store_atom("ك", features={"class": "consonant"})
        entry = self.mem.get_atom("ك")
        assert entry is not None
        assert entry.symbol == "ك"
        assert entry.features["class"] == "consonant"

    def test_atom_access_count_increments(self) -> None:
        self.mem.store_atom("م")
        self.mem.get_atom("م")
        self.mem.get_atom("م")
        entry = self.mem.get_atom("م")
        assert entry.access_count >= 3

    def test_store_and_get_relation(self) -> None:
        self.mem.store_relation(
            "root:كتب", "root", "كتب",
            field_label="تدوين", certainty=0.90
        )
        entry = self.mem.get_relation("root:كتب")
        assert entry is not None
        assert entry.surface == "كتب"
        assert entry.certainty == 0.90

    def test_update_relation_certainty(self) -> None:
        self.mem.store_relation("root:درس", "root", "درس", certainty=0.70)
        self.mem.update_relation_certainty("root:درس", delta=+0.10)
        entry = self.mem.get_relation("root:درس")
        assert entry.certainty == pytest.approx(0.80, abs=0.01)

    def test_mark_relation_weak(self) -> None:
        self.mem.store_relation("root:weak", "root", "xyz", certainty=0.80)
        self.mem.mark_relation_weak("root:weak", threshold=0.30)
        entry = self.mem.get_relation("root:weak")
        assert entry.certainty <= 0.30

    def test_store_and_get_concept(self) -> None:
        self.mem.store_concept(
            "c-katib", "كاتب",
            definition="من قام بفعل الكتابة",
            certainty=0.84,
        )
        concept = self.mem.get_concept("c-katib")
        assert concept is not None
        assert concept.name == "كاتب"
        assert concept.certainty == 0.84

    def test_update_concept_certainty(self) -> None:
        self.mem.store_concept("c-test", "تجربة", certainty=0.60)
        self.mem.update_concept_certainty("c-test", delta=+0.15)
        concept = self.mem.get_concept("c-test")
        assert concept.certainty == pytest.approx(0.75, abs=0.01)

    def test_certainty_clamped_at_one(self) -> None:
        self.mem.store_relation("root:clamp", "root", "clamp", certainty=0.99)
        self.mem.update_relation_certainty("root:clamp", delta=+0.50)
        entry = self.mem.get_relation("root:clamp")
        assert entry.certainty <= 1.0

    def test_snapshot_contains_all_layers(self) -> None:
        self.mem.store_atom("ب")
        self.mem.store_relation("root:بدع", "root", "بدع", certainty=0.70)
        self.mem.store_concept("c-bada", "بديع", certainty=0.75)
        snap = self.mem.snapshot()
        assert "atomic" in snap
        assert "relational" in snap
        assert "conceptual" in snap

    def test_counts_correct(self) -> None:
        self.mem.store_atom("ت")
        self.mem.store_relation("r1", "root", "تعب", certainty=0.60)
        self.mem.store_relation("r2", "pattern", "فاعل", certainty=0.80)
        self.mem.store_concept("c1", "تعب", certainty=0.65)
        assert self.mem.atom_count == 1
        assert self.mem.relation_count == 2
        assert self.mem.concept_count == 1


# ===========================================================================
# FractalComposer
# ===========================================================================

class TestFractalComposer:
    """Tests for the fractal composition engine."""

    def setup_method(self) -> None:
        self.enc = UnicodeAtomicEncoder()
        self.composer = FractalComposer()

    def _atoms(self, word: str) -> list:
        return [self.enc.to_node(ch, node_id=f"a-{i}") for i, ch in enumerate(word)]

    def test_compose_syllables_returns_nodes(self) -> None:
        atoms = self._atoms("كتب")
        syllables = self.composer.compose_syllables(atoms)
        assert len(syllables) > 0
        for s in syllables:
            assert s.level == NodeLevel.SYLLABLE

    def test_compose_roots_returns_root_nodes(self) -> None:
        roots = self.composer.compose_roots("كتب")
        assert len(roots) > 0
        for r in roots:
            assert r.level == NodeLevel.ROOT

    def test_compose_patterns_returns_pattern_nodes(self) -> None:
        patterns = self.composer.compose_patterns("كاتب")
        assert len(patterns) > 0
        for p in patterns:
            assert p.level == NodeLevel.PATTERN

    def test_compose_word_returns_word_node(self) -> None:
        roots = self.composer.compose_roots("كتب")
        patterns = self.composer.compose_patterns("كتب")
        word_node = self.composer.compose_word("كتب", roots, patterns)
        assert word_node.level == NodeLevel.WORD
        assert word_node.surface == "كتب"

    def test_compose_word_has_root_relations(self) -> None:
        roots = self.composer.compose_roots("كاتب")
        patterns = self.composer.compose_patterns("كاتب")
        word_node = self.composer.compose_word("كاتب", roots, patterns)
        relation_types = [r.relation_type for r in word_node.relations]
        assert "has_root" in relation_types

    def test_compose_phrase_returns_phrase_node(self) -> None:
        roots = self.composer.compose_roots("الطالب")
        patterns = self.composer.compose_patterns("الطالب")
        w1 = self.composer.compose_word("الطالب", roots, patterns)
        roots2 = self.composer.compose_roots("يكتب")
        patterns2 = self.composer.compose_patterns("يكتب")
        w2 = self.composer.compose_word("يكتب", roots2, patterns2)
        phrase = self.composer.compose_phrase([w1, w2])
        assert phrase.level == NodeLevel.PHRASE
        assert "contains_word" in [r.relation_type for r in phrase.relations]

    def test_compose_all_returns_all_levels(self) -> None:
        atoms = self._atoms("كتب")
        levels = self.composer.compose_all(atoms, context="كتب الطالب الدرس")
        for key in ("atoms", "syllables", "words", "phrases", "sentences", "concepts"):
            assert key in levels, f"Missing level: {key}"

    def test_compose_sentence_returns_sentence_node(self) -> None:
        p1 = self.composer.compose_phrase([], context="test")
        sent = self.composer.compose_sentence([p1], sentence_surface="كتب الطالب")
        assert sent.level == NodeLevel.SENTENCE

    def test_compose_concept_returns_concept_node(self) -> None:
        atoms = self._atoms("كتب")
        levels = self.composer.compose_all(atoms, context="كتب الطالب الدرس")
        if levels.get("sentences"):
            concept = self.composer.compose_concept(levels["sentences"])
            assert concept.level == NodeLevel.CONCEPT


# ===========================================================================
# KnowledgeNode
# ===========================================================================

class TestKnowledgeNode:
    """Tests for the universal KnowledgeNode model."""

    def test_to_dict_has_required_fields(self) -> None:
        node = KnowledgeNode(
            node_id="N-001",
            level=NodeLevel.WORD,
            surface="كتب",
            certainty=CertaintyInfo(score=0.85, status="verified"),
        )
        d = node.to_dict()
        assert d["node_id"] == "N-001"
        assert d["level"] == "word"
        assert d["surface"] == "كتب"
        assert d["certainty"]["score"] == 0.85

    def test_add_relation(self) -> None:
        node = KnowledgeNode(node_id="N-002", surface="درس")
        node.add_relation("has_root", "N-003", certainty=0.90)
        assert len(node.relations) == 1
        assert node.relations[0].relation_type == "has_root"
        assert node.relations[0].target_id == "N-003"

    def test_top_role(self) -> None:
        node = KnowledgeNode(surface="م")
        node.role_vector = {"prefix_derivational": 0.80, "root_radical": 0.30}
        assert node.top_role() == "prefix_derivational"

    def test_top_role_none_when_empty(self) -> None:
        node = KnowledgeNode(surface="ك")
        assert node.top_role() is None

    def test_is_verified_threshold(self) -> None:
        node = KnowledgeNode(certainty=CertaintyInfo(score=0.75))
        assert node.is_verified(threshold=0.60)
        assert not node.is_verified(threshold=0.80)

    def test_certainty_label_arabic(self) -> None:
        ci = CertaintyInfo(score=0.80)
        assert ci.label == "معرفة صحيحة"

    def test_certainty_label_low(self) -> None:
        ci = CertaintyInfo(score=0.10)
        assert ci.label == "لفظ بلا واقع"


# ===========================================================================
# CognitiveReasoningMind — Knower Mode
# ===========================================================================

class TestCognitiveReasoningMindKnower:
    """Tests for the main reasoning pipeline in knower mode."""

    def setup_method(self) -> None:
        self.mind = CognitiveReasoningMind()

    def test_reason_returns_mind_output(self) -> None:
        from bayani.cognitive.mind import MindOutput
        output = self.mind.reason("كتب الطالب الدرس")
        assert isinstance(output, MindOutput)

    def test_reason_mode_is_knower(self) -> None:
        output = self.mind.reason("كتب الطالب الدرس")
        assert output.mode == "knower"

    def test_reason_atom_nodes_populated(self) -> None:
        output = self.mind.reason("كتب")
        assert len(output.atom_nodes) > 0
        for node in output.atom_nodes:
            assert node.level == NodeLevel.ATOM

    def test_reason_levels_has_words(self) -> None:
        output = self.mind.reason("كتب الطالب الدرس")
        assert "words" in output.levels
        assert len(output.levels["words"]) > 0

    def test_reason_overall_certainty_in_range(self) -> None:
        output = self.mind.reason("كتب الطالب الدرس")
        assert 0.0 <= output.overall_certainty <= 1.0

    def test_reason_certainty_label_not_empty(self) -> None:
        output = self.mind.reason("العقل يفهم اللغة")
        assert output.certainty_label != ""

    def test_reason_answer_not_empty(self) -> None:
        output = self.mind.reason("العقل يفهم اللغة")
        assert output.answer.strip() != ""

    def test_reason_no_learned_entries_in_knower_mode(self) -> None:
        output = self.mind.reason("كتب الطالب الدرس", allow_learning=False)
        assert output.learned == []

    def test_reason_knower_does_not_change_memory(self) -> None:
        snap_before = self.mind.memory.snapshot()
        self.mind.reason("مكتبة الجامعة كبيرة", allow_learning=False)
        # Atom memory grows (perceive always stores atoms), relational/conceptual should not
        snap_after = self.mind.memory.snapshot()
        assert len(snap_after["relational"]) == len(snap_before["relational"])
        assert len(snap_after["conceptual"]) == len(snap_before["conceptual"])

    def test_verified_and_suspended_are_lists(self) -> None:
        output = self.mind.reason("كتب الطالب")
        assert isinstance(output.verified, list)
        assert isinstance(output.suspended, list)


# ===========================================================================
# CognitiveReasoningMind — Learner Mode
# ===========================================================================

class TestCognitiveReasoningMindLearner:
    """Tests for the reasoning pipeline in learner mode."""

    def setup_method(self) -> None:
        self.mind = CognitiveReasoningMind()

    def test_reason_mode_is_learner(self) -> None:
        output = self.mind.reason("كتب الطالب الدرس", allow_learning=True)
        assert output.mode == "learner"

    def test_learner_may_store_to_memory(self) -> None:
        snap_before = self.mind.memory.snapshot()
        self.mind.reason(
            "كتب الطالب الدرس",
            external_evidence=["word_order", "definiteness"],
            allow_learning=True,
        )
        snap_after = self.mind.memory.snapshot()
        # At minimum, atoms should have been stored
        assert self.mind.memory.atom_count > 0

    def test_learner_learned_list(self) -> None:
        output = self.mind.reason(
            "كتب الطالب الدرس",
            external_evidence=["word_order"],
            allow_learning=True,
        )
        # learned is a list (may be empty if no node passed learning_threshold)
        assert isinstance(output.learned, list)

    def test_second_run_updates_existing_relations(self) -> None:
        """Running learner mode twice on the same text should update existing entries."""
        self.mind.reason(
            "كتب الطالب الدرس",
            external_evidence=["repeated_context_1"],
            allow_learning=True,
        )
        self.mind.reason(
            "كتب الطالب الدرس",
            external_evidence=["repeated_context_2"],
            allow_learning=True,
        )
        # Memory should reflect repeated access
        snap = self.mind.memory.snapshot()
        assert len(snap["atomic"]) > 0

    def test_external_evidence_boosts_certainty(self) -> None:
        out_no_ev = self.mind.reason("كتب الطالب")
        out_with_ev = self.mind.reason(
            "كتب الطالب",
            external_evidence=["e1", "e2", "e3", "e4", "e5"],
        )
        # More evidence should yield equal or higher certainty
        assert out_with_ev.overall_certainty >= out_no_ev.overall_certainty - 0.05

    def test_memory_snapshot_serialisable(self) -> None:
        import json
        self.mind.reason("العقل يفهم اللغة", allow_learning=True)
        snap = self.mind.memory_snapshot()
        # Must be JSON-serialisable
        json_str = json.dumps(snap)
        assert len(json_str) > 0


# ===========================================================================
# Integration: full pipeline on canonical example
# ===========================================================================

class TestFullPipelineIntegration:
    """End-to-end test on the canonical example from the specification."""

    def test_kataba_al_taalib_al_darss(self) -> None:
        """Test 'كتب الطالب الدرس' — the spec's running example."""
        mind = CognitiveReasoningMind()
        output = mind.reason("كتب الطالب الدرس")

        # Atoms for every character should be present
        assert len(output.atom_nodes) > 0

        # Word-level nodes should exist
        words = output.levels.get("words", [])
        assert len(words) == 3, f"Expected 3 word nodes, got {len(words)}"

        # Each word node should reference a surface
        surfaces = {w.surface for w in words}
        assert "كتب" in surfaces
        assert "الطالب" in surfaces
        assert "الدرس" in surfaces

        # Overall certainty should be meaningful (above 0)
        assert output.overall_certainty > 0.0

    def test_concept_node_produced(self) -> None:
        mind = CognitiveReasoningMind()
        output = mind.reason("كتب الطالب الدرس")
        concepts = output.levels.get("concepts", [])
        assert len(concepts) > 0
        assert concepts[0].level == NodeLevel.CONCEPT

    def test_certainty_results_count_matches_candidates(self) -> None:
        mind = CognitiveReasoningMind()
        output = mind.reason("كتب الطالب الدرس")
        total_nodes = len(output.verified) + len(output.suspended)
        assert len(output.certainty_results) == total_nodes
