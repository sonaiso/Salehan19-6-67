"""Tests for the Bayani Relational Parser v0.2.

Covers:
1.  Nominal sentence → isnadiyyah
2.  Verbal sentence  → fa_iliyyah + maf_uliyyah
3.  Adjective phrase → taqyidiyyah + possible_mafhoom_sifah
4.  Idafa/possession → unresolved (not failure)
5.  Conditional      → shartiyyah
6.  Exception        → istithnaiyyah
7.  Ghayah           → ghaiyyah
8.  Hal              → haliyyah
9.  Sabab            → sababiyyah
10. Parser output attaches to relational_mapping_layer claims
11. arabic_operator_layer exposes carrier_operator claims
12. Audit prevents judgment when relational layer is skipped/unresolved

Run with:  python -m pytest tests/test_bayani_relational_parser.py -v
"""

from __future__ import annotations

import unittest

from bayani.runtime.relational_parser import (
    GHAIYYAH,
    HALIYYAH,
    ISNADIYYAH,
    ISTITHNAIYYAH,
    MAF_ULIYYAH,
    FA_ILIYYAH,
    MUSABBABIYYAH,
    SABABIYYAH,
    SHARTIYYAH,
    TAQYIDIYYAH,
    BayaniRelation,
    RelationalParseResult,
    parse_relations,
)
from bayani.runtime.contracts import (
    IntentClassificationResult,
    PipelineLayerResult,
    PromptInput,
    PromptTypeResult,
)
from bayani.runtime.layers import (
    arabic_operator_layer,
    relational_mapping_layer,
)
from bayani.runtime.audit import run_audit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _relation_types(result: RelationalParseResult) -> list[str]:
    return [r.relation_type for r in result.relations]


def _get_relation(result: RelationalParseResult, rel_type: str) -> BayaniRelation | None:
    for r in result.relations:
        if r.relation_type == rel_type:
            return r
    return None


# ===========================================================================
# Test 1 — nominal sentence extracts isnadiyyah
# ===========================================================================

class TestIsnadiyyah(unittest.TestCase):

    def test_al_khamr_haram_extracts_isnadiyyah(self):
        """'الخمر حرام' must produce an isnadiyyah relation."""
        result = parse_relations("الخمر حرام")
        self.assertIn(ISNADIYYAH, _relation_types(result),
                      f"Expected isnadiyyah in {_relation_types(result)}")

    def test_isnadiyyah_carrier_is_nominal_sentence(self):
        result = parse_relations("الخمر حرام")
        rel = _get_relation(result, ISNADIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "nominal_sentence")

    def test_isnadiyyah_subject_is_mubtada(self):
        result = parse_relations("الخمر حرام")
        rel = _get_relation(result, ISNADIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.subject, "الخمر")

    def test_isnadiyyah_predicate_is_khabar(self):
        result = parse_relations("الخمر حرام")
        rel = _get_relation(result, ISNADIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "حرام")

    def test_almaau_tahoor_extracts_isnadiyyah(self):
        """'الماء طهور' must also produce isnadiyyah."""
        result = parse_relations("الماء طهور")
        self.assertIn(ISNADIYYAH, _relation_types(result))

    def test_isnadiyyah_forbidden_jumps_present(self):
        result = parse_relations("الخمر حرام")
        rel = _get_relation(result, ISNADIYYAH)
        self.assertIsNotNone(rel)
        self.assertIn(
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
            rel.forbidden_jumps_checked,
        )


# ===========================================================================
# Test 2 — verbal sentence extracts fa_iliyyah and maf_uliyyah
# ===========================================================================

