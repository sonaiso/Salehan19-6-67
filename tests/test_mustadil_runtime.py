"""Tests for the Bayani Mustadil Runtime Engine.

Covers the full pipeline:
- test_runtime_engine.py       — end-to-end engine tests
- test_prompt_type_routing.py  — PT classifier + router
- test_mpc_intent_layers.py    — MPC intent classifier
- test_forbidden_jumps_runtime.py — invariant/jump enforcement
- test_epistemic_trace.py      — trace recording

All five test modules are included in this single file for convenience.
Run with:  python -m pytest tests/test_mustadil_runtime.py -v
"""

from __future__ import annotations

import unittest

from bayani.runtime.contracts import PromptInput
from bayani.runtime.engine import MustadilRuntimeEngine
from bayani.runtime.classifier import prompt_type_classifier, mustadil_prompt_classifier
from bayani.runtime.router import get_required_layers
from bayani.runtime.layers import LAYER_REGISTRY
from bayani.runtime.audit import run_audit
from bayani.runtime.trace import build_trace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENGINE = MustadilRuntimeEngine()


def _run(prompt: str, mode: str = "analysis"):
    return ENGINE.run(prompt, mode=mode)


# ===========================================================================
# test_runtime_engine — end-to-end engine tests
# ===========================================================================

class TestRuntimeEngine(unittest.TestCase):

    def test_engine_returns_mustadil_output(self):
        output = _run("هل العام قطعي؟")
        self.assertIsNotNone(output)
        self.assertIsNotNone(output.prompt_type)
        self.assertIsNotNone(output.intent)
        self.assertIsNotNone(output.audit)
        self.assertIsNotNone(output.trace)

    def test_engine_classifies_general_specific_prompt(self):
        output = _run("هل العام قطعي؟")
        self.assertEqual(output.prompt_type, "PT-08")

    def test_engine_classifies_application_prompt(self):
        output = _run("طبّق هذا الحكم على واقعة معينة.")
        self.assertEqual(output.prompt_type, "PT-10")

    def test_engine_classifies_illah_qiyas_prompt(self):
        output = _run("هل الإسكار علة التحريم؟")
        self.assertEqual(output.prompt_type, "PT-09")

    def test_engine_classifies_mafhoom_prompt(self):
        output = _run("ما مفهوم المخالفة في هذا النص؟")
        self.assertEqual(output.prompt_type, "PT-07")

    def test_engine_classifies_existence_prompt(self):
        output = _run("هل ورد هذا اللفظ في النص؟")
        self.assertEqual(output.prompt_type, "PT-01")

    def test_engine_required_layers_not_empty(self):
        output = _run("هل العام قطعي؟")
        self.assertGreater(len(output.required_layers), 0)

    def test_engine_layer_results_match_required_layers(self):
        output = _run("هل العام قطعي؟")
        executed_names = [r.layer_name for r in output.layer_results]
        for layer in output.required_layers:
            self.assertIn(layer, executed_names)

    def test_engine_audit_passed_for_normal_prompt(self):
        output = _run("هل العام قطعي؟")
        self.assertTrue(output.audit.passed)

    def test_engine_certainty_map_has_required_fields(self):
        output = _run("هل العام قطعي؟")
        cm = output.audit.certainty_map
        for field in ("text_existence", "word_meaning", "scope", "external_application"):
            self.assertIn(field, cm, f"certainty_map missing field: {field}")

    def test_engine_trace_has_steps(self):
        output = _run("هل العام قطعي؟")
        self.assertGreater(len(output.trace.steps), 0)

    def test_engine_final_rank_is_structured_answer_allowed(self):
        output = _run("هل العام قطعي؟")
        self.assertEqual(output.audit.final_rank, "structured_answer_allowed")

    def test_engine_jumps_prevented_list_is_not_empty(self):
        output = _run("طبّق هذا الحكم على واقعة معينة.")
        self.assertGreater(len(output.audit.jumps_prevented), 0)


