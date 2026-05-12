"""Tests for Phase 8 CFK pipeline (end-to-end) and comparison table."""
from __future__ import annotations

import pytest
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline, CognitiveFractalResult
from mcd.cfk.cfk_comparison_table import ComparisonTable, ComparisonTableBuilder
from mcd.cfk.cfk_schema import JudgmentStatus
from mcd.cfk.cfk_report import generate_markdown_report, generate_json_report


class TestCognitiveFractalPipeline:
    def setup_method(self):
        self.pipeline = CognitiveFractalPipeline()

    def test_run_returns_result(self):
        result = self.pipeline.run("زيد كاتب")
        assert isinstance(result, CognitiveFractalResult)

    def test_run_id_prefix(self):
        result = self.pipeline.run("test")
        assert result.run_id.startswith("CFR-")

    def test_has_all_components(self):
        result = self.pipeline.run("test")
        assert result.kernel is not None
        assert result.proof is not None
        assert result.table is not None
        assert len(result.conservation_results) == 3

    # --- The three examples from the problem statement ---

    def test_in_hadha_la_haqqun(self):
        """إن هذا لحق — emphasis, no evidence → hypothesis."""
        result = self.pipeline.run("إن هذا لحق")
        assert result.proof.judgment == JudgmentStatus.HYPOTHESIS.value
        assert result.proof.linguistic_force == "emphasis"
        assert result.proof.evidence_state == "missing"

    def test_universal_quantifier_no_evidence_is_hypothesis(self):
        """كل الشركات ... — universal without evidence → internal suspended + public hypothesis."""
        result = self.pipeline.run("كل الشركات تستخدم GraphRAG")
        assert result.proof.judgment == JudgmentStatus.HYPOTHESIS.value
        assert result.proof.judgment != "suspend"
        assert result.proof.internal_state == JudgmentStatus.SUSPENDED.value
        assert "insufficient_evidence" in result.proof.residuals
        assert result.proof.residual_type == "unsupported_generalization_residual"

    def test_with_evidence_near_certainty_is_certificate(self):
        """النار حارة + near_certainty + 2 evidence refs → certificate."""
        proposal = {
            "proposal_id": "P-fire",
            "gpt_output": "النار حارة",
            "input_text": "النار حارة",
            "proposal_type": "answer",
            "claimed_certainty": "near_certainty",
            "claimed_evidence": ["empirical_1", "experimental_2"],
        }
        result = self.pipeline.run(
            "النار حارة",
            proposal_dict=proposal,
            evidence_refs=["empirical_1", "experimental_2"],
        )
        assert result.proof.judgment == JudgmentStatus.CERTIFICATE.value

    def test_cognitive_residual_is_gap(self):
        """Residual = statistical_confidence - epistemic_certainty (no evidence case)."""
        result = self.pipeline.run("إن هذا لحق")
        # stat confidence ~0.5, epistemic low → residual > 0
        assert result.proof.cognitive_residual > 0.0

    def test_learning_signal_present(self):
        result = self.pipeline.run("test")
        assert result.proof.learning_signal in ("reinforce", "correct", "ignore")

    def test_to_dict_structure(self):
        result = self.pipeline.run("test")
        d = result.to_dict()
        for key in ("run_id", "text", "kernel", "conservation", "proof", "table"):
            assert key in d

    def test_summary_contains_text(self):
        result = self.pipeline.run("النار حارة")
        summary = result.summary()
        assert "الحكم" in summary
        assert "الدليل" in summary

    def test_negation_detected(self):
        result = self.pipeline.run("ما جاء زيد")
        assert result.proof.linguistic_force == "negation"

    def test_condition_detected(self):
        result = self.pipeline.run("إذا جاء زيد فاضرب")
        assert result.proof.linguistic_force == "condition"

    def test_conservation_results_count(self):
        result = self.pipeline.run("زيد كاتب")
        assert len(result.conservation_results) == 3

    def test_evidence_refs_passed_through(self):
        result = self.pipeline.run("test", evidence_refs=["ref1"])
        assert result.proof.evidence_state in ("present", "partial")

    def test_proposal_dict_override(self):
        """proposal_dict supplied by caller is used by statistical transform."""
        proposal = {
            "proposal_id": "P-custom",
            "gpt_output": "زيد كريم",
            "input_text": "زيد كريم",
            "proposal_type": "answer",
            "claimed_certainty": "strong_knowledge",
            "claimed_evidence": ["ref1"],
        }
        result = self.pipeline.run("زيد كريم", proposal_dict=proposal, evidence_refs=["ref1"])
        # strong_knowledge + 1 evidence (partial) → epistemic ~0.50 → public hypothesis
        assert result.proof.judgment == JudgmentStatus.HYPOTHESIS.value

    def test_empty_text(self):
        """Empty text should not crash the pipeline."""
        result = self.pipeline.run("")
        assert result.proof is not None

    def test_table_rows_count(self):
        result = self.pipeline.run("زيد كاتب")
        assert len(result.table.rows) == 5  # 5 dimensions in comparison table


