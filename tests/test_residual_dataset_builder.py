"""Tests for ResidualDatasetBuilder."""
from __future__ import annotations

import json
import pytest
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalType
from mcd.residual_learning.residual_schema import CognitiveResidual, ResidualType, Severity
from mcd.residual_learning.residual_dataset_builder import ResidualDatasetBuilder


def make_proposal(**kwargs) -> GPTProposal:
    defaults = dict(
        proposal_id="ds-test",
        input_text="هل هذا صحيح؟",
        gpt_output="نعم هذا صحيح.",
        proposal_type=ProposalType.ANSWER,
        claimed_evidence=[],
        claimed_certainty=None,
        metadata={},
    )
    defaults.update(kwargs)
    return GPTProposal(**defaults)


def make_residual(types: list[str], severity: str = Severity.HIGH.value) -> CognitiveResidual:
    return CognitiveResidual(
        residual_id="r-test",
        proposal_id="ds-test",
        residual_types=types,
        severity=severity,
        residual_score=0.5,
        explanation="Test residual",
    )


class TestResidualDatasetBuilder:
    def setup_method(self) -> None:
        self.builder = ResidualDatasetBuilder()
        self.proposal = make_proposal()

    def test_residual_to_adversarial_case(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value])
        case = self.builder.residual_to_adversarial_case(r, self.proposal)
        assert case.case_id.startswith("ADV-")
        assert case.input_text == self.proposal.input_text
        assert ResidualType.CERTAINTY.value in case.expected_residual_types

    def test_adversarial_case_jsonl_serializable(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)
        case = self.builder.residual_to_adversarial_case(r, self.proposal)
        json.dumps(case.to_dict())  # should not raise

    def test_residual_to_curriculum_unit(self) -> None:
        r = make_residual([ResidualType.METAPHOR.value], Severity.MEDIUM.value)
        unit = self.builder.residual_to_curriculum_unit(r, self.proposal)
        assert unit.unit_id.startswith("CU-")
        assert unit.level == 2  # medium → level 2

    def test_residual_to_calibration_case(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value, ResidualType.EVIDENCE.value])
        case = self.builder.residual_to_calibration_case(r, self.proposal)
        assert case.case_id.startswith("CAL-")
        assert "false_certainty_rate" in case.calibration_metrics or "evidence_need_accuracy" in case.calibration_metrics

    def test_calibration_case_has_threshold_changes(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)
        case = self.builder.residual_to_calibration_case(r, self.proposal)
        assert isinstance(case.proposed_threshold_changes, dict)

    def test_residual_to_regression_test_spec(self) -> None:
        r = make_residual([ResidualType.TOOL_EVIDENCE.value], Severity.HIGH.value)
        spec = self.builder.residual_to_regression_test_spec(r, self.proposal)
        assert spec.spec_id.startswith("REG-")
        assert "api_as_authority" in spec.forbidden_behaviors

    def test_regression_spec_jsonl_serializable(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value], Severity.HIGH.value)
        spec = self.builder.residual_to_regression_test_spec(r, self.proposal)
        json.dumps(spec.to_dict())  # should not raise

    def test_blocking_maps_to_level_4(self) -> None:
        r = make_residual([ResidualType.INJECTION.value], Severity.BLOCKING.value)
        unit = self.builder.residual_to_curriculum_unit(r, self.proposal)
        assert unit.level == 4

    def test_without_proposal_uses_placeholder(self) -> None:
        r = make_residual([ResidualType.EVIDENCE.value])
        case = self.builder.residual_to_adversarial_case(r, None)
        assert "(unknown input)" in case.input_text
