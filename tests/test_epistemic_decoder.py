"""Tests for the Epistemic Cognitive Decoder.

Covers all seven pipeline units and the end-to-end decoder:

- test_input_analyzer          — Unit 1
- test_reality_extractor       — Unit 2
- test_semiotic_parser         — Unit 3
- test_relation_graph_builder  — Unit 4
- test_evidence_retriever      — Unit 5
- test_certainty_scorer        — Unit 6
- test_answer_decoder          — Unit 7
- test_epistemic_decoder_e2e   — full pipeline
- test_knowledge_files         — YAML/MD file validation
- test_certainty_score_formula — scoring formula

Run with::

    python -m pytest tests/test_epistemic_decoder.py -v
"""

from __future__ import annotations

import unittest
from pathlib import Path

from bayani.epistemic_decoder.contracts import (
    CertaintyScore,
    DecoderInput,
    EvidenceBundle,
    EvidenceItem,
    RelationEdge,
    RelationGraph,
    RealityExtractionResult,
    SemioticMap,
    SignifierEntry,
    TaskAnalysis,
    VerifiedThought,
)
from bayani.epistemic_decoder.units import (
    AnswerDecoder,
    CertaintyScorer,
    EvidenceRetriever,
    InputAnalyzer,
    RealityExtractor,
    RelationGraphBuilder,
    SemioticParser,
)
from bayani.epistemic_decoder.decoder import EpistemicCognitiveDecoder

_ROOT = Path(__file__).resolve().parents[1]
_DECODER_DIR = _ROOT / "bayani" / "epistemic_decoder"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DECODER = EpistemicCognitiveDecoder()


def _make_input(query: str, effort: str = "high") -> DecoderInput:
    return DecoderInput(query=query, reasoning_effort=effort)


# ===========================================================================
# Unit 1 — Input Analyzer
# ===========================================================================

class TestInputAnalyzer(unittest.TestCase):

    def setUp(self):
        self.unit = InputAnalyzer()

    def _run(self, query: str, effort: str = "high") -> TaskAnalysis:
        return self.unit(_make_input(query, effort))

    def test_returns_task_analysis(self):
        result = self._run("ما المفهوم؟")
        self.assertIsInstance(result, TaskAnalysis)

    def test_epistemology_domain_detected(self):
        result = self._run("ما اليقين؟")
        self.assertEqual(result.domain, "epistemology_language_reasoning")

    def test_fiqh_domain_detected(self):
        result = self._run("ما حكم هذه المسألة في الفقه؟")
        self.assertEqual(result.domain, "islamic_jurisprudence")

    def test_comparative_task_type(self):
        result = self._run("ما الفرق بين العلم والثقافة؟")
        self.assertEqual(result.task_type, "comparative_analysis")

    def test_conceptual_task_type(self):
        result = self._run("اشرح لي مفهوم العقل.")
        self.assertEqual(result.task_type, "conceptual_modeling")

    def test_requires_reality_grounding(self):
        result = self._run("ما الواقع؟")
        self.assertTrue(result.requires_reality_grounding)

    def test_complexity_from_effort(self):
        result_low = self._run("سؤال بسيط", effort="low")
        result_xhigh = self._run("سؤال معقد", effort="xhigh")
        self.assertEqual(result_low.complexity, "simple")
        self.assertEqual(result_xhigh.complexity, "deep")

    def test_hallucination_risk_high_for_epistemology(self):
        result = self._run("ما اليقين والمعرفة؟")
        self.assertEqual(result.risk_of_hallucination, "high")


# ===========================================================================
# Unit 2 — Reality Extractor
# ===========================================================================

class TestRealityExtractor(unittest.TestCase):

    def setUp(self):
        self.unit = RealityExtractor()
        self.analyzer = InputAnalyzer()

    def _run(self, query: str) -> RealityExtractionResult:
        inp = _make_input(query)
        task = self.analyzer(inp)
        return self.unit(task, inp)

    def test_returns_reality_result(self):
        result = self._run("ما المفهوم؟")
        self.assertIsInstance(result, RealityExtractionResult)

    def test_reality_objects_extracted(self):
        result = self._run("ما الفرق بين العلم والثقافة؟")
        self.assertGreater(len(result.reality_objects), 0)

    def test_textual_reality_for_nass(self):
        result = self._run("ما معنى هذا النص؟")
        self.assertEqual(result.reality_type, "textual")

    def test_cognitive_reality_for_thinking_concepts(self):
        result = self._run("ما اليقين والمعرفة والإدراك؟")
        self.assertEqual(result.reality_type, "conceptual_human_cognition")

    def test_evidence_needed_populated(self):
        result = self._run("ما اليقين؟")
        self.assertGreater(len(result.evidence_needed), 0)

    def test_indirect_sensory_access_default(self):
        result = self._run("ما المفهوم؟")
        self.assertIn(result.sensory_access, ("indirect", "textual", "direct"))


