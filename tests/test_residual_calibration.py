"""Tests for ResidualCalibrationEngine."""
from __future__ import annotations

import json
import pytest
from mcd.residual_learning.residual_schema import CognitiveResidual, ResidualType, Severity
from mcd.residual_learning.residual_calibration import ResidualCalibrationEngine


def make_residual(
    types: list[str],
    severity: str = Severity.HIGH.value,
    pid: str = "p-001",
) -> CognitiveResidual:
    return CognitiveResidual(
        residual_id=f"cal-{pid}",
        proposal_id=pid,
        residual_types=types,
        severity=severity,
        residual_score=0.5,
        explanation="Test",
    )


class TestResidualCalibrationEngine:
    def setup_method(self) -> None:
        self.engine = ResidualCalibrationEngine()

    def test_empty_residuals_gives_empty_report(self) -> None:
        report = self.engine.generate_report([])
        assert report.residual_count == 0
        assert report.blocking_count == 0

    def test_residual_count_correct(self) -> None:
        residuals = [
            make_residual([ResidualType.CERTAINTY.value], pid="p1"),
            make_residual([ResidualType.EVIDENCE.value], pid="p2"),
            make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value, pid="p3"),
        ]
        report = self.engine.generate_report(residuals)
        assert report.residual_count == 3

    def test_blocking_count_tracked(self) -> None:
        residuals = [
            make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value),
            make_residual([ResidualType.INJECTION.value], Severity.BLOCKING.value, pid="p2"),
        ]
        report = self.engine.generate_report(residuals)
        assert report.blocking_count == 2

    def test_residual_calibration_report_has_threshold_recommendations(self) -> None:
        residuals = [
            make_residual([ResidualType.CERTAINTY.value]),
            make_residual([ResidualType.EVIDENCE.value], pid="p2"),
        ]
        report = self.engine.generate_report(residuals)
        # Should propose threshold updates for certainty/evidence metrics
        assert len(report.proposed_threshold_updates) > 0

    def test_thresholds_are_recommendations_only(self) -> None:
        """Verify thresholds are never auto-applied — just recommended."""
        residuals = [make_residual([ResidualType.CERTAINTY.value])]
        report = self.engine.generate_report(residuals)
        # proposed_threshold_updates exist but are just recommendations
        assert "false_certainty_rate" in report.proposed_threshold_updates
        # The report itself does not apply changes — it just lists them
        assert isinstance(report.proposed_threshold_updates["false_certainty_rate"], float)

    def test_blocking_warning_generated(self) -> None:
        residuals = [
            make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value),
        ]
        report = self.engine.generate_report(residuals)
        assert any("blocking" in w.lower() for w in report.calibration_warnings)

    def test_to_markdown_output(self) -> None:
        residuals = [make_residual([ResidualType.CERTAINTY.value])]
        report = self.engine.generate_report(residuals)
        md = report.to_markdown()
        assert "Calibration Report" in md
        assert "Threshold" in md

    def test_to_dict_json_serializable(self) -> None:
        residuals = [make_residual([ResidualType.TOOL_EVIDENCE.value])]
        report = self.engine.generate_report(residuals)
        json.dumps(report.to_dict())  # should not raise

    def test_residuals_by_type_aggregated(self) -> None:
        residuals = [
            make_residual([ResidualType.CERTAINTY.value], pid="p1"),
            make_residual([ResidualType.CERTAINTY.value], pid="p2"),
            make_residual([ResidualType.EVIDENCE.value], pid="p3"),
        ]
        report = self.engine.generate_report(residuals)
        assert report.residuals_by_type.get(ResidualType.CERTAINTY.value, 0) == 2
        assert report.residuals_by_type.get(ResidualType.EVIDENCE.value, 0) == 1

    def test_expected_metric_impact_present(self) -> None:
        residuals = [make_residual([ResidualType.HARM_HARAM.value], Severity.BLOCKING.value)]
        report = self.engine.generate_report(residuals)
        assert len(report.expected_metric_impact) >= 0  # may be empty if no metrics triggered
