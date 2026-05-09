"""Tests for ResidualClassifier."""
from __future__ import annotations

import pytest
from mcd.residual_learning.residual_schema import CognitiveResidual, ResidualType, Severity
from mcd.residual_learning.residual_classifier import ResidualClassifier


def make_residual(
    types: list[str],
    severity: str = Severity.LOW.value,
) -> CognitiveResidual:
    return CognitiveResidual(
        residual_id="cls-test",
        proposal_id="p-001",
        residual_types=types,
        severity=severity,
        residual_score=0.5,
        explanation="Test residual",
    )


class TestResidualClassifier:
    def setup_method(self) -> None:
        self.classifier = ResidualClassifier()

    def test_empty_residual_gives_low_priority(self) -> None:
        r = make_residual(types=[])
        cls = self.classifier.classify(r)
        assert cls.learning_priority == "low"

    def test_harm_haram_is_blocking(self) -> None:
        r = make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)
        cls = self.classifier.classify(r)
        assert cls.learning_priority == "blocking"
        assert "invariant" in cls.target_datasets
        assert "regression_test" in cls.target_datasets

    def test_injection_is_blocking(self) -> None:
        r = make_residual([ResidualType.INJECTION.value], Severity.BLOCKING.value)
        cls = self.classifier.classify(r)
        assert cls.learning_priority == "blocking"

    def test_certainty_residual_is_high(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value], Severity.HIGH.value)
        cls = self.classifier.classify(r)
        assert cls.learning_priority == "high"
        assert "adversarial" in cls.target_datasets
        assert "calibration" in cls.target_datasets

    def test_evidence_residual_targets_calibration(self) -> None:
        r = make_residual([ResidualType.EVIDENCE.value], Severity.HIGH.value)
        cls = self.classifier.classify(r)
        assert "calibration" in cls.target_datasets
        assert "evidence_need_accuracy" in cls.target_calibration_metrics

    def test_metaphor_residual_targets_curriculum(self) -> None:
        r = make_residual([ResidualType.METAPHOR.value], Severity.MEDIUM.value)
        cls = self.classifier.classify(r)
        assert "curriculum" in cls.target_datasets

    def test_tool_evidence_targets_adversarial(self) -> None:
        r = make_residual([ResidualType.TOOL_EVIDENCE.value], Severity.HIGH.value)
        cls = self.classifier.classify(r)
        assert "adversarial" in cls.target_datasets
        assert "api_as_evidence_rejection" in cls.target_calibration_metrics

    def test_suggested_tests_populated(self) -> None:
        r = make_residual([ResidualType.CERTAINTY.value], Severity.HIGH.value)
        cls = self.classifier.classify(r)
        assert len(cls.suggested_tests) > 0

    def test_multiple_types_merge_datasets(self) -> None:
        r = make_residual(
            [ResidualType.CERTAINTY.value, ResidualType.HARM_HARAM.value],
            Severity.BLOCKING.value,
        )
        cls = self.classifier.classify(r)
        # Should include both adversarial (from certainty) and invariant (from harm_haram)
        assert "adversarial" in cls.target_datasets or "calibration" in cls.target_datasets
        assert "invariant" in cls.target_datasets

    def test_classification_has_residual_id(self) -> None:
        r = make_residual([ResidualType.EVIDENCE.value])
        cls = self.classifier.classify(r)
        assert cls.residual_id == r.residual_id

    def test_to_dict_serializable(self) -> None:
        import json
        r = make_residual([ResidualType.METAPHOR.value], Severity.MEDIUM.value)
        cls = self.classifier.classify(r)
        d = cls.to_dict()
        json.dumps(d)  # should not raise