# ===========================================================================
# Unit 3 — Semiotic Parser
# ===========================================================================

class TestSemioticParser(unittest.TestCase):

    def setUp(self):
        self.unit = SemioticParser()
        self.analyzer = InputAnalyzer()
        self.extractor = RealityExtractor()

    def _run(self, query: str) -> SemioticMap:
        inp = _make_input(query)
        task = self.analyzer(inp)
        reality = self.extractor(task, inp)
        return self.unit(inp, reality)

    def test_returns_semiotic_map(self):
        result = self._run("ما اليقين؟")
        self.assertIsInstance(result, SemioticMap)

    def test_signifiers_not_empty(self):
        result = self._run("ما الفرق بين العلم والثقافة؟")
        self.assertGreater(len(result.signifiers), 0)

    def test_signifier_has_semantic_mode(self):
        result = self._run("ما اليقين؟")
        for s in result.signifiers:
            self.assertIsInstance(s.semantic_mode, list)
            self.assertIn("مطابقة", s.semantic_mode)

    def test_signifier_entries_are_correct_type(self):
        result = self._run("الإنسان حيوان ناطق")
        for entry in result.signifiers:
            self.assertIsInstance(entry, SignifierEntry)

    def test_yaqeen_detected_as_epistemic_attribute(self):
        result = self._run("اليقين")
        texts = [s.text for s in result.signifiers]
        self.assertIn("اليقين", texts)


# ===========================================================================
# Unit 4 — Relation Graph Builder
# ===========================================================================

class TestRelationGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.unit = RelationGraphBuilder()

    def _build_graph(self, query: str) -> RelationGraph:
        analyzer = InputAnalyzer()
        extractor = RealityExtractor()
        parser = SemioticParser()
        inp = _make_input(query)
        task = analyzer(inp)
        reality = extractor(task, inp)
        semiotic_map = parser(inp, reality)
        return self.unit(semiotic_map, reality)

    def test_returns_relation_graph(self):
        result = self._build_graph("ما اليقين؟")
        self.assertIsInstance(result, RelationGraph)

    def test_relations_not_empty(self):
        result = self._build_graph("ما اليقين؟")
        self.assertGreater(len(result.relations), 0)

    def test_default_cognitive_pipeline_relations(self):
        result = self._build_graph("أي سؤال")
        from_nodes = {r.from_node for r in result.relations}
        self.assertIn("واقع", from_nodes)
        self.assertIn("حس", from_nodes)

    def test_edges_have_carrier_operator(self):
        result = self._build_graph("الإنسان يتعلم")
        for edge in result.relations:
            self.assertIsInstance(edge, RelationEdge)

    def test_relation_types_are_strings(self):
        result = self._build_graph("العقل يحتاج الواقع")
        for edge in result.relations:
            self.assertIsInstance(edge.relation_type, str)


# ===========================================================================
# Unit 5 — Evidence Retriever
# ===========================================================================

class TestEvidenceRetriever(unittest.TestCase):

    def setUp(self):
        self.unit = EvidenceRetriever()

    def _run(self, query: str) -> EvidenceBundle:
        analyzer = InputAnalyzer()
        extractor = RealityExtractor()
        builder = RelationGraphBuilder()
        parser = SemioticParser()
        inp = _make_input(query)
        task = analyzer(inp)
        reality = extractor(task, inp)
        semiotic_map = parser(inp, reality)
        graph = builder(semiotic_map, reality)
        return self.unit(reality, graph)

    def test_returns_evidence_bundle(self):
        result = self._run("ما اليقين؟")
        self.assertIsInstance(result, EvidenceBundle)

    def test_evidence_items_not_empty(self):
        result = self._run("ما اليقين؟")
        self.assertGreater(len(result.items), 0)

    def test_policy_item_always_present(self):
        result = self._run("سؤال عشوائي")
        sources = [item.source for item in result.items]
        self.assertIn("decoder_policy.md", sources)

    def test_evidence_strength_valid_values(self):
        result = self._run("ما المفهوم؟")
        valid_strengths = {"high", "medium", "low"}
        for item in result.items:
            self.assertIn(item.strength, valid_strengths)

    def test_evidence_items_are_correct_type(self):
        result = self._run("ما الواقع؟")
        for item in result.items:
            self.assertIsInstance(item, EvidenceItem)


