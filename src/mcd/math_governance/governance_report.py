from __future__ import annotations

from mcd.math_governance.governance_gate import MathematicalGovernanceReport


class GovernanceReportBuilder:
    def markdown(self, report: MathematicalGovernanceReport) -> str:
        lines = [
            "# Mathematical Function Governance Report",
            "",
            f"- Passed: {'✅' if report.passed else '❌'}",
            f"- Governance score: {report.governance_score:.4f}",
            f"- Morphism score: {report.morphism_score:.4f}",
            f"- Operator law score: {report.operator_law_score:.4f}",
            f"- Fold stability score: {report.fold_stability_score:.4f}",
            f"- Jami score: {report.jami_score:.4f}",
            f"- Mani score: {report.mani_score:.4f}",
            f"- Dataset annotation score: {report.dataset_annotation_score:.4f}",
        ]
        if report.violations:
            lines.append("\n## Violations")
            lines.extend([f"- {v}" for v in report.violations])
        if report.warnings:
            lines.append("\n## Warnings")
            lines.extend([f"- {w}" for w in report.warnings])
        return "\n".join(lines)