# ===========================================================================
# test_prompt_type_routing — PT classifier + router
# ===========================================================================

class TestPromptTypeRouting(unittest.TestCase):

    # --- Classifier ---

    def test_pt01_existence_classified(self):
        result = prompt_type_classifier("هل هذا النص موجود؟")
        self.assertEqual(result.type_id, "PT-01")

    def test_pt02_definition_classified(self):
        result = prompt_type_classifier("ما معنى القياس؟")
        self.assertEqual(result.type_id, "PT-02")

    def test_pt05_linguistic_classified(self):
        result = prompt_type_classifier("أعرب هذه الجملة")
        self.assertEqual(result.type_id, "PT-05")

    def test_pt06_mantuq_classified(self):
        result = prompt_type_classifier("ما المنطوق في هذه الآية؟")
        self.assertEqual(result.type_id, "PT-06")

    def test_pt07_mafhoom_classified(self):
        result = prompt_type_classifier("ما مفهوم المخالفة في هذا النص؟")
        self.assertEqual(result.type_id, "PT-07")

    def test_pt08_general_specific_classified(self):
        result = prompt_type_classifier("هل العام قطعي الدلالة؟")
        self.assertEqual(result.type_id, "PT-08")

    def test_pt09_illah_classified(self):
        result = prompt_type_classifier("هل الإسكار علة التحريم؟")
        self.assertEqual(result.type_id, "PT-09")

    def test_pt10_application_classified(self):
        result = prompt_type_classifier("طبّق الحكم على هذه الواقعة.")
        self.assertEqual(result.type_id, "PT-10")

    # --- Router ---

    def test_pt07_routes_mantuq_before_mafhoom(self):
        """PT-07 must enter mantuq_layer before mafhoom_layer (spec invariant)."""
        layers = get_required_layers("PT-07")
        self.assertIn("mantuq_layer", layers)
        self.assertIn("mafhoom_layer", layers)
        mantuq_idx = layers.index("mantuq_layer")
        mafhoom_idx = layers.index("mafhoom_layer")
        self.assertLess(mantuq_idx, mafhoom_idx,
                        "mantuq_layer must precede mafhoom_layer for PT-07")

    def test_pt10_routes_tahqeeq_before_application(self):
        """PT-10 must include tahqeeq_manat_layer before application_layer."""
        layers = get_required_layers("PT-10")
        self.assertIn("tahqeeq_manat_layer", layers)
        self.assertIn("application_layer", layers)
        tahqeeq_idx = layers.index("tahqeeq_manat_layer")
        app_idx = layers.index("application_layer")
        self.assertLess(tahqeeq_idx, app_idx,
                        "tahqeeq_manat_layer must precede application_layer for PT-10")

    def test_pt09_routes_causal_before_tahqeeq(self):
        """PT-09 must include causal_juridical_relations_layer before tahqeeq."""
        layers = get_required_layers("PT-09")
        self.assertIn("causal_juridical_relations_layer", layers)
        causal_idx = layers.index("causal_juridical_relations_layer")
        tahqeeq_idx = layers.index("tahqeeq_manat_layer")
        self.assertLess(causal_idx, tahqeeq_idx,
                        "causal_juridical_relations_layer must precede tahqeeq_manat_layer for PT-09")

    def test_all_pt_types_end_with_audit_layer(self):
        for pt_id in [f"PT-{i:02d}" for i in range(1, 11)]:
            layers = get_required_layers(pt_id)
            self.assertEqual(layers[-1], "epistemic_audit_layer",
                             f"{pt_id} must end with epistemic_audit_layer")

    def test_all_pt_types_start_with_base_layers(self):
        for pt_id in [f"PT-{i:02d}" for i in range(1, 11)]:
            layers = get_required_layers(pt_id)
            self.assertIn("reality_grounding_layer", layers)
            self.assertIn("prior_opinion_filter_layer", layers)

    def test_unknown_pt_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_required_layers("PT-99")