# ===========================================================================
# Unit 6 — Certainty Scorer
# ===========================================================================

class TestCertaintyScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = CertaintyScorer()
        self._evidence = EvidenceBundle(items=[
            EvidenceItem(source="test", content="دليل", strength="high"),
        ])
        self._reality = RealityExtractionResult(
            reality_objects=["مفهوم"],
            reality_type="conceptual_human_cognition",
            sensory_access="indirect",
        )
        self._graph = RelationGraph(relations=[
            RelationEdge("واقع", "ينقل", "حس", "sababiyya", "cause_tool"),
        ])

    def _score(self, thought: str) -> CertaintyScore:
        return self.scorer(thought, self._evidence, self._reality, self._graph)

    def test_returns_certainty_score(self):
        result = self._score("العقل يحتاج واقعًا")
        self.assertIsInstance(result, CertaintyScore)

    def test_score_between_zero_and_one(self):
        result = self._score("العقل يحتاج واقعًا")
        self.assertGreaterEqual(result.answer_score, 0.0)
        self.assertLessEqual(result.answer_score, 1.0)

    def test_reality_grounded_when_type_known(self):
        result = self._score("العقل يحتاج واقعًا")
        self.assertTrue(result.reality_grounded)

    def test_evidence_present_when_high_evidence_exists(self):
        result = self._score("العقل يحتاج واقعًا")
        self.assertTrue(result.evidence_present)

    def test_certainty_level_is_string(self):
        result = self._score("الفكر ينتج عن الربط")
        self.assertIsInstance(result.certainty_level, str)

    def test_passes_threshold_at_0_60(self):
        result = self._score("العقل يحتاج واقعًا")
        # With good reality + evidence it should pass
        self.assertTrue(result.passes_threshold(0.60))


# ===========================================================================
# Certainty Score Formula
# ===========================================================================

class TestCertaintyScoreFormula(unittest.TestCase):

    def test_formula_gives_correct_value(self):
        score = CertaintyScore(claim="test")
        result = score.compute_score(
            linguistic_coherence=1.0,
            reality_match=1.0,
            evidence_strength=1.0,
            semantic_validity=1.0,
            inference_validity=1.0,
            certainty_clarity=1.0,
            hallucination_risk=0.0,
        )
        expected = 0.20 + 0.25 + 0.20 + 0.15 + 0.10 + 0.10
        self.assertAlmostEqual(result, expected, places=4)

    def test_hallucination_risk_reduces_score(self):
        score_low_risk = CertaintyScore(claim="a")
        score_high_risk = CertaintyScore(claim="b")
        score_low_risk.compute_score(
            linguistic_coherence=0.8,
            reality_match=0.8,
            evidence_strength=0.8,
            semantic_validity=0.8,
            inference_validity=0.8,
            certainty_clarity=0.8,
            hallucination_risk=0.0,
        )
        score_high_risk.compute_score(
            linguistic_coherence=0.8,
            reality_match=0.8,
            evidence_strength=0.8,
            semantic_validity=0.8,
            inference_validity=0.8,
            certainty_clarity=0.8,
            hallucination_risk=1.0,
        )
        self.assertGreater(score_low_risk.answer_score, score_high_risk.answer_score)

    def test_threshold_check(self):
        score = CertaintyScore(claim="test", answer_score=0.75)
        self.assertTrue(score.passes_threshold(0.60))
        self.assertFalse(score.passes_threshold(0.80))

    def test_score_never_below_zero(self):
        score = CertaintyScore(claim="test")
        result = score.compute_score(
            linguistic_coherence=0.0,
            reality_match=0.0,
            evidence_strength=0.0,
            semantic_validity=0.0,
            inference_validity=0.0,
            certainty_clarity=0.0,
            hallucination_risk=1.0,
        )
        self.assertGreaterEqual(result, 0.0)


# ===========================================================================
# Unit 7 — Answer Decoder
# ===========================================================================

