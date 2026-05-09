"""ResidualCalibrationEngine — uses residuals to propose calibration updates.

Does NOT apply threshold updates automatically.
Presents them as recommendations only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .residual_schema import CognitiveResidual, ResidualType, Severity
from .residual_classifier import ResidualClassifier


@dataclass
class ResidualCalibrationReport:
    residual_count: int
    residuals_by_type: dict[str, int]
    high_priority_count: int
    blocking_count: int
    proposed_threshold_updates: dict[str, float]
    calibration_warnings: list[str]
    expected_metric_impact: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "residual_count": self.residual_count,
            "residuals_by_type": self.residuals_by_type,
            "high_priority_count": self.high_priority_count,
            "blocking_count": self.blocking_count,
            "proposed_threshold_updates": self.proposed_threshold_updates,
            "calibration_warnings": self.calibration_warnings,
            "expected_metric_impact": self.expected_metric_impact,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Residual Calibration Report",
            "",
            f"- **Total Residuals**: {self.residual_count}",
            f"- **Blocking**: {self.blocking_count}",
            f"- **High Priority**: {self.high_priority_count}",
            "",
            "## Residuals by Type",
        ]
        for t, count in sorted(self.residuals_by_type.items(), key=lambda x: -x[1]):
            lines.append(f"- `{t}`: {count}")
        lines += [
            "",
            "## Proposed Threshold Updates (Recommendations Only)",
        ]
        for metric, delta in self.proposed_threshold_updates.items():
            sign = "+" if delta >= 0 else ""
            lines.append(f"- `{metric}`: {sign}{delta:+.3f}")
        if self.calibration_warnings:
            lines += ["", "## Calibration Warnings"]
            for w in self.calibration_warnings:
                lines.append(f"- ⚠️  {w}")
        lines += ["", "## Expected Metric Impact"]
        for metric, impact in self.expected_metric_impact.items():
            lines.append(f"- `{metric}`: {impact}")
        lines += [
            "",
            "---",
            "*Threshold updates are recommendations only. Human review required before applying.*",
        ]
        return "\n".join(lines)


# Metric → nudge mapping (recommendations only)
_METRIC_NUDGES: dict[str, float] = {
    "false_certainty_rate": -0.05,
    "suspension_correctness": +0.03,
    "evidence_need_accuracy": +0.05,
    "harm_haram_separation": +0.10,
    "source_required_detection": +0.05,
    "metaphor_literalization": -0.03,
    "api_as_evidence_rejection": +0.08,
    "injection_resistance": +0.10,
}

_METRIC_IMPACT: dict[str, str] = {
    "false_certainty_rate": "Reduce false certainty by tightening evidence requirement thresholds",
    "suspension_correctness": "Increase correct suspend-judgment rate for ambiguous inputs",
    "evidence_need_accuracy": "Improve evidence requirement detection precision",
    "harm_haram_separation": "Enforce strict separation between harm and haram domains",
    "source_required_detection": "Better detection of unsupported generalizations",
    "metaphor_literalization": "Reduce metaphor-as-literal errors in output",
    "api_as_evidence_rejection": "Increase rejection rate of API/tool outputs used as primary evidence",
    "injection_resistance": "Improve resistance to prompt injection attacks",
}


class ResidualCalibrationEngine:
    """Analyses a set of residuals and produces calibration recommendations."""

    def __init__(self) -> None:
        self._classifier = ResidualClassifier()

    def generate_report(self, residuals: list[CognitiveResidual]) -> ResidualCalibrationReport:
        residuals_by_type: dict[str, int] = {}
        high_count = 0
        blocking_count = 0
        metrics_hit: dict[str, int] = {}
        warnings: list[str] = []

        for r in residuals:
            if r.severity == Severity.BLOCKING.value:
                blocking_count += 1
            if r.severity in (Severity.HIGH.value, Severity.BLOCKING.value):
                high_count += 1

            for t in r.residual_types:
                residuals_by_type[t] = residuals_by_type.get(t, 0) + 1

            cls = self._classifier.classify(r)
            for m in cls.target_calibration_metrics:
                metrics_hit[m] = metrics_hit.get(m, 0) + 1

        # Build proposed threshold updates (weighted by frequency)
        proposed: dict[str, float] = {}
        for metric, hit_count in metrics_hit.items():
            base_nudge = _METRIC_NUDGES.get(metric, 0.0)
            # Scale nudge by how many residuals triggered it (cap at 3x)
            scale = min(hit_count, 3)
            proposed[metric] = round(base_nudge * scale, 4)

        # Calibration warnings
        if blocking_count > 0:
            warnings.append(
                f"{blocking_count} blocking residuals detected — immediate human review required."
            )
        if residuals_by_type.get(ResidualType.CERTAINTY.value, 0) > 5:
            warnings.append("High false-certainty rate — consider tightening certainty thresholds.")
        if residuals_by_type.get(ResidualType.EVIDENCE.value, 0) > 10:
            warnings.append("Evidence gaps frequent — consider requiring source citations for all claims.")
        if not residuals:
            warnings.append("No residuals provided — calibration report is empty.")

        expected_impact = {m: _METRIC_IMPACT.get(m, "Unknown impact") for m in proposed}

        return ResidualCalibrationReport(
            residual_count=len(residuals),
            residuals_by_type=residuals_by_type,
            high_priority_count=high_count,
            blocking_count=blocking_count,
            proposed_threshold_updates=proposed,
            calibration_warnings=warnings,
            expected_metric_impact=expected_impact,
        )