# ===========================================================================
# test_mpc_intent_layers — MPC intent classifier
# ===========================================================================

class TestMPCIntentLayers(unittest.TestCase):

    def test_mpc_all_layers_activated(self):
        result = mustadil_prompt_classifier("ما العام وهل هو قطعي؟")
        for i in range(1, 12):
            mpc_id = f"MPC-{i:02d}"
            self.assertIn(mpc_id, result.mpc_layers_activated,
                          f"MPC layer {mpc_id} must always be activated")

    def test_mpc_application_prompt_sets_tahqeeq(self):
        result = mustadil_prompt_classifier("طبّق هذا الحكم على واقعة معينة.")
        self.assertTrue(result.tahqeeq_manat_required)

    def test_mpc_tarjih_prompt_sets_tarjih_flag(self):
        result = mustadil_prompt_classifier("رجّح بين القولين.")
        self.assertTrue(result.tarjih_required)

    def test_mpc_hukm_istinbat_mode(self):
        result = mustadil_prompt_classifier("استنبط الحكم من هذا النص.")
        self.assertEqual(result.hukm_mode, "istinbat")

    def test_mpc_malakah_mode(self):
        result = mustadil_prompt_classifier("كيف تبني ملكة الفقه؟")
        self.assertTrue(result.malakah_mode)

    def test_mpc_primary_purpose_is_set(self):
        result = mustadil_prompt_classifier("ما معنى القياس؟")
        self.assertIsNotNone(result.primary_purpose)
        self.assertGreater(len(result.primary_purpose), 0)

    def test_mpc_schema_construction_intent(self):
        result = mustadil_prompt_classifier("أنشئ schema لتصنيف الأحكام.")
        self.assertTrue(result.construction_intent)


# ===========================================================================
# test_forbidden_jumps_runtime — invariant/jump enforcement
# ===========================================================================