class TestAnswerDecoder(unittest.TestCase):

    def setUp(self):
        self.decoder_unit = AnswerDecoder()
        self.task = TaskAnalysis(
            task_type="conceptual_modeling",
            domain="epistemology_language_reasoning",
        )
        self.reality = RealityExtractionResult(
            reality_objects=["مفهوم"],
            reality_type="conceptual_human_cognition",
            sensory_access="indirect",
        )
        self.evidence = EvidenceBundle(items=[
            EvidenceItem(source="test", content="دليل قوي", strength="high"),
        ])

    def _make_verified(self, claim: str, score_val: float) -> VerifiedThought:
        s = CertaintyScore(claim=claim, answer_score=score_val)
        s.certainty_level = "معرفة راجحة"
        return VerifiedThought(claim=claim, score=s)

    def test_returns_decoder_output(self):
        from bayani.epistemic_decoder.contracts import DecoderOutput
        vt = self._make_verified("العقل يحتاج واقعًا", 0.75)
        result = self.decoder_unit([vt], self.task, self.reality, self.evidence)
        self.assertIsInstance(result, DecoderOutput)

    def test_final_answer_not_empty_when_thoughts_verified(self):
        vt = self._make_verified("العقل يحتاج واقعًا", 0.75)
        result = self.decoder_unit([vt], self.task, self.reality, self.evidence)
        self.assertTrue(len(result.final_answer) > 0)

    def test_blocked_when_no_verified_thoughts(self):
        result = self.decoder_unit([], self.task, self.reality, self.evidence)
        self.assertTrue(result.blocked)

    def test_certainty_level_from_best_thought(self):
        vt = self._make_verified("الفكر ينتج عن الربط", 0.80)
        result = self.decoder_unit([vt], self.task, self.reality, self.evidence)
        self.assertEqual(result.certainty_level, "معرفة راجحة")

    def test_known_claims_included_in_output(self):
        vt1 = self._make_verified("أ", 0.70)
        vt2 = self._make_verified("ب", 0.75)
        result = self.decoder_unit([vt1, vt2], self.task, self.reality, self.evidence)
        self.assertIn("أ", result.known)
        self.assertIn("ب", result.known)


# ===========================================================================
# End-to-end decoder tests
# ===========================================================================

class TestEpistemicDecoderE2E(unittest.TestCase):

    def test_decode_returns_output(self):
        from bayani.epistemic_decoder.contracts import DecoderOutput
        output = DECODER.decode("ما الفرق بين العلم والثقافة؟")
        self.assertIsInstance(output, DecoderOutput)

    def test_decode_epistemic_query(self):
        output = DECODER.decode("ما اليقين؟")
        self.assertIsNotNone(output.task)
        self.assertIsNotNone(output.reality)
        self.assertIsNotNone(output.semiotic_map)
        self.assertIsNotNone(output.relation_graph)
        self.assertIsNotNone(output.evidence)

    def test_decode_final_answer_not_empty(self):
        output = DECODER.decode("ما المفهوم؟")
        self.assertGreater(len(output.final_answer), 0)

    def test_decode_produces_certainty_level(self):
        output = DECODER.decode("هل المفاهيم مرتبطة بالواقع؟")
        self.assertIsInstance(output.certainty_level, str)

    def test_decode_answer_score_in_range(self):
        output = DECODER.decode("ما الحضارة؟")
        self.assertGreaterEqual(output.answer_score, 0.0)
        self.assertLessEqual(output.answer_score, 1.0)

    def test_decode_with_low_effort(self):
        output = DECODER.decode("ما الواقع؟", reasoning_effort="low")
        self.assertIsNotNone(output)
        self.assertEqual(output.task.complexity, "simple")

    def test_decode_with_xhigh_effort(self):
        output = DECODER.decode(
            "هل العقل يحتاج حسًا ومعلومات سابقة وواقعًا لإنتاج الفكر؟",
            reasoning_effort="xhigh",
        )
        self.assertEqual(output.task.complexity, "deep")

    def test_decode_relation_graph_built(self):
        output = DECODER.decode("الإنسان يتعلم بالحس والتجربة.")
        self.assertIsNotNone(output.relation_graph)
        self.assertGreater(len(output.relation_graph.relations), 0)

    def test_decode_evidence_bundle_present(self):
        output = DECODER.decode("ما الحكم؟")
        self.assertIsNotNone(output.evidence)
        self.assertGreater(len(output.evidence.items), 0)

    def test_decode_semiotic_map_populated(self):
        output = DECODER.decode("اليقين معرفة مطابقة للواقع.")
        self.assertIsNotNone(output.semiotic_map)
        self.assertGreater(len(output.semiotic_map.signifiers), 0)

    def test_blocked_output_has_reason(self):
        # Force a blocked output by using a custom threshold of 1.0
        decoder = EpistemicCognitiveDecoder(knowledge_threshold=1.0)
        output = decoder.decode("ما؟")
        # May or may not be blocked depending on score, but block_reason should be str
        self.assertIsInstance(output.block_reason, str)

    def test_custom_evidence_retriever_accepted(self):
        from bayani.epistemic_decoder.units import EvidenceRetriever

        class FakeRetriever(EvidenceRetriever):
            def _retrieve_from_backend(self, entity, reality_type):
                return [EvidenceItem(
                    source="fake",
                    content="دليل مزيّف",
                    strength="high",
                )]

        decoder = EpistemicCognitiveDecoder(evidence_retriever=FakeRetriever())
        output = decoder.decode("ما الدليل؟")
        sources = [item.source for item in output.evidence.items]
        self.assertIn("fake", sources)


