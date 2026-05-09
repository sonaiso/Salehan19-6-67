"""ResidualDatasetBuilder — converts CognitiveResiduals to dataset entries."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from .residual_schema import CognitiveResidual
from .proposal_schema import GPTProposal


@dataclass
class CurriculumUnit:
    unit_id: str
    input_text: str
    expected_residual_types: list[str]
    explanation: str
    level: int
    domain: str

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "input_text": self.input_text,
            "expected_residual_types": self.expected_residual_types,
            "explanation": self.explanation,
            "level": self.level,
            "domain": self.domain,
        }


@dataclass
class AdversarialCase:
    case_id: str
    input_text: str
    gpt_output: str
    expected_residual_types: list[str]
    severity: str
    explanation: str

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "input_text": self.input_text,
            "gpt_output": self.gpt_output,
            "expected_residual_types": self.expected_residual_types,
            "severity": self.severity,
            "explanation": self.explanation,
        }


@dataclass
class CalibrationCase:
    case_id: str
    input_text: str
    gpt_output: str
    residual_types: list[str]
    calibration_metrics: list[str]
    proposed_threshold_changes: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "input_text": self.input_text,
            "gpt_output": self.gpt_output,
            "residual_types": self.residual_types,
            "calibration_metrics": self.calibration_metrics,
            "proposed_threshold_changes": self.proposed_threshold_changes,
        }


@dataclass
class RegressionTestSpec:
    spec_id: str
    test_name: str
    input_text: str
    expected_residual_types: list[str]
    forbidden_behaviors: list[str]
    severity: str

    def to_dict(self) -> dict:
        return {
            "spec_id": self.spec_id,
            "test_name": self.test_name,
            "input_text": self.input_text,
            "expected_residual_types": self.expected_residual_types,
            "forbidden_behaviors": self.forbidden_behaviors,
            "severity": self.severity,
        }


# Calibration metric → threshold nudge (recommendation only, never auto-applied)
_METRIC_THRESHOLD_NUDGE: dict[str, float] = {
    "false_certainty_rate": -0.05,
    "suspension_correctness": +0.03,
    "evidence_need_accuracy": +0.05,
    "harm_haram_separation": +0.1,
    "source_required_detection": +0.05,
    "metaphor_literalization": -0.03,
    "api_as_evidence_rejection": +0.08,
}


class ResidualDatasetBuilder:
    """Converts CognitiveResiduals to various dataset formats (all JSONL serializable)."""

    def residual_to_curriculum_unit(
        self, residual: CognitiveResidual, proposal: GPTProposal | None = None
    ) -> CurriculumUnit:
        input_text = proposal.input_text if proposal else "(unknown input)"
        return CurriculumUnit(
            unit_id=f"CU-{uuid.uuid4().hex[:8]}",
            input_text=input_text,
            expected_residual_types=list(residual.residual_types),
            explanation=residual.explanation,
            level=self._level_from_severity(residual.severity),
            domain="residual_learning",
        )

    def residual_to_adversarial_case(
        self, residual: CognitiveResidual, proposal: GPTProposal | None = None
    ) -> AdversarialCase:
        input_text = proposal.input_text if proposal else "(unknown input)"
        gpt_output = proposal.gpt_output if proposal else "(unknown output)"
        return AdversarialCase(
            case_id=f"ADV-{uuid.uuid4().hex[:8]}",
            input_text=input_text,
            gpt_output=gpt_output,
            expected_residual_types=list(residual.residual_types),
            severity=residual.severity,
            explanation=residual.explanation,
        )

    def residual_to_calibration_case(
        self, residual: CognitiveResidual, proposal: GPTProposal | None = None
    ) -> CalibrationCase:
        from .residual_classifier import ResidualClassifier
        cls = ResidualClassifier().classify(residual)
        threshold_changes = {
            m: _METRIC_THRESHOLD_NUDGE.get(m, 0.0)
            for m in cls.target_calibration_metrics
        }
        input_text = proposal.input_text if proposal else "(unknown input)"
        gpt_output = proposal.gpt_output if proposal else "(unknown output)"
        return CalibrationCase(
            case_id=f"CAL-{uuid.uuid4().hex[:8]}",
            input_text=input_text,
            gpt_output=gpt_output,
            residual_types=list(residual.residual_types),
            calibration_metrics=list(cls.target_calibration_metrics),
            proposed_threshold_changes=threshold_changes,
        )

    def residual_to_regression_test_spec(
        self, residual: CognitiveResidual, proposal: GPTProposal | None = None
    ) -> RegressionTestSpec:
        from .residual_classifier import ResidualClassifier
        cls = ResidualClassifier().classify(residual)
        input_text = proposal.input_text if proposal else "(unknown input)"
        test_name = f"test_residual_{residual.proposal_id.replace('-', '_')}"
        forbidden = []
        for t in residual.residual_types:
            if "certainty" in t:
                forbidden.append("near_certainty_without_evidence")
            if "evidence" in t:
                forbidden.append("gpt_as_evidence")
            if "harm" in t:
                forbidden.append("harm_entails_haram")
            if "tool" in t:
                forbidden.append("api_as_authority")
            if "injection" in t:
                forbidden.append("follow_injection_instruction")
        return RegressionTestSpec(
            spec_id=f"REG-{uuid.uuid4().hex[:8]}",
            test_name=test_name,
            input_text=input_text,
            expected_residual_types=list(residual.residual_types),
            forbidden_behaviors=list(set(forbidden)),
            severity=residual.severity,
        )

    @staticmethod
    def _level_from_severity(severity: str) -> int:
        mapping = {"low": 1, "medium": 2, "high": 3, "blocking": 4}
        return mapping.get(severity, 1)
