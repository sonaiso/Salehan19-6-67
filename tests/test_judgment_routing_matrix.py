"""Tests for judgment_routing_matrix.py — فهرس سياسة التوجيه المعرفي.

Covers:
- All 10 task types are present
- All 10 policy dimensions are populated for each entry
- Suspension policy matches known shari/ambiguous/analogy types
- Evidence requirements are correct per task type
- Round-trip serialisation (to_dict / from_dict / save / load)
- Policy helper methods (should_suspend, required_evidence, etc.)
- Markdown rendering
- JSON data file consistency
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from mcd.classification.taxonomy import CertaintyPolicy, JudgmentType
from mcd.evaluation.judgment_routing_matrix import (
    JudgmentRoutingMatrix,
    MatrixEntry,
    _MATRIX_FILE,
)

DATA_FILE = Path(__file__).parent.parent / "data" / "evaluation" / "judgment_routing_matrix.json"

ALL_TASK_TYPES = [jt.value for jt in JudgmentType]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def matrix() -> JudgmentRoutingMatrix:
    return JudgmentRoutingMatrix()


@pytest.fixture(scope="module")
def matrix_from_file() -> JudgmentRoutingMatrix:
    return JudgmentRoutingMatrix.load(DATA_FILE)


# ---------------------------------------------------------------------------
# Coverage: all 10 task types
# ---------------------------------------------------------------------------

class TestMatrixCoverage:
    def test_all_judgment_types_present(self, matrix):
        found = set(matrix.task_types())
        for jt in ALL_TASK_TYPES:
            assert jt in found, f"Missing entry for task_type={jt!r}"

    def test_length_equals_ten(self, matrix):
        assert len(matrix) == 10

    def test_iteration_yields_all(self, matrix):
        entries = list(matrix)
        assert len(entries) == 10


# ---------------------------------------------------------------------------
# Schema: all 10 dimensions non-empty for every entry
# ---------------------------------------------------------------------------

class TestMatrixSchema:
    def test_intended_reality_nonempty(self, matrix):
        for e in matrix:
            assert e.intended_reality.strip(), f"{e.task_type}: intended_reality empty"

    def test_required_evidence_nonempty(self, matrix):
        for e in matrix:
            assert e.required_evidence, f"{e.task_type}: required_evidence empty"

    def test_certainty_degree_nonempty(self, matrix):
        valid = set(cp.value for cp in CertaintyPolicy)
        for e in matrix:
            assert e.certainty_degree in valid, (
                f"{e.task_type}: invalid certainty_degree={e.certainty_degree!r}"
            )

    def test_when_to_answer_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_answer.strip(), f"{e.task_type}: when_to_answer empty"

    def test_when_to_suspend_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_suspend.strip(), f"{e.task_type}: when_to_suspend empty"

    def test_when_to_request_source_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_request_source.strip(), (
                f"{e.task_type}: when_to_request_source empty"
            )

    def test_when_to_distinguish_opinion_evidence_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_distinguish_opinion_evidence.strip(), (
                f"{e.task_type}: when_to_distinguish_opinion_evidence empty"
            )

    def test_when_to_detect_hallucination_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_detect_hallucination.strip(), (
                f"{e.task_type}: when_to_detect_hallucination empty"
            )

    def test_when_to_separate_technical_from_value_shari_nonempty(self, matrix):
        for e in matrix:
            assert e.when_to_separate_technical_from_value_shari.strip(), (
                f"{e.task_type}: when_to_separate_technical_from_value_shari empty"
            )


# ---------------------------------------------------------------------------
# Suspension logic
# ---------------------------------------------------------------------------

class TestSuspensionPolicy:
    """Types that must always suspend: shari, ambiguous, analogy."""

    def test_shari_suspends(self, matrix):
        entry = matrix.require(JudgmentType.SHARI)
        assert entry.certainty_degree == CertaintyPolicy.SUSPEND

    def test_ambiguous_suspends(self, matrix):
        entry = matrix.require(JudgmentType.AMBIGUOUS)
        assert entry.certainty_degree == CertaintyPolicy.SUSPEND

    def test_analogy_suspends(self, matrix):
        entry = matrix.require(JudgmentType.ANALOGY)
        assert entry.certainty_degree == CertaintyPolicy.SUSPEND

    def test_epistemic_does_not_always_suspend(self, matrix):
        entry = matrix.require(JudgmentType.EPISTEMIC)
        assert entry.certainty_degree != CertaintyPolicy.SUSPEND

    def test_technical_does_not_always_suspend(self, matrix):
        entry = matrix.require(JudgmentType.TECHNICAL)
        assert entry.certainty_degree != CertaintyPolicy.SUSPEND

    def test_should_suspend_helper_shari(self, matrix):
        assert matrix.should_suspend(JudgmentType.SHARI) is True

    def test_should_suspend_helper_ambiguous(self, matrix):
        assert matrix.should_suspend(JudgmentType.AMBIGUOUS) is True

    def test_should_suspend_override(self, matrix):
        # Even an epistemic task suspends if certainty_policy forces it
        assert matrix.should_suspend(
            JudgmentType.EPISTEMIC, certainty_policy=CertaintyPolicy.SUSPEND
        ) is True

    def test_should_suspend_false_for_technical(self, matrix):
        assert matrix.should_suspend(JudgmentType.TECHNICAL) is False


# ---------------------------------------------------------------------------
# Evidence requirements
# ---------------------------------------------------------------------------

class TestEvidenceRequirements:
    def test_shari_requires_shari_evidence(self, matrix):
        assert "shari" in matrix.required_evidence(JudgmentType.SHARI)

    def test_shari_requires_textual_evidence(self, matrix):
        assert "textual" in matrix.required_evidence(JudgmentType.SHARI)

    def test_technical_requires_technical_evidence(self, matrix):
        assert "technical" in matrix.required_evidence(JudgmentType.TECHNICAL)

    def test_ambiguous_requires_linguistic(self, matrix):
        assert "linguistic" in matrix.required_evidence(JudgmentType.AMBIGUOUS)

    def test_ambiguous_requires_contextual(self, matrix):
        assert "contextual" in matrix.required_evidence(JudgmentType.AMBIGUOUS)

    def test_analogy_requires_contextual(self, matrix):
        assert "contextual" in matrix.required_evidence(JudgmentType.ANALOGY)

    def test_epistemic_requires_sensory_or_experimental(self, matrix):
        ev = matrix.required_evidence(JudgmentType.EPISTEMIC)
        assert "sensory" in ev or "experimental" in ev

    def test_unknown_type_returns_empty(self, matrix):
        assert matrix.required_evidence("nonexistent_type") == ()


# ---------------------------------------------------------------------------
# Policy helper methods
# ---------------------------------------------------------------------------

class TestPolicyHelpers:
    def test_when_to_answer_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_answer(jt)
            assert isinstance(result, str)

    def test_when_to_suspend_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_suspend(jt)
            assert isinstance(result, str)

    def test_when_to_request_source_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_request_source(jt)
            assert isinstance(result, str)

    def test_when_to_distinguish_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_distinguish_opinion_evidence(jt)
            assert isinstance(result, str)

    def test_when_to_detect_hallucination_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_detect_hallucination(jt)
            assert isinstance(result, str)

    def test_when_to_separate_returns_string(self, matrix):
        for jt in ALL_TASK_TYPES:
            result = matrix.when_to_separate_technical_from_value_shari(jt)
            assert isinstance(result, str)

    def test_unknown_type_helpers_return_empty(self, matrix):
        assert matrix.when_to_answer("ghost") == ""
        assert matrix.when_to_suspend("ghost") == ""
        assert matrix.when_to_request_source("ghost") == ""

    def test_get_returns_none_for_unknown(self, matrix):
        assert matrix.get("nonexistent") is None

    def test_require_raises_for_unknown(self, matrix):
        with pytest.raises(KeyError):
            matrix.require("nonexistent")


# ---------------------------------------------------------------------------
# Specific policy content checks
# ---------------------------------------------------------------------------

class TestPolicyContent:
    """Spot-check that key Arabic policy phrases appear in the right cells."""

    def test_shari_request_source_always(self, matrix):
        policy = matrix.when_to_request_source(JudgmentType.SHARI)
        assert "دائمًا" in policy or "نص" in policy

    def test_ambiguous_request_context(self, matrix):
        policy = matrix.when_to_request_source(JudgmentType.AMBIGUOUS)
        assert "سياق" in policy or "جملة" in policy

    def test_shari_separate_policy_mentions_harm_wajib(self, matrix):
        policy = matrix.when_to_separate_technical_from_value_shari(JudgmentType.SHARI)
        assert "ضرر" in policy or "تحريم" in policy or "وجوب" in policy

    def test_analogy_suspend_mentions_illah(self, matrix):
        policy = matrix.when_to_suspend(JudgmentType.ANALOGY)
        assert "علة" in policy or "فارق" in policy

    def test_metaphor_hallucination_mentions_literal(self, matrix):
        policy = matrix.when_to_detect_hallucination(JudgmentType.METAPHOR)
        assert "حرفي" in policy or "واقعي" in policy or "استعارة" in policy

    def test_technical_hallucination_mentions_api(self, matrix):
        policy = matrix.when_to_detect_hallucination(JudgmentType.TECHNICAL)
        assert "API" in policy or "مكتبات" in policy or "تفاصيل" in policy


# ---------------------------------------------------------------------------
# Round-trip: to_dict / from_dict
# ---------------------------------------------------------------------------

class TestMatrixEntryRoundTrip:
    def test_to_dict_keys(self, matrix):
        expected_keys = {
            "task_type", "intended_reality", "required_evidence", "certainty_degree",
            "when_to_answer", "when_to_suspend", "when_to_request_source",
            "when_to_distinguish_opinion_evidence", "when_to_detect_hallucination",
            "when_to_separate_technical_from_value_shari",
        }
        for e in matrix:
            assert set(e.to_dict().keys()) == expected_keys

    def test_from_dict_roundtrip(self, matrix):
        for e in matrix:
            d = e.to_dict()
            e2 = MatrixEntry.from_dict(d)
            assert e2.task_type == e.task_type
            assert e2.certainty_degree == e.certainty_degree
            assert e2.required_evidence == e.required_evidence

    def test_to_list_roundtrip(self, matrix):
        lst = matrix.to_list()
        m2 = JudgmentRoutingMatrix(entries=[MatrixEntry.from_dict(d) for d in lst])
        assert len(m2) == len(matrix)
        for jt in ALL_TASK_TYPES:
            assert m2.get(jt) is not None


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

class TestMatrixSaveLoad:
    def test_save_and_load(self, matrix):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test_matrix.json"
            matrix.save(path)
            assert path.exists()
            m2 = JudgmentRoutingMatrix.load(path)
            assert len(m2) == len(matrix)

    def test_saved_json_structure(self, matrix):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.json"
            matrix.save(path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 10
            for row in data:
                assert "task_type" in row
                assert "required_evidence" in row
                assert isinstance(row["required_evidence"], list)

    def test_data_file_exists(self):
        assert DATA_FILE.exists(), f"Matrix data file not found at {DATA_FILE}"

    def test_data_file_loadable(self, matrix_from_file):
        assert len(matrix_from_file) == 10

    def test_data_file_matches_defaults(self, matrix, matrix_from_file):
        for jt in ALL_TASK_TYPES:
            e1 = matrix.require(jt)
            e2 = matrix_from_file.require(jt)
            assert e1.task_type == e2.task_type
            assert e1.certainty_degree == e2.certainty_degree
            assert set(e1.required_evidence) == set(e2.required_evidence)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

class TestMarkdownRendering:
    def test_to_markdown_returns_string(self, matrix):
        md = matrix.to_markdown()
        assert isinstance(md, str)

    def test_to_markdown_has_header_row(self, matrix):
        md = matrix.to_markdown()
        assert "نوع المهمة" in md
        assert "الواقع المقصود" in md
        assert "الدليل المطلوب" in md
        assert "درجة اليقين" in md
        assert "متى تجيب" in md
        assert "متى تعلق" in md
        assert "متى تطلب مصدرًا" in md
        assert "متى تميز بين رأي ودليل" in md
        assert "متى تكشف الهلوسة" in md
        assert "متى تفرق بين حكم تقني وحكم قيمي أو شرعي" in md

    def test_to_markdown_has_all_task_types(self, matrix):
        md = matrix.to_markdown()
        for jt in ALL_TASK_TYPES:
            assert jt in md, f"Task type {jt!r} missing from markdown"

    def test_to_markdown_has_separator_row(self, matrix):
        md = matrix.to_markdown()
        assert "---" in md


# ---------------------------------------------------------------------------
# Integration: matrix aligns with web evaluator dataset
# ---------------------------------------------------------------------------

class TestMatrixWebEvaluatorAlignment:
    """Spot-check that key web evaluator categories map to correct matrix policies."""

    def test_ambiguity_category_maps_to_suspend(self, matrix):
        # Web evaluator Category B (WEB-006–015) → ambiguous judgment
        assert matrix.should_suspend(JudgmentType.AMBIGUOUS) is True

    def test_analogy_category_requires_illah(self, matrix):
        # Web evaluator Category E (WEB-036–045)
        entry = matrix.require(JudgmentType.ANALOGY)
        assert "علة" in entry.when_to_answer or "مناط" in entry.when_to_answer

    def test_adversarial_category_maps_to_hallucination_detection(self, matrix):
        # Web evaluator Category I (WEB-076–085) — false certainty
        # All types must have a non-empty hallucination detection policy
        for jt in ALL_TASK_TYPES:
            policy = matrix.when_to_detect_hallucination(jt)
            assert len(policy) > 0, f"{jt}: missing hallucination detection policy"

    def test_shari_category_always_requires_source(self, matrix):
        # Web evaluator Category C partial (harm_haram with shari keywords)
        source_policy = matrix.when_to_request_source(JudgmentType.SHARI)
        assert len(source_policy) > 10  # substantive policy text