# ===========================================================================
# Knowledge file validation
# ===========================================================================

class TestKnowledgeFiles(unittest.TestCase):

    def test_ontology_yaml_exists(self):
        self.assertTrue((_DECODER_DIR / "ontology.yaml").exists())

    def test_semiotics_yaml_exists(self):
        self.assertTrue((_DECODER_DIR / "semiotics.yaml").exists())

    def test_relations_yaml_exists(self):
        self.assertTrue((_DECODER_DIR / "relations.yaml").exists())

    def test_decoder_policy_md_exists(self):
        self.assertTrue((_DECODER_DIR / "decoder_policy.md").exists())

    def test_ontology_yaml_valid(self):
        try:
            import yaml
            with open(_DECODER_DIR / "ontology.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self.assertIn("ontology_levels", data)
            self.assertIn("cognitive_pipeline", data)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_semiotics_yaml_valid(self):
        try:
            import yaml
            with open(_DECODER_DIR / "semiotics.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self.assertIn("signifier_modes", data)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_relations_yaml_valid(self):
        try:
            import yaml
            with open(_DECODER_DIR / "relations.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self.assertIn("relation_types", data)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_decoder_policy_contains_allow_rules(self):
        policy = (_DECODER_DIR / "decoder_policy.md").read_text(encoding="utf-8")
        self.assertIn("ALLOW", policy)

    def test_decoder_policy_contains_block_rules(self):
        policy = (_DECODER_DIR / "decoder_policy.md").read_text(encoding="utf-8")
        self.assertIn("BLOCK", policy)

    def test_decoder_policy_contains_formula(self):
        policy = (_DECODER_DIR / "decoder_policy.md").read_text(encoding="utf-8")
        self.assertIn("AnswerScore", policy)

    def test_ontology_levels_include_required_concepts(self):
        try:
            import yaml
            with open(_DECODER_DIR / "ontology.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            ids = {lvl["id"] for lvl in data["ontology_levels"]}
            for required in ("reality", "sense", "information", "linking", "thought", "concept", "certainty"):
                self.assertIn(required, ids)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_relations_yaml_includes_isnad_and_sababiyya(self):
        try:
            import yaml
            with open(_DECODER_DIR / "relations.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            ids = {r["id"] for r in data["relation_types"]}
            self.assertIn("isnad", ids)
            self.assertIn("sababiyya", ids)
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_semiotics_dal_only_includes_mutabaqa(self):
        try:
            import yaml
            with open(_DECODER_DIR / "semiotics.yaml", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            dal_only = next(
                m for m in data["signifier_modes"] if m["id"] == "dal_only"
            )
            rel_ids = {r["id"] for r in dal_only["semantic_relations"]}
            self.assertIn("mutabaqa", rel_ids)
            self.assertIn("tadammun", rel_ids)
            self.assertIn("iltizam", rel_ids)
        except ImportError:
            self.skipTest("PyYAML not installed")


# ===========================================================================
# run_decoder.py — module-level validation
# ===========================================================================

class TestRunDecoderModule(unittest.TestCase):

    def test_run_decoder_exists(self):
        path = _ROOT / "run_decoder.py"
        self.assertTrue(path.exists())

    def test_run_function_returns_dict(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_decoder", str(_ROOT / "run_decoder.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.run(
            query="ما الفرق بين العلم والثقافة؟",
            reasoning_effort="high",
            verbose=False,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("certainty_level", result)
        self.assertIn("answer_score", result)
        self.assertIn("final_answer", result)

    def test_knowledge_files_loadable(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_decoder", str(_ROOT / "run_decoder.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Should not raise FileNotFoundError
        try:
            knowledge = mod.load_knowledge_files()
            self.assertIn("policy", knowledge)
            self.assertIn("ontology", knowledge)
            self.assertIn("semiotics", knowledge)
            self.assertIn("relations", knowledge)
        except FileNotFoundError as exc:
            self.fail(f"load_knowledge_files raised FileNotFoundError: {exc}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