class TestFaIliyyahMafUliyyah(unittest.TestCase):

    def test_akrama_extracts_fa_iliyyah(self):
        """'أكرم المعلم الطلاب' must produce fa_iliyyah."""
        result = parse_relations("أكرم المعلم الطلاب")
        self.assertIn(FA_ILIYYAH, _relation_types(result),
                      f"Expected fa_iliyyah in {_relation_types(result)}")

    def test_akrama_extracts_maf_uliyyah(self):
        """'أكرم المعلم الطلاب' must produce maf_uliyyah."""
        result = parse_relations("أكرم المعلم الطلاب")
        self.assertIn(MAF_ULIYYAH, _relation_types(result),
                      f"Expected maf_uliyyah in {_relation_types(result)}")

    def test_fa_iliyyah_subject_is_verb(self):
        result = parse_relations("أكرم المعلم الطلاب")
        rel = _get_relation(result, FA_ILIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.subject, "أكرم")

    def test_fa_iliyyah_predicate_is_faaил(self):
        result = parse_relations("أكرم المعلم الطلاب")
        rel = _get_relation(result, FA_ILIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "المعلم")

    def test_maf_uliyyah_target_is_object(self):
        result = parse_relations("أكرم المعلم الطلاب")
        rel = _get_relation(result, MAF_ULIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "الطلاب")

    def test_verbal_carrier_is_verb_sentence(self):
        result = parse_relations("أكرم المعلم الطلاب")
        for rel in result.relations:
            if rel.relation_type in (FA_ILIYYAH, MAF_ULIYYAH):
                self.assertEqual(rel.carrier_operator, "verb_sentence")


# ===========================================================================
# Test 3 — adjective phrase extracts taqyidiyyah
# ===========================================================================

class TestTaqyidiyyah(unittest.TestCase):

    def test_altullab_almujtahidoon_extracts_taqyidiyyah(self):
        """'الطلاب المجتهدون' must produce taqyidiyyah."""
        result = parse_relations("الطلاب المجتهدون")
        self.assertIn(TAQYIDIYYAH, _relation_types(result),
                      f"Expected taqyidiyyah in {_relation_types(result)}")

    def test_taqyidiyyah_has_possible_mafhoom_sifah(self):
        result = parse_relations("الطلاب المجتهدون")
        rel = _get_relation(result, TAQYIDIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.possible_usuli_effect, "possible_mafhoom_sifah")

    def test_taqyidiyyah_carrier_is_sifah(self):
        result = parse_relations("الطلاب المجتهدون")
        rel = _get_relation(result, TAQYIDIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "sifah/adjective")

    def test_raqabah_muaminah_extracts_taqyidiyyah(self):
        """'رقبة مؤمنة' (indefinite adj pair) must produce taqyidiyyah."""
        result = parse_relations("رقبة مؤمنة")
        self.assertIn(TAQYIDIYYAH, _relation_types(result))


# ===========================================================================
# Test 4 — idafa / possession is unresolved, not failure
# ===========================================================================

class TestIdafaUnresolved(unittest.TestCase):

    def test_kitab_zayd_does_not_raise(self):
        """parse_relations must never raise for any input."""
        result = parse_relations("كتاب زيد")
        self.assertIsInstance(result, RelationalParseResult)

    def test_kitab_zayd_marked_unresolved_or_relation(self):
        """'كتاب زيد' must either produce a relation or appear in unresolved."""
        result = parse_relations("كتاب زيد")
        has_content = len(result.relations) > 0 or len(result.unresolved) > 0
        self.assertTrue(has_content,
                        "idafa 'كتاب زيد' must produce a relation or unresolved note")

    def test_parse_result_is_relational_parse_result_instance(self):
        result = parse_relations("كتاب زيد")
        self.assertIsInstance(result, RelationalParseResult)
        self.assertEqual(result.source_text, "كتاب زيد")


# ===========================================================================
# Test 5 — conditional extracts shartiyyah
# ===========================================================================

class TestShartiyyah(unittest.TestCase):

    def test_in_tadrus_tanjih_extracts_shartiyyah(self):
        """'إن تدرس تنجح' must produce shartiyyah."""
        result = parse_relations("إن تدرس تنجح")
        self.assertIn(SHARTIYYAH, _relation_types(result))

    def test_shartiyyah_carrier_is_conditional_tool(self):
        result = parse_relations("إن تدرس تنجح")
        rel = _get_relation(result, SHARTIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "conditional_tool")

    def test_itha_conditional_extracts_shartiyyah(self):
        """'إذا جاء الشرط' must produce shartiyyah."""
        result = parse_relations("إذا جاء الشرط")
        self.assertIn(SHARTIYYAH, _relation_types(result))

    def test_shartiyyah_has_usuli_effect(self):
        result = parse_relations("إن تدرس تنجح")
        rel = _get_relation(result, SHARTIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.possible_usuli_effect, "hukm_conditioned")


# ===========================================================================
# Test 6 — exception extracts istithnaiyyah
# ===========================================================================

