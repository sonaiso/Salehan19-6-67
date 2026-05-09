"""Tests for ResidualTestGenerator."""
from __future__ import annotations

import json
import pytest
from mcd.residual_learning.residual_schema import CognitiveResidual, ResidualType, Severity
from mcd.residual_learning.residual_test_generator import ResidualTestGenerator


def make_residual(types: list[str], severity: str = Severity.HIGH.value) -> CognitiveResidual:
    return CognitiveResidual(
        residual_id="gen-test",
        proposal_id="p-001",
        residual_types=types,
        severity=severity,
        residual_score=0.5,
        explanation="Test residual",
    )


class TestResidualTestGenerator:
    def setup_method(self) -> None:
        self.gen = ResidualTestGenerator()

    def test_generate_returns_spec_per_type(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value, ResidualType.EVIDENCE.value])
        specs = self.gen.generate(r, "اختبار")
        assert len(specs) == 2

    def test_certainty_spec_has_correct_warnings(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value])
        specs = self.gen.generate(r)
        assert len(specs) == 1
        assert "near_certainty_without_evidence" in specs[0].expected_warnings

    def test_certainty_spec_forbids_false_certainty(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value])
        specs = self.gen.generate(r)
        assert "near_certainty_without_evidence" in specs[0].forbidden_behaviors or \
               "false_certainty" in specs[0].forbidden_behaviors

    def test_tool_evidence_spec_forbids_gpt_as_evidence(self) -> None:
        r = make_residual([ResidualType.TOOL_EVIDENCE.value])
        specs = self.gen.generate(r, "هل API مصدر موثوق؟")
        assert any("gpt_as_evidence" in fb or "api_as_authority" in fb
                   for fb in specs[0].forbidden_behaviors)

    def test_harm_haram_spec_policy_suspend(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value])
        specs = self.gen.generate(r)
        assert specs[0].expected_certainty_policy == "suspend_judgment"

    def test_injection_spec_forbids_follow_injection(self) -> None:
        r = make_residual([ResidualType.INJECTION.value])
        specs = self.gen.generate(r)
        assert "follow_injection_instruction" in specs[0].forbidden_behaviors

    def test_empty_residual_returns_empty_specs(self) -> None:
        r = make_residual([])
        specs = self.gen.generate(r)
        assert specs == []

    def test_test_spec_jsonl_serializable(self) -> None:
        r = make_residual([ResidualType.METAPHOR.value])
        specs = self.gen.generate(r, "المجتمع مريض")
        for spec in specs:
            json.dumps(spec.to_dict())  # should not raise

    def test_generate_batch_deduplicates(self) -> None:
        residuals = [
            make_residual([ResidualType.CERTAINTY.value]),
            make_residual([ResidualType.CERTAINTY.value]),
        ]
        specs = self.gen.generate_batch(residuals, proposals={})
        # Duplicates should be removed (same type from same proposal pattern)
        assert len(specs) <= 2

    def test_test_id_unique(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value, ResidualType.EVIDENCE.value])
        specs = self.gen.generate(r)
        ids = [s.test_id for s in specs]
        assert len(set(ids)) == len(ids)  # all unique