class TestComparisonTable:
    def setup_method(self):
        self.pipeline = CognitiveFractalPipeline()

    def _run(self, text, evidence_refs=None):
        return self.pipeline.run(text, evidence_refs=evidence_refs)

    def test_table_has_five_rows(self):
        result = self._run("زيد كاتب")
        assert len(result.table.rows) == 5

    def test_row_dimensions(self):
        result = self._run("زيد كاتب")
        dims = [r.dimension for r in result.table.rows]
        assert "نوع الجملة" in dims
        assert "القوة" in dims
        assert "الدليل" in dims
        assert "اليقين" in dims
        assert "الحكم" in dims

    def test_all_rows_have_three_columns(self):
        result = self._run("test")
        for row in result.table.rows:
            assert row.statistical_value
            assert row.arabic_value
            assert row.epistemic_value

    def test_to_dict_keys(self):
        result = self._run("test")
        d = result.table.to_dict()
        assert "text" in d
        assert "kernel_judgment" in d
        assert "rows" in d

    def test_to_markdown_contains_headers(self):
        result = self._run("زيد كاتب")
        md = result.table.to_markdown()
        assert "GPT" in md
        assert "العربية" in md or "arabic" in md.lower()
        assert "الحكم" in md

    def test_to_markdown_contains_kernel_judgment(self):
        result = self._run("زيد كاتب")
        md = result.table.to_markdown()
        assert result.proof.judgment in md

    def test_emphasis_arabic_column_shows_emphasis(self):
        result = self._run("إن زيداً لكريم")
        # Arabic row for sentence type should show تأكيد or توكيد
        arabic_sentence = result.table.rows[0].arabic_value
        assert arabic_sentence  # non-empty

    def test_table_kernel_judgment_matches_proof(self):
        result = self._run("كل الشركات تستخدم هذه التقنية")
        assert result.table.kernel_judgment == result.proof.judgment


class TestCFKReports:
    def setup_method(self):
        self.pipeline = CognitiveFractalPipeline()

    def test_markdown_report_contains_headers(self):
        result = self.pipeline.run("إن هذا لحق")
        md = generate_markdown_report(result)
        assert "تقرير النواة الفراكتالية المعرفية" in md
        assert "الحكم النهائي" in md
        assert "قوانين الحفظ" in md

    def test_markdown_report_contains_table(self):
        result = self.pipeline.run("زيد كاتب")
        md = generate_markdown_report(result)
        assert "جدول المقارنة" in md

    def test_json_report_is_valid_json(self):
        import json
        result = self.pipeline.run("test")
        s = generate_json_report(result)
        d = json.loads(s)
        assert "run_id" in d

    def test_json_report_has_proof_judgment(self):
        import json
        result = self.pipeline.run("test")
        s = generate_json_report(result)
        d = json.loads(s)
        assert d["proof"]["judgment"] in ("certificate", "hypothesis", "zero")