class TestIstithnaiyyah(unittest.TestCase):

    def test_jaa_alqawm_illa_zayd_extracts_istithnaiyyah(self):
        """'جاء القوم إلا زيدا' must produce istithnaiyyah."""
        result = parse_relations("جاء القوم إلا زيدا")
        self.assertIn(ISTITHNAIYYAH, _relation_types(result))

    def test_istithnaiyyah_carrier_is_exception_tool(self):
        result = parse_relations("جاء القوم إلا زيدا")
        rel = _get_relation(result, ISTITHNAIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "exception_tool")

    def test_istithnaiyyah_takhsis_effect(self):
        result = parse_relations("جاء القوم إلا زيدا")
        rel = _get_relation(result, ISTITHNAIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.possible_usuli_effect, "takhsis_candidate")

    def test_mustathna_is_zayd(self):
        result = parse_relations("جاء القوم إلا زيدا")
        rel = _get_relation(result, ISTITHNAIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "زيدا")


# ===========================================================================
# Test 7 — ghayah extracts ghaiyyah
# ===========================================================================

class TestGhaiyyah(unittest.TestCase):

    def test_atimmoo_alsiyam_extracts_ghaiyyah(self):
        """'أتموا الصيام إلى الليل' must produce ghaiyyah."""
        result = parse_relations("أتموا الصيام إلى الليل")
        self.assertIn(GHAIYYAH, _relation_types(result))

    def test_ghaiyyah_carrier_is_ghayah_tool(self):
        result = parse_relations("أتموا الصيام إلى الليل")
        rel = _get_relation(result, GHAIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "ghayah_tool")

    def test_ghaiyyah_target_is_allayl(self):
        result = parse_relations("أتموا الصيام إلى الليل")
        rel = _get_relation(result, GHAIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "الليل")

    def test_hatta_ghayah_extracts_ghaiyyah(self):
        """'أكلوا حتى الشبع' must produce ghaiyyah."""
        result = parse_relations("أكلوا حتى الشبع")
        # حتى should be detected as a ghayah tool even if أكلوا is not in known verbs
        # Parser may return ghaiyyah regardless of verb recognition
        self.assertIn(GHAIYYAH, _relation_types(result))


# ===========================================================================
# Test 8 — hal extracts haliyyah
# ===========================================================================

class TestHaliyyah(unittest.TestCase):

    def setUp(self):
        self._result = parse_relations("جاء زيد راكبا")

    def test_jaa_zayd_rakiban_extracts_haliyyah(self):
        """'جاء زيد راكبا' must produce haliyyah."""
        self.assertIn(HALIYYAH, _relation_types(self._result))

    def test_haliyyah_carrier_is_hal(self):
        rel = _get_relation(self._result, HALIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "hal")

    def test_haliyyah_subject_is_zayd(self):
        rel = _get_relation(self._result, HALIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.subject, "زيد")

    def test_haliyyah_predicate_is_rakiban(self):
        rel = _get_relation(self._result, HALIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate_or_target, "راكبا")


# ===========================================================================
# Test 9 — sabab extracts sababiyyah
# ===========================================================================

class TestSababiyyah(unittest.TestCase):

    def test_wajaba_aldaman_bisabab_extracts_sababiyyah(self):
        """'وجب الضمان بسبب الإتلاف' must produce sababiyyah."""
        result = parse_relations("وجب الضمان بسبب الإتلاف")
        self.assertIn(SABABIYYAH, _relation_types(result))

    def test_sababiyyah_carrier_is_cause_tool(self):
        result = parse_relations("وجب الضمان بسبب الإتلاف")
        rel = _get_relation(result, SABABIYYAH)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.carrier_operator, "cause_tool")

    def test_sababiyyah_sabab_is_ittilaf(self):
        result = parse_relations("وجب الضمان بسبب الإتلاف")
        rel = _get_relation(result, SABABIYYAH)
        self.assertIsNotNone(rel)
        self.assertIn("الإتلاف", rel.predicate_or_target or "")

    def test_sababiyyah_also_extracts_musabbabiyyah(self):
        """Sababiyyah detection should also produce a musabbabiyyah relation."""
        result = parse_relations("وجب الضمان بسبب الإتلاف")
        self.assertIn(MUSABBABIYYAH, _relation_types(result))


# ===========================================================================
# Test 10 — parser output attaches to relational_mapping_layer claims
# ===========================================================================

