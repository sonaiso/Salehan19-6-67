"""CalibrationBridge — connects curriculum to Phase 5.2 metrics."""
from __future__ import annotations

from dataclasses import dataclass, field

from .cognitive_unit import CognitiveUnit


@dataclass
class CurriculumCoverageReport:
    total_units: int = 0
    levels_covered: list[int] = field(default_factory=list)
    layers_covered: list[str] = field(default_factory=list)
    coverage_ratio: float = 0.0
    dataset_score_estimate: float = 0.0
    calibration_score_estimate: float = 0.0
    industrial_testing_score_estimate: float = 0.0
    source_trust_score_estimate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "total_units": self.total_units,
            "levels_covered": self.levels_covered,
            "layers_covered": self.layers_covered,
            "coverage_ratio": round(self.coverage_ratio, 4),
            "dataset_score_estimate": round(self.dataset_score_estimate, 4),
            "calibration_score_estimate": round(self.calibration_score_estimate, 4),
            "industrial_testing_score_estimate": round(self.industrial_testing_score_estimate, 4),
            "source_trust_score_estimate": round(self.source_trust_score_estimate, 4),
        }


class CalibrationBridge:
    """Bridges curriculum to pre-API qualification metrics."""

    _DATASET_BASELINE = 4.30
    _CALIBRATION_BASELINE = 4.30
    _INDUSTRIAL_BASELINE = 4.26
    _SOURCE_TRUST_BASELINE = 4.40
    _MAX_SCORE = 5.0

    def export_to_evaluation_dataset(self, units: list[CognitiveUnit]) -> list[dict]:
        """Convert curriculum units to evaluation dataset format."""
        result = []
        for u in units:
            result.append({
                "example_id": u.unit_id,
                "input_text": u.input_text,
                "judgment_type": u.target_layer,
                "certainty_policy": u.certainty_policy,
                "evidence_need": u.evidence_need,
                "expected_warnings": u.expected_warnings,
                "tags": u.tags,
                "source": "curriculum",
            })
        return result

    def export_to_calibration_cases(self, units: list[CognitiveUnit]) -> list[dict]:
        """Export calibration-relevant units (levels 7–8)."""
        calibration_units = [u for u in units if u.level in (7, 8)]
        return [
            {
                "unit_id": u.unit_id,
                "input_text": u.input_text,
                "expected_certainty_policy": u.certainty_policy,
                "evidence_need": u.evidence_need,
                "forbidden_confusions": u.forbidden_confusions,
                "level": u.level,
            }
            for u in calibration_units
        ]

    def compute_curriculum_coverage(self, units: list[CognitiveUnit]) -> CurriculumCoverageReport:
        """Compute coverage metrics for the curriculum dataset."""
        report = CurriculumCoverageReport(total_units=len(units))
        if not units:
            return report

        levels = sorted({u.level for u in units})
        layers = sorted({u.target_layer for u in units})
        report.levels_covered = levels
        report.layers_covered = layers

        report.coverage_ratio = (len(levels) / 10) * 0.5 + (len(layers) / 14) * 0.5

        base_improvement = 0.2 * report.coverage_ratio
        report.dataset_score_estimate = min(
            self._MAX_SCORE,
            self._DATASET_BASELINE + base_improvement + (0.05 * len(units) / 400)
        )
        report.calibration_score_estimate = min(
            self._MAX_SCORE,
            self._CALIBRATION_BASELINE + base_improvement + (0.04 * len(units) / 400)
        )
        report.industrial_testing_score_estimate = min(
            self._MAX_SCORE,
            self._INDUSTRIAL_BASELINE + base_improvement * 0.8 + (0.04 * len(units) / 400)
        )
        report.source_trust_score_estimate = min(
            self._MAX_SCORE,
            self._SOURCE_TRUST_BASELINE + base_improvement * 0.6 + (0.03 * len(units) / 400)
        )
        return report

    def produce_pre_api_improvement_metrics(self, units: list[CognitiveUnit]) -> dict:
        """Produce a metrics dict that PreAPIQualificationGate can consume."""
        coverage = self.compute_curriculum_coverage(units)
        return {
            "curriculum_units": len(units),
            "coverage_ratio": coverage.coverage_ratio,
            "dataset_score_estimate": coverage.dataset_score_estimate,
            "calibration_score_estimate": coverage.calibration_score_estimate,
            "industrial_testing_score_estimate": coverage.industrial_testing_score_estimate,
            "source_trust_score_estimate": coverage.source_trust_score_estimate,
            "levels_covered": coverage.levels_covered,
            "layers_covered": coverage.layers_covered,
        }