class TestForbiddenJumpsRuntime(unittest.TestCase):

    def test_pt07_engine_prevents_mafhoom_without_mantuq(self):
        """PT-07 pipeline must include mantuq before mafhoom (via engine)."""
        output = _run("ما مفهوم المخالفة في هذا النص؟")
        executed = [r.layer_name for r in output.layer_results]
        if "mafhoom_layer" in executed:
            mantuq_idx = executed.index("mantuq_layer")
            mafhoom_idx = executed.index("mafhoom_layer")
            self.assertLess(mantuq_idx, mafhoom_idx)

    def test_pt10_engine_prevents_application_without_tahqeeq(self):
        """PT-10 pipeline must include tahqeeq before application (via engine)."""
        output = _run("طبّق هذا الحكم على واقعة معينة.")
        executed = [r.layer_name for r in output.layer_results]
        self.assertIn("tahqeeq_manat_layer", executed,
                      "tahqeeq_manat_layer must run for PT-10")
        self.assertIn("application_layer", executed,
                      "application_layer must run for PT-10")
        tahqeeq_idx = executed.index("tahqeeq_manat_layer")
        app_idx = executed.index("application_layer")
        self.assertLess(tahqeeq_idx, app_idx)

    def test_audit_blocks_application_without_tahqeeq(self):
        """Audit must flag NoApplicationWithoutTahqeeqManat when tahqeeq is missing."""
        from bayani.runtime.contracts import (
            IntentClassificationResult, PipelineLayerResult, PromptTypeResult
        )
        from bayani.runtime.audit import run_audit

        pt = PromptTypeResult("PT-10", "Application Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="tahqeeq_manat",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        # Layer results WITHOUT tahqeeq_manat_layer but WITH application_layer
        layer_results = [
            PipelineLayerResult("reality_grounding_layer", "passed"),
            PipelineLayerResult("application_layer", "passed"),
        ]
        required_layers = ["reality_grounding_layer", "tahqeeq_manat_layer",
                           "application_layer", "epistemic_audit_layer"]

        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertFalse(audit.passed)
        violations_text = " ".join(audit.violations)
        self.assertIn("NoApplicationWithoutTahqeeqManat", violations_text)

    def test_audit_blocks_mafhoom_without_mantuq(self):
        """Audit must flag NoMafhumStrongerThanMantuq when mantuq layer is missing."""
        from bayani.runtime.contracts import (
            IntentClassificationResult, PipelineLayerResult, PromptTypeResult
        )

        pt = PromptTypeResult("PT-07", "Mafhoom Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="explanation",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        # Layer results WITHOUT mantuq but WITH mafhoom
        layer_results = [
            PipelineLayerResult("reality_grounding_layer", "passed"),
            PipelineLayerResult("mafhoom_layer", "passed"),
        ]
        required_layers = ["reality_grounding_layer", "mantuq_layer",
                           "mafhoom_layer", "epistemic_audit_layer"]

        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertFalse(audit.passed)
        violations_text = " ".join(audit.violations)
        self.assertIn("NoMafhumStrongerThanMantuq", violations_text)

    def test_audit_blocks_classification_incomplete(self):
        """Audit must flag NoFinalAnswerBeforeClassificationComplete for bad input."""
        from bayani.runtime.contracts import (
            IntentClassificationResult, PipelineLayerResult, PromptTypeResult
        )

        # Invalid type_id that does not start with PT-
        pt = PromptTypeResult("UNKNOWN", "Unknown", "low", "no rule")
        intent = IntentClassificationResult(primary_purpose="")  # empty purpose
        layer_results = [PipelineLayerResult("reality_grounding_layer", "passed")]
        required_layers = ["reality_grounding_layer", "epistemic_audit_layer"]

        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertFalse(audit.passed)
        violations_text = " ".join(audit.violations)
        self.assertIn("NoFinalAnswerBeforeClassificationComplete", violations_text)

    def test_pt09_audit_checks_illah_validation(self):
        output = _run("هل الإسكار علة التحريم؟")
        cm = output.audit.certainty_map
        self.assertEqual(cm.get("illah_validation"), "performed")

    def test_final_rank_blocked_when_level_skip(self):
        """Final rank must not be structured_answer_allowed when a level is skipped."""
        from bayani.runtime.contracts import (
            IntentClassificationResult, PipelineLayerResult, PromptTypeResult
        )

        pt = PromptTypeResult("PT-10", "Application Prompt", "high", "test")
        intent = IntentClassificationResult(
            primary_purpose="tahqeeq_manat",
            mpc_layers_activated=[f"MPC-{i:02d}" for i in range(1, 12)],
        )
        # Only reality_grounding — many required layers are skipped
        layer_results = [PipelineLayerResult("reality_grounding_layer", "passed")]
        required_layers = [
            "reality_grounding_layer", "essence_assignment_layer",
            "tahqeeq_manat_layer", "application_layer", "epistemic_audit_layer"
        ]
        audit = run_audit(pt, intent, required_layers, layer_results)
        self.assertNotEqual(audit.final_rank, "structured_answer_allowed")


# ===========================================================================
# test_epistemic_trace — trace recording
# ===========================================================================

class TestEpistemicTrace(unittest.TestCase):

    def test_trace_records_all_transitions(self):
        """Number of trace steps must equal len(layers) - 1."""
        output = _run("هل العام قطعي؟")
        expected_steps = len(output.required_layers) - 1
        self.assertEqual(len(output.trace.steps), expected_steps)

    def test_trace_from_to_are_consecutive_layers(self):
        output = _run("هل العام قطعي؟")
        layers = output.required_layers
        for i, step in enumerate(output.trace.steps):
            self.assertEqual(step.from_layer, layers[i])
            self.assertEqual(step.to_layer, layers[i + 1])

    def test_trace_all_steps_validated(self):
        output = _run("هل العام قطعي؟")
        for step in output.trace.steps:
            self.assertTrue(step.validated, f"Step {step.from_layer}->{step.to_layer} not validated")

    def test_trace_has_bridge_for_all_steps(self):
        output = _run("هل العام قطعي؟")
        for step in output.trace.steps:
            self.assertGreater(len(step.bridge), 0,
                               f"Step {step.from_layer}->{step.to_layer} has empty bridge")

    def test_trace_mantuq_to_mafhoom_has_invariant(self):
        """mantuq→mafhoom transition must record the NoMafhumStrongerThanMantuq invariant."""
        output = _run("ما مفهوم المخالفة في هذا النص؟")
        mantuq_to_mafhoom = [
            s for s in output.trace.steps
            if s.from_layer == "mantuq_layer" and s.to_layer == "mafhoom_layer"
        ]
        if mantuq_to_mafhoom:
            self.assertEqual(
                mantuq_to_mafhoom[0].forbidden_jump_checked,
                "NoMafhumStrongerThanMantuq",
            )

    def test_trace_as_list_returns_dicts(self):
        output = _run("هل العام قطعي؟")
        trace_list = output.trace.as_list()
        self.assertIsInstance(trace_list, list)
        for item in trace_list:
            self.assertIn("from", item)
            self.assertIn("to", item)
            self.assertIn("bridge", item)
            self.assertIn("validated", item)

    def test_trace_tahqeeq_to_application_has_invariant(self):
        """tahqeeq_manat→application transition must record NoApplicationWithoutTahqeeqManat."""
        output = _run("طبّق هذا الحكم على واقعة معينة.")
        tahqeeq_to_app = [
            s for s in output.trace.steps
            if s.from_layer == "tahqeeq_manat_layer" and s.to_layer == "application_layer"
        ]
        if tahqeeq_to_app:
            self.assertEqual(
                tahqeeq_to_app[0].forbidden_jump_checked,
                "NoApplicationWithoutTahqeeqManat",
            )

    def test_build_trace_standalone(self):
        layers = [
            "reality_grounding_layer",
            "mantuq_layer",
            "mafhoom_layer",
            "epistemic_audit_layer",
        ]
        trace = build_trace(layers)
        self.assertEqual(len(trace.steps), 3)
        self.assertEqual(trace.steps[0].from_layer, "reality_grounding_layer")
        self.assertEqual(trace.steps[2].to_layer, "epistemic_audit_layer")


# ===========================================================================
# test_layers — layer registry and structure
# ===========================================================================

class TestLayerRegistry(unittest.TestCase):

    def test_all_21_layers_in_registry(self):
        from bayani.runtime.router import _PT_LAYER_MAP, _ALWAYS_LAST
        all_layers = set()
        for layers in _PT_LAYER_MAP.values():
            all_layers.update(layers)
        all_layers.update(_ALWAYS_LAST)
        for layer in all_layers:
            self.assertIn(layer, LAYER_REGISTRY, f"Layer {layer!r} missing from LAYER_REGISTRY")

    def test_each_layer_returns_pipeline_layer_result(self):
        from bayani.runtime.contracts import PipelineLayerResult
        pi = PromptInput(prompt="test", mode="analysis")
        for layer_name, layer_fn in LAYER_REGISTRY.items():
            result = layer_fn(pi)
            self.assertIsInstance(result, PipelineLayerResult,
                                  f"Layer {layer_name} did not return PipelineLayerResult")
            self.assertEqual(result.layer_name, layer_name)

    def test_each_layer_result_has_status(self):
        pi = PromptInput(prompt="test", mode="analysis")
        for layer_name, layer_fn in LAYER_REGISTRY.items():
            result = layer_fn(pi)
            self.assertIn(result.status, ("passed", "failed", "deferred"),
                          f"Layer {layer_name} has invalid status: {result.status!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