class TestRelationalMappingLayerIntegration(unittest.TestCase):

    def test_relational_mapping_layer_has_relations_mapped(self):
        """relational_mapping_layer must include 'relations_mapped' in claims."""
        prompt_input = PromptInput("الخمر حرام")
        result = relational_mapping_layer(prompt_input)
        self.assertIn("relations_mapped", result.claims)

    def test_relational_mapping_layer_attaches_relation_types(self):
        """relational_mapping_layer claims must include the extracted relation types."""
        prompt_input = PromptInput("الخمر حرام")
        result = relational_mapping_layer(prompt_input)
        relation_claims = [c for c in result.claims if c.startswith("relation:")]
        self.assertGreater(len(relation_claims), 0,
                           "Expected at least one relation: claim")
        self.assertIn(f"relation:{ISNADIYYAH}", result.claims)

    def test_relational_mapping_layer_attaches_carrier_operators(self):
        """relational_mapping_layer claims must include carrier_operator entries."""
        prompt_input = PromptInput("الخمر حرام")
        result = relational_mapping_layer(prompt_input)
        carrier_claims = [c for c in result.claims if c.startswith("carrier_operator:")]
        self.assertGreater(len(carrier_claims), 0,
                           "Expected at least one carrier_operator: claim")

    def test_relational_mapping_layer_checks_forbidden_jumps(self):
        """relational_mapping_layer must record relevant forbidden jumps."""
        prompt_input = PromptInput("الخمر حرام")
        result = relational_mapping_layer(prompt_input)
        self.assertIn(
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
            result.forbidden_jumps_checked,
        )

    def test_relational_mapping_layer_unresolved_in_uncertainties(self):
        """Unresolved relations should appear in the layer uncertainties."""
        # "كتاب زيد" is an idafa that the parser marks as unresolved
        prompt_input = PromptInput("كتاب زيد")
        result = relational_mapping_layer(prompt_input)
        # If parser produced unresolved, uncertainties should contain it
        parse_result = parse_relations("كتاب زيد")
        if parse_result.unresolved:
            unresolved_uncertainties = [
                u for u in result.uncertainties if u.startswith("unresolved:")
            ]
            self.assertGreater(len(unresolved_uncertainties), 0)


# ===========================================================================
# Test 11 — arabic_operator_layer exposes carrier_operator claims
# ===========================================================================

class TestArabicOperatorLayerIntegration(unittest.TestCase):

    def test_arabic_operator_layer_has_validated_claim(self):
        prompt_input = PromptInput("الخمر حرام")
        result = arabic_operator_layer(prompt_input)
        self.assertIn("arabic_operators_validated", result.claims)

    def test_arabic_operator_layer_exposes_carrier_operators(self):
        """arabic_operator_layer must list carrier_operator values in claims."""
        prompt_input = PromptInput("الخمر حرام")
        result = arabic_operator_layer(prompt_input)
        carrier_claims = [c for c in result.claims if c.startswith("carrier_operator:")]
        self.assertGreater(len(carrier_claims), 0,
                           "Expected carrier_operator: claims in arabic_operator_layer")

    def test_arabic_operator_layer_verbal_sentence_operator(self):
        """For a verbal sentence, arabic_operator_layer must report verb_sentence."""
        prompt_input = PromptInput("أكرم المعلم الطلاب")
        result = arabic_operator_layer(prompt_input)
        self.assertIn("carrier_operator:verb_sentence", result.claims)

    def test_arabic_operator_layer_nominal_sentence_operator(self):
        """For a nominal sentence, arabic_operator_layer must report nominal_sentence."""
        prompt_input = PromptInput("الخمر حرام")
        result = arabic_operator_layer(prompt_input)
        self.assertIn("carrier_operator:nominal_sentence", result.claims)


# ===========================================================================
# Test 12 — audit prevents judgment if relational layer skipped
# ===========================================================================

