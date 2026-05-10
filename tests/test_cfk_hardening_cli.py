"""Tests for Phase 8.1 — CFK Hardening CLI commands."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure src is on path for subprocess calls
_SRC = str(Path(__file__).parent.parent / "src")


def _run(args: list[str]) -> tuple[int, str, str]:
    """Run `python -m mcd.cli <args>` and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + args,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": _SRC},
    )
    return result.returncode, result.stdout, result.stderr


class TestCFKValidateCLI:
    def test_cfk_validate_json_output(self):
        rc, out, err = _run([
            "cfk-validate",
            "--text", "النار حارة",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        assert "cfk_validation_score" in data
        assert "all_passed" in data
        assert "checks" in data

    def test_cfk_validate_score_is_float(self):
        rc, out, _ = _run([
            "cfk-validate",
            "--text", "النار حارة",
            "--output", "json",
        ])
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data["cfk_validation_score"], float)

    def test_cfk_validate_text_output(self):
        rc, out, err = _run([
            "cfk-validate",
            "--text", "زيد كاتب",
            "--output", "text",
        ])
        assert rc == 0, f"STDERR: {err}"
        assert "CFK Validation Score" in out

    def test_cfk_validate_with_evidence(self):
        rc, out, _ = _run([
            "cfk-validate",
            "--text", "النار حارة",
            "--evidence", "empirical_1,exp_2",
            "--output", "json",
        ])
        assert rc == 0
        data = json.loads(out)
        assert "cfk_validation_score" in data

    def test_cfk_validate_default_text(self):
        """cfk-validate works with just --output flag (default text)."""
        rc, out, err = _run([
            "cfk-validate",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"


class TestCFKIntegrationReportCLI:
    def test_cfk_integration_report_markdown(self):
        rc, out, err = _run([
            "cfk-integration-report",
            "--text", "النار حارة",
            "--output", "markdown",
        ])
        assert rc == 0, f"STDERR: {err}"
        assert "CFK Integration Contract Report" in out
        assert "Phase 8.1" in out

    def test_cfk_integration_report_json(self):
        rc, out, err = _run([
            "cfk-integration-report",
            "--text", "زيد كاتب",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        assert "cfk_validation_score" in data
        assert "contracts" in data
        assert "cross_layer_conservation_score" in data

    def test_cfk_integration_report_contains_contracts(self):
        rc, out, _ = _run([
            "cfk-integration-report",
            "--output", "markdown",
        ])
        assert rc == 0
        assert "statistical_transform" in out or "الطبقة" in out


class TestCFKConservationCLI:
    def test_cfk_conservation_json_basic(self):
        rc, out, err = _run([
            "cfk-conservation",
            "--text", "كل الشركات تستخدم GraphRAG",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        assert "conservation_score" in data
        assert "passed" in data
        assert data["text"] == "كل الشركات تستخدم GraphRAG"

    def test_cfk_conservation_universal_no_evidence(self):
        """Universal quantifier without evidence should have violations or warnings."""
        rc, out, err = _run([
            "cfk-conservation",
            "--text", "كل الشركات تستخدم GraphRAG",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        # Either violations or warnings should be non-empty, or score < 1.0
        assert (
            len(data.get("violations", [])) > 0
            or len(data.get("warnings", [])) > 0
            or data["conservation_score"] < 1.0
        )

    def test_cfk_conservation_score_range(self):
        rc, out, _ = _run([
            "cfk-conservation",
            "--text", "النار حارة",
            "--evidence", "e1,e2",
            "--output", "json",
        ])
        assert rc == 0
        data = json.loads(out)
        assert 0.0 <= data["conservation_score"] <= 1.0


class TestCFKReverseTraceCLI:
    def test_cfk_reverse_trace_markdown(self):
        rc, out, err = _run([
            "cfk-reverse-trace",
            "--text", "النار حارة",
            "--evidence", "empirical_1,exp_2",
            "--output", "markdown",
        ])
        assert rc == 0, f"STDERR: {err}"
        assert "CFK Reverse Trace Report" in out
        assert "Phase 8.1" in out

    def test_cfk_reverse_trace_json(self):
        rc, out, err = _run([
            "cfk-reverse-trace",
            "--text", "النار حارة",
            "--evidence", "empirical_1,exp_2",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        assert "reverse_trace_id" in data
        assert "final_judgment" in data
        assert "complete" in data

    def test_cfk_reverse_trace_has_projection_ids(self):
        rc, out, _ = _run([
            "cfk-reverse-trace",
            "--text", "النار حارة",
            "--evidence", "empirical_1,exp_2",
            "--output", "json",
        ])
        assert rc == 0
        data = json.loads(out)
        assert data["statistical_projection_id"].startswith("KP-S-")
        assert data["arabic_projection_id"].startswith("KP-A-")
        assert data["epistemic_projection_id"].startswith("KP-E-")

    def test_cfk_reverse_trace_no_evidence(self):
        """Reverse trace without evidence should be incomplete."""
        rc, out, err = _run([
            "cfk-reverse-trace",
            "--text", "زيد كاتب",
            "--output", "json",
        ])
        assert rc == 0, f"STDERR: {err}"
        data = json.loads(out)
        # No evidence → trace should be incomplete
        assert data["complete"] is False

    def test_cfk_reverse_trace_with_evidence(self):
        """Reverse trace with evidence should record them."""
        rc, out, _ = _run([
            "cfk-reverse-trace",
            "--text", "النار حارة",
            "--evidence", "e1,e2",
            "--output", "json",
        ])
        assert rc == 0
        data = json.loads(out)
        assert "e1" in data["evidence_refs"]
        assert "e2" in data["evidence_refs"]


# ---------------------------------------------------------------------------
# Hardening critical tests (via pipeline)
# ---------------------------------------------------------------------------

class TestCFKHardeningCritical:
    """Critical hardening tests that must pass for the PR to be accepted."""

    def test_gpt_high_confidence_without_evidence_not_certificate(self):
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        from mcd.cfk.cfk_schema import JudgmentStatus
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run(
            "الأرض كروية",
            proposal_dict={
                "proposal_id": "P-high",
                "gpt_output": "الأرض كروية",
                "input_text": "الأرض كروية",
                "proposal_type": "answer",
                "claimed_certainty": "near_certainty",
                "claimed_evidence": [],
            },
            evidence_refs=[],
        )
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_emphasis_without_evidence_not_certificate(self):
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        from mcd.cfk.cfk_schema import JudgmentStatus
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("إن هذا لحق", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_universal_without_evidence_suspend(self):
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        from mcd.cfk.cfk_schema import JudgmentStatus
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("كل الشركات تستخدم GraphRAG", evidence_refs=[])
        assert result.proof.judgment in (
            JudgmentStatus.SUSPEND.value,
            JudgmentStatus.HYPOTHESIS.value,
        )
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_murab_syntactic_certainty_not_factual_certainty(self):
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        from mcd.cfk.cfk_schema import JudgmentStatus
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("جاء الطالبُ", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_trace_completeness_not_truth(self):
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        from mcd.cfk.cfk_schema import JudgmentStatus
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("النار حارة", evidence_refs=[])
        assert result.proof.judgment != JudgmentStatus.CERTIFICATE.value

    def test_fake_evidence_forces_zero(self):
        """Fake evidence detection should force judgment to zero.

        The FractalKernel forces judgment=zero when the epistemic projection
        already carries judgment=zero (which is set when fake_evidence_detected=True
        in EpistemicTransform). We simulate this by directly exercising the kernel rule.
        """
        from mcd.cfk.cfk_schema import JudgmentStatus
        from mcd.cfk.fractal_kernel import FractalKernel
        from mcd.cfk.statistical_transform import StatisticalTransform
        from mcd.cfk.arabic_semantic_transform import ArabicSemanticTransform
        from mcd.cfk.epistemic_transform import EpistemicTransform

        stat = StatisticalTransform()
        arab = ArabicSemanticTransform()
        epis_proj = EpistemicTransform().transform("test", statistical_confidence=0.5)

        # Manually force zero judgment on the epistemic projection (simulates fake evidence)
        epis_proj.judgment = JudgmentStatus.ZERO.value
        epis_proj.unit.metadata["fake_evidence_detected"] = True

        stat_proj = stat.transform({
            "proposal_id": "P-fake",
            "gpt_output": "test",
            "input_text": "test",
            "proposal_type": "answer",
            "claimed_certainty": "near_certainty",
            "claimed_evidence": [],
        })
        arab_proj = arab.transform("test")

        kernel = FractalKernel()
        result = kernel.apply("test", stat_proj, arab_proj, epis_proj)
        assert result.kernel_judgment == JudgmentStatus.ZERO.value

    def test_cross_layer_conservation_score_above_095(self):
        """A well-formed run with evidence should score ≥ 0.95."""
        from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
        pipeline = CognitiveFractalPipeline()
        result = pipeline.run("النار حارة", evidence_refs=["e1", "e2"])
        assert result.cross_layer_report is not None
        assert result.cross_layer_report.conservation_score >= 0.95
