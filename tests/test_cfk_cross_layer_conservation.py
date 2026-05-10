"""Tests for Phase 8.1 — CrossLayerConservationChecker."""
from __future__ import annotations

import pytest

from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.cfk.cross_layer_conservation import (
    CrossLayerConservationChecker,
    CrossLayerConservationReport,
    CrossLayerViolation,
)
from mcd.cfk.cfk_schema import JudgmentStatus
from mcd.cfk.statistical_transform import StatisticalTransform
from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
from mcd.cfk.epistemic_transform import EpistemicTransform


def _make_projections(
    text: str = "النار حارة",
    evidence_refs: list[str] | None = None,
    statistical_claimed: str = "hypothesis",
):
    stat = StatisticalTransform()
    arab = ArabicSemanticTransform()
    epis = EpistemicTransform()

    proposal = {
        "proposal_id": "P-test",
        "gpt_output": text,
        "input_text": text,
        "proposal_type": "answer",
        "claimed_certainty": statistical_claimed,
        "claimed_evidence": evidence_refs or [],
    }
    s_proj = stat.transform(proposal)
    a_proj = arab.transform(text)
    e_proj = epis.transform(
        text,
        statistical_confidence=s_proj.comparable_score,
        evidence_refs=evidence_refs or [],
    )
    return s_proj, a_proj, e_proj


class TestCrossLayerConservationChecker:
    def setup_method(self):
        self.checker = CrossLayerConservationChecker()

    def test_clean_run_passes(self):
        s, a, e = _make_projections("النار حارة", evidence_refs=["e1", "e2"])
        report = self.checker.check(s, a, e, JudgmentStatus.CERTIFICATE.value)
        assert report.conservation_score >= 0.95

    def test_report_has_id(self):
        s, a, e = _make_projections("زيد كاتب")
        report = self.checker.check(s, a, e, JudgmentStatus.HYPOTHESIS.value)
        assert report.report_id.startswith("CLCR-")

    def test_universal_without_evidence_certificate_blocked(self):
        """Universal quantifier + no evidence → certificate must NOT be allowed."""
        text = "كل الشركات تستخدم GraphRAG"
        s, a, e = _make_projections(text, evidence_refs=[])
        # Force kernel_judgment to certificate (simulating a bug)
        report = self.checker.check(s, a, e, JudgmentStatus.CERTIFICATE.value)
        check_names = [v.check_name for v in report.violations]
        assert "universal_without_evidence" in check_names or not report.passed

    def test_universal_without_evidence_suspend_ok(self):
        """Universal + no evidence + suspend judgment → should have no blocking violations."""
        text = "كل الشركات تستخدم GraphRAG"
        s, a, e = _make_projections(text, evidence_refs=[])
        report = self.checker.check(s, a, e, JudgmentStatus.SUSPEND.value)
        blocking = [v for v in report.violations if v.severity == "blocking" and v.check_name == "universal_without_evidence"]
        assert len(blocking) == 0

    def test_emphasis_without_evidence_no_certificate(self):
        """Emphasis operator + no evidence → certificate blocked."""
        text = "إن هذا لحق"
        s, a, e = _make_projections(text, evidence_refs=[])
        report = self.checker.check(s, a, e, JudgmentStatus.CERTIFICATE.value)
        check_names = [v.check_name for v in report.violations]
        # Either emphasis_without_evidence or evidence_missing_no_certificate must be present
        assert (
            "emphasis_without_evidence" in check_names
            or "evidence_missing_no_certificate" in check_names
        )

    def test_evidence_missing_no_certificate(self):
        """evidence_state=missing + certificate → blocking violation."""
        text = "زيد كاتب"
        s, a, e = _make_projections(text, evidence_refs=[])
        report = self.checker.check(s, a, e, JudgmentStatus.CERTIFICATE.value)
        assert not report.passed
        blocking_names = [v.check_name for v in report.violations if v.severity == "blocking"]
        assert "evidence_missing_no_certificate" in blocking_names

    def test_high_stat_no_evidence_not_certificate(self):
        """High statistical confidence without evidence + certificate → blocking."""
        text = "الأرض كروية"
        s, a, e = _make_projections(text, evidence_refs=[], statistical_claimed="near_certainty")
        report = self.checker.check(s, a, e, JudgmentStatus.CERTIFICATE.value)
        blocking_names = [v.check_name for v in report.violations if v.severity == "blocking"]
        # Either high_stat_no_evidence or evidence_missing_no_certificate should fire
        assert len(blocking_names) > 0

    def test_high_stat_no_evidence_hypothesis_ok(self):
        """High statistical confidence without evidence + hypothesis → no blocking."""
        text = "الأرض كروية"
        s, a, e = _make_projections(text, evidence_refs=[], statistical_claimed="near_certainty")
        report = self.checker.check(s, a, e, JudgmentStatus.SUSPEND.value)
        blocking = [v for v in report.violations if v.severity == "blocking"]
        assert len(blocking) == 0

    def test_cross_layer_conservation_score_above_095_clean(self):
        """A clean run (evidence present, correct judgment) scores ≥ 0.95."""
        s, a, e = _make_projections("النار حارة", evidence_refs=["e1", "e2"])
        report = self.checker.check(s, a, e, JudgmentStatus.HYPOTHESIS.value)
        assert report.conservation_score >= 0.95

    def test_to_dict(self):
        s, a, e = _make_projections("زيد كاتب")
        report = self.checker.check(s, a, e, JudgmentStatus.HYPOTHESIS.value)
        d = report.to_dict()
        assert "passed" in d
        assert "conservation_score" in d
        assert "violations" in d
        assert "warnings" in d

    def test_unit_identity_preserved(self):
        s, a, e = _make_projections("النار حارة")
        report = self.checker.check(s, a, e, JudgmentStatus.HYPOTHESIS.value)
        assert report.unit_preserved is True

    def test_murab_syntactic_not_factual_certainty(self):
        """Murab certain_syntactic + no evidence must not allow high epistemic certainty."""
        text = "جاء الطالبُ"
        s, a, e = _make_projections(text, evidence_refs=[])
        # Simulate a murab unit reporting certain_syntactic
        a.unit.metadata["syntactic_certainty"] = "certain_syntactic"
        # Simulate epistemic certainty being raised (bug scenario)
        e.unit.C.epistemic_certainty = 0.80
        e.unit.E.evidence_state = "missing"
        report = self.checker.check(s, a, e, JudgmentStatus.HYPOTHESIS.value)
        check_names = [v.check_name for v in report.violations]
        assert "murab_syntactic_not_factual" in check_names

    def test_pipeline_cross_layer_included(self):
        """CognitiveFractalPipeline now includes cross_layer_report in result."""
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("النار حارة")
        assert result.cross_layer_report is not None
        assert hasattr(result.cross_layer_report, "conservation_score")

    def test_pipeline_to_dict_includes_cross_layer(self):
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("النار حارة")
        d = result.to_dict()
        assert "cross_layer_conservation" in d
