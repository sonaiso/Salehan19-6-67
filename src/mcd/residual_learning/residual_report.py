"""ResidualReport — generates a summary report for a set of CognitiveResiduals."""
from __future__ import annotations

from dataclasses import dataclass, field

from .residual_schema import CognitiveResidual, Severity


@dataclass
class ResidualReport:
    total: int
    by_severity: dict[str, int]
    by_type: dict[str, int]
    blocking_count: int
    high_count: int
    adversarial_candidates: int
    calibration_recommendations: int
    gpt_used_as_evidence: bool

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "by_severity": self.by_severity,
            "by_type": self.by_type,
            "blocking_count": self.blocking_count,
            "high_count": self.high_count,
            "adversarial_candidates": self.adversarial_candidates,
            "calibration_recommendations": self.calibration_recommendations,
            "gpt_used_as_evidence": self.gpt_used_as_evidence,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Cognitive Residual Learning Report",
            "",
            f"- **Total Residuals**: {self.total}",
            f"- **Blocking**: {self.blocking_count}",
            f"- **High**: {self.high_count}",
            f"- **Adversarial Candidates**: {self.adversarial_candidates}",
            f"- **Calibration Recommendations**: {self.calibration_recommendations}",
            f"- **GPT Output Used as Evidence**: {'❌ YES — VIOLATION' if self.gpt_used_as_evidence else '✅ No'}",
            "",
            "## Residuals by Severity",
        ]
        for s in (Severity.BLOCKING.value, Severity.HIGH.value, Severity.MEDIUM.value, Severity.LOW.value):
            count = self.by_severity.get(s, 0)
            lines.append(f"- `{s}`: {count}")
        lines += ["", "## Residuals by Type"]
        for t, count in sorted(self.by_type.items(), key=lambda x: -x[1]):
            lines.append(f"- `{t}`: {count}")
        return "\n".join(lines)

    @classmethod
    def build(cls, residuals: list[CognitiveResidual]) -> "ResidualReport":
        by_severity: dict[str, int] = {}
        by_type: dict[str, int] = {}
        blocking = 0
        high = 0
        adversarial = 0
        calibration = 0
        gpt_as_evidence = False

        for r in residuals:
            by_severity[r.severity] = by_severity.get(r.severity, 0) + 1
            for t in r.residual_types:
                by_type[t] = by_type.get(t, 0) + 1
            if r.severity == Severity.BLOCKING.value:
                blocking += 1
                adversarial += 1
            if r.severity == Severity.HIGH.value:
                high += 1
                adversarial += 1
                calibration += 1
            if any("gpt_output_as_evidence" in g for g in r.evidence_gaps):
                gpt_as_evidence = True

        return cls(
            total=len(residuals),
            by_severity=by_severity,
            by_type=by_type,
            blocking_count=blocking,
            high_count=high,
            adversarial_candidates=adversarial,
            calibration_recommendations=calibration,
            gpt_used_as_evidence=gpt_as_evidence,
        )
