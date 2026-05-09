"""Tests for the Web Evaluator Arabic Prompt Dataset (WEB-001 – WEB-085).

Covers:
- Loading web_evaluator_prompts_ar_dataset.jsonl
- WebEvaluatorExample schema validity
- Category-specific rules (ambiguity → suspend, shari warnings, analogy illah,
  adversarial false-certainty traps)
- Round-trip serialisation
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcd.evaluation.dataset_schema import WebEvaluatorExample
from mcd.evaluation.dataset_loader import load_web_evaluator, load_web_evaluator_jsonl

DATA_DIR = Path(__file__).parent.parent / "data" / "evaluation"
DATASET_PATH = DATA_DIR / "web_evaluator_prompts_ar_dataset.jsonl"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def examples() -> list[WebEvaluatorExample]:
    return load_web_evaluator(DATA_DIR)


# ---------------------------------------------------------------------------
# Basic loading
# ---------------------------------------------------------------------------

class TestWebEvaluatorLoading:
    def test_file_exists(self):
        assert DATASET_PATH.exists(), f"Dataset not found at {DATASET_PATH}"

    def test_load_returns_list(self, examples):
        assert isinstance(examples, list)

    def test_minimum_count(self, examples):
        assert len(examples) >= 85, f"Expected ≥85 examples, got {len(examples)}"

    def test_all_instances_are_web_evaluator(self, examples):
        for ex in examples:
            assert isinstance(ex, WebEvaluatorExample)

    def test_ids_start_with_WEB(self, examples):
        for ex in examples:
            assert ex.id.startswith("WEB-"), f"Bad id: {ex.id}"

    def test_ids_are_unique(self, examples):
        ids = [ex.id for ex in examples]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_ids_sequential(self, examples):
        nums = sorted(int(ex.id.split("-")[1]) for ex in examples)
        assert nums[0] == 1
        assert nums[-1] == len(examples)

    def test_load_via_path(self):
        exs = load_web_evaluator_jsonl(DATASET_PATH)
        assert len(exs) >= 85


# ---------------------------------------------------------------------------
# Schema field validation
# ---------------------------------------------------------------------------

class TestWebEvaluatorSchema:
    def test_prompt_nonempty(self, examples):
        for ex in examples:
            assert ex.prompt.strip(), f"Empty prompt in {ex.id}"

    def test_what_is_reality_nonempty(self, examples):
        for ex in examples:
            assert ex.what_is_reality.strip(), f"Empty what_is_reality in {ex.id}"

    def test_required_behavior_nonempty(self, examples):
        for ex in examples:
            assert ex.required_behavior.strip(), f"Empty required_behavior in {ex.id}"

    def test_root_domain_nonempty(self, examples):
        for ex in examples:
            assert ex.root_domain, f"Empty root_domain in {ex.id}"

    def test_judgment_type_nonempty(self, examples):
        for ex in examples:
            assert ex.judgment_type, f"Empty judgment_type in {ex.id}"

    def test_certainty_policy_valid(self, examples):
        valid = {"near_certainty", "strong_knowledge", "probable_knowledge", "hypothesis", "suspend"}
        for ex in examples:
            assert ex.certainty_policy in valid, (
                f"{ex.id}: invalid certainty_policy '{ex.certainty_policy}'"
            )

    def test_difficulty_valid(self, examples):
        valid = {"easy", "medium", "hard", "adversarial"}
        for ex in examples:
            assert ex.difficulty in valid, (
                f"{ex.id}: invalid difficulty '{ex.difficulty}'"
            )

    def test_tags_list(self, examples):
        for ex in examples:
            assert isinstance(ex.tags, list), f"{ex.id}: tags must be a list"

    def test_forbidden_outputs_list(self, examples):
        for ex in examples:
            assert isinstance(ex.forbidden_outputs, list)

    def test_scoring_focus_list(self, examples):
        for ex in examples:
            assert isinstance(ex.scoring_focus, list)


# ---------------------------------------------------------------------------
# Category-specific rules
# ---------------------------------------------------------------------------

class TestWebEvaluatorCategoryRules:

    # Category A: epistemic — strong certainty allowed
    def test_epistemic_examples_have_epistemic_judgment(self, examples):
        epistemic_ids = [f"WEB-{i:03d}" for i in range(1, 6)]
        for ex in examples:
            if ex.id in epistemic_ids:
                assert "epistemic" in ex.judgment_type, (
                    f"{ex.id} should have epistemic judgment"
                )

    # Category B: ambiguity — must suspend
    def test_ambiguity_examples_suspend(self, examples):
        ambiguity_ids = [f"WEB-{i:03d}" for i in range(6, 16)]
        for ex in examples:
            if ex.id in ambiguity_ids:
                assert ex.certainty_policy == "suspend", (
                    f"{ex.id} (ambiguity) must have certainty_policy=suspend"
                )
                assert ex.expected_status == "requires_context", (
                    f"{ex.id} (ambiguity) must have expected_status=requires_context"
                )
                assert "requires_context" in ex.required_warnings, (
                    f"{ex.id} (ambiguity) must warn requires_context"
                )

    # Category B: must forbid forced single meaning
    def test_ambiguity_forbids_forced_meaning(self, examples):
        ambiguity_ids = {f"WEB-{i:03d}" for i in range(6, 16)}
        for ex in examples:
            if ex.id in ambiguity_ids:
                assert (
                    "single_forced_meaning" in ex.forbidden_outputs
                    or "near_certainty" in ex.forbidden_outputs
                ), f"{ex.id} should forbid single_forced_meaning or near_certainty"

    # Category C: shari prompts — must require shari evidence
    def test_shari_prompts_have_warning(self, examples):
        shari_ids = {f"WEB-{i:03d}" for i in range(16, 26)}
        for ex in examples:
            if ex.id in shari_ids and "shari" in ex.judgment_type:
                if ex.certainty_policy == "suspend":
                    assert "shari_evidence_required" in ex.required_warnings, (
                        f"{ex.id}: shari/suspend example missing shari_evidence_required"
                    )

    # Category C: harm vs haram — forbid harm_equals_haram
    def test_harm_haram_forbids_conflation(self, examples):
        harm_ids = {f"WEB-{i:03d}" for i in range(16, 26)}
        for ex in examples:
            if ex.id in harm_ids:
                assert "harm_equals_haram" in ex.forbidden_outputs, (
                    f"{ex.id}: harm/haram example must forbid harm_equals_haram"
                )

    # Category E: analogy — must flag missing_illah
    def test_analogy_requires_illah(self, examples):
        analogy_ids = {f"WEB-{i:03d}" for i in range(36, 46)}
        for ex in examples:
            if ex.id in analogy_ids:
                assert "missing_illah" in ex.required_warnings, (
                    f"{ex.id}: analogy example must warn missing_illah"
                )
                assert ex.certainty_policy == "suspend", (
                    f"{ex.id}: analogy example must suspend"
                )

    # Category I: adversarial — difficulty = adversarial
    def test_adversarial_difficulty(self, examples):
        adv_ids = {f"WEB-{i:03d}" for i in range(76, 86)}
        for ex in examples:
            if ex.id in adv_ids:
                assert ex.difficulty == "adversarial", (
                    f"{ex.id}: adversarial example must have difficulty=adversarial"
                )

    # Category I: adversarial — must warn false_certainty_trap
    def test_adversarial_warns_false_certainty(self, examples):
        adv_ids = {f"WEB-{i:03d}" for i in range(76, 86)}
        for ex in examples:
            if ex.id in adv_ids:
                assert "false_certainty_trap" in ex.required_warnings, (
                    f"{ex.id}: adversarial example must warn false_certainty_trap"
                )

    # Metaphor examples — must flag metaphor_not_literal
    def test_metaphor_examples_not_literal(self, examples):
        for ex in examples:
            if "metaphor" in ex.judgment_type:
                assert (
                    "metaphor_not_literal" in ex.required_warnings
                    or "literal_biological_claim" in ex.forbidden_outputs
                    or "surface_similarity_as_proof" in ex.forbidden_outputs
                ), f"{ex.id}: metaphor example needs anti-literal guard"


# ---------------------------------------------------------------------------
# Round-trip serialisation
# ---------------------------------------------------------------------------

class TestWebEvaluatorRoundTrip:
    def test_to_dict_from_dict_roundtrip(self, examples):
        for ex in examples[:10]:
            d = ex.to_dict()
            ex2 = WebEvaluatorExample.from_dict(d)
            assert ex2.id == ex.id
            assert ex2.prompt == ex.prompt
            assert ex2.certainty_policy == ex.certainty_policy
            assert ex2.judgment_type == ex.judgment_type

    def test_to_dict_json_serialisable(self, examples):
        for ex in examples[:10]:
            blob = json.dumps(ex.to_dict(), ensure_ascii=False)
            assert isinstance(blob, str)
            parsed = json.loads(blob)
            assert parsed["id"] == ex.id

    def test_from_dict_ignores_unknown_fields(self):
        d = {
            "id": "WEB-TEST",
            "prompt": "test",
            "what_is_reality": "test",
            "certainty_policy": "suspend",
            "expected_status": "suspended",
            "required_behavior": "test",
            "UNKNOWN_FIELD": "should_be_ignored",
        }
        ex = WebEvaluatorExample.from_dict(d)
        assert ex.id == "WEB-TEST"


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

class TestWebEvaluatorProperties:
    def test_should_suspend_true_when_suspend(self):
        ex = WebEvaluatorExample(
            id="T-001", prompt="test", what_is_reality="x",
            certainty_policy="suspend", expected_status="suspended",
            required_behavior="suspend",
        )
        assert ex.should_suspend is True

    def test_should_suspend_false_for_strong_knowledge(self):
        ex = WebEvaluatorExample(
            id="T-002", prompt="test", what_is_reality="x",
            certainty_policy="strong_knowledge", expected_status="verified",
            required_behavior="confirm",
        )
        assert ex.should_suspend is False

    def test_is_adversarial_true(self):
        ex = WebEvaluatorExample(
            id="T-003", prompt="test", what_is_reality="x",
            difficulty="adversarial", required_behavior="resist",
        )
        assert ex.is_adversarial is True

    def test_is_adversarial_false(self):
        ex = WebEvaluatorExample(
            id="T-004", prompt="test", what_is_reality="x",
            difficulty="medium", required_behavior="answer",
        )
        assert ex.is_adversarial is False


# ---------------------------------------------------------------------------
# Category coverage summary (informational)
# ---------------------------------------------------------------------------

class TestWebEvaluatorCoverageSummary:
    def test_all_nine_categories_present(self, examples):
        """Each of the 9 categories (A-I) contributes at least 4 examples."""
        ranges = {
            "A_epistemic": range(1, 6),
            "B_ambiguity": range(6, 16),
            "C_harm_haram": range(16, 26),
            "D_technical": range(26, 36),
            "E_analogy": range(36, 46),
            "F_civilization": range(46, 56),
            "G_society": range(56, 66),
            "H_linguistic": range(66, 76),
            "I_adversarial": range(76, 86),
        }
        id_set = {ex.id for ex in examples}
        for cat, rng in ranges.items():
            found = sum(1 for n in rng if f"WEB-{n:03d}" in id_set)
            assert found >= 4, f"Category {cat} has only {found} examples"

    def test_judgment_type_variety(self, examples):
        all_jt = {jt for ex in examples for jt in ex.judgment_type}
        expected = {"epistemic", "ambiguous", "value", "shari", "technical",
                    "practical", "analogy", "linguistic", "usuli", "metaphor"}
        for jt in expected:
            assert jt in all_jt, f"Judgment type '{jt}' missing from dataset"

    def test_difficulty_variety(self, examples):
        diffs = {ex.difficulty for ex in examples}
        assert "easy" in diffs
        assert "medium" in diffs
        assert "hard" in diffs
        assert "adversarial" in diffs