class TestAuditRelationalLayerEnforcement(unittest.TestCase):

    def test_audit_flags_judgment_without_relational_mapping(self):
        """Audit must flag violation when judgment_formation_layer runs
        but relational_mapping_layer was not executed."""
        pt = PromptTypeResult("PT-06", "Mantuq Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="hukm_knowledge",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        # Layer results: judgment was run, but relational_mapping was skipped
        layer_results = [
            PipelineLayerResult("reality_grounding_layer", "passed"),
            PipelineLayerResult("essence_assignment_layer", "passed"),
            PipelineLayerResult("domain_assignment_layer", "passed"),
            PipelineLayerResult("judgment_formation_layer", "passed"),
        ]
        required_layers = [
            "reality_grounding_layer",
            "essence_assignment_layer",
            "domain_assignment_layer",
            "relational_mapping_layer",
            "judgment_formation_layer",
            "epistemic_audit_layer",
        ]
        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertFalse(audit.passed)
        violations_text = " ".join(audit.violations)
        self.assertIn("NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
                      violations_text)

    def test_audit_passes_when_relational_mapping_present(self):
        """When relational_mapping_layer is executed, judgment invariant clears."""
        pt = PromptTypeResult("PT-06", "Mantuq Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="hukm_knowledge",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        layer_results = [
            PipelineLayerResult("reality_grounding_layer", "passed"),
            PipelineLayerResult("essence_assignment_layer", "passed"),
            PipelineLayerResult("domain_assignment_layer", "passed"),
            PipelineLayerResult("relational_mapping_layer", "passed",
                                claims=["relations_mapped"]),
            PipelineLayerResult("judgment_formation_layer", "passed"),
            PipelineLayerResult("epistemic_audit_layer", "passed"),
        ]
        required_layers = [
            "reality_grounding_layer",
            "essence_assignment_layer",
            "domain_assignment_layer",
            "relational_mapping_layer",
            "judgment_formation_layer",
            "epistemic_audit_layer",
        ]
        audit = run_audit(pt, intent, required_layers, layer_results)
        # NoJudgmentFormationBeforeEssenceDomainRelationsResolved must not fire
        violations_text = " ".join(audit.violations)
        self.assertNotIn(
            "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
            violations_text,
        )

    def test_audit_flags_no_relation_without_carrier(self):
        """Audit must flag NoRelationWithoutCarrier when the layer signals it."""
        pt = PromptTypeResult("PT-01", "Existence Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="existence_check",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        # Manually craft a relational_mapping_layer result with a missing-carrier warning
        layer_results = [
            PipelineLayerResult(
                "relational_mapping_layer",
                "passed",
                claims=[
                    "relations_mapped",
                    "warning:relation_without_carrier_detected:isnadiyyah",
                ],
            ),
            PipelineLayerResult("epistemic_audit_layer", "passed"),
        ]
        required_layers = [
            "relational_mapping_layer",
            "epistemic_audit_layer",
        ]
        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertFalse(audit.passed)
        violations_text = " ".join(audit.violations)
        self.assertIn("NoRelationWithoutCarrier", violations_text)


# ===========================================================================
# Additional parser robustness tests
# ===========================================================================

class TestParserRobustness(unittest.TestCase):

    def test_empty_string_does_not_raise(self):
        result = parse_relations("")
        self.assertIsInstance(result, RelationalParseResult)
        self.assertIn("empty_input", result.notes)

    def test_parse_result_source_text_preserved(self):
        text = "الخمر حرام"
        result = parse_relations(text)
        self.assertEqual(result.source_text, text)

    def test_all_relations_have_carrier_operator(self):
        """Every extracted relation must have a non-None carrier_operator."""
        test_cases = [
            "الخمر حرام",
            "أكرم المعلم الطلاب",
            "إن تدرس تنجح",
            "جاء القوم إلا زيدا",
            "أتموا الصيام إلى الليل",
            "جاء زيد راكبا",
            "وجب الضمان بسبب الإتلاف",
        ]
        for text in test_cases:
            result = parse_relations(text)
            for rel in result.relations:
                self.assertIsNotNone(
                    rel.carrier_operator,
                    f"Relation {rel.relation_type!r} from {text!r} "
                    "has carrier_operator=None",
                )

    def test_all_relations_have_confidence_in_range(self):
        for text in ["الخمر حرام", "أكرم المعلم الطلاب", "جاء زيد راكبا"]:
            result = parse_relations(text)
            for rel in result.relations:
                self.assertGreater(rel.confidence, 0.0)
                self.assertLessEqual(rel.confidence, 1.0)

    def test_notes_always_populated(self):
        result = parse_relations("الخمر حرام")
        self.assertGreater(len(result.notes), 0)

    def test_tadmin_pattern_detected(self):
        """'البيع يتضمن مبادلة' must produce tadminiyyah."""
        from bayani.runtime.relational_parser import TADMINIYYAH
        result = parse_relations("البيع يتضمن مبادلة")
        self.assertIn(TADMINIYYAH, _relation_types(result))


if __name__ == "__main__":
    unittest.main()
