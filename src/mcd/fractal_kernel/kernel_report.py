from __future__ import annotations
from .kernel_validator import KernelValidationReport


class KernelReport:
    """Generate human-readable reports from KernelValidationReport."""

    def generate_markdown(self, report: KernelValidationReport, extra_notes: str = "") -> str:
        lines = [
            "# Fractal Geometry Kernel Validation Report",
            "",
            f"**Overall Score**: {report.kernel_validation_score:.4f}",
            f"**Passed**: {'✅ Yes' if report.passed else '❌ No'}",
            "",
            "## Component Scores",
            f"| Component | Score |",
            f"|-----------|-------|",
            f"| Unit Validity | {report.unit_validity_score:.4f} |",
            f"| Vector Validity | {report.vector_validity_score:.4f} |",
            f"| Morphism Validity | {report.morphism_validity_score:.4f} |",
            f"| Fold Law | {report.fold_law_score:.4f} |",
            f"| Conflict Resolution | {report.conflict_resolution_score:.4f} |",
            f"| Proof+Trace | {report.proof_trace_score:.4f} |",
            f"| Jami/Mani | {report.jami_mani_score:.4f} |",
            "",
        ]
        if report.violations:
            lines.append("## Violations")
            for v in report.violations:
                lines.append(f"- ❌ {v}")
            lines.append("")
        if report.warnings:
            lines.append("## Warnings")
            for w in report.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")
        if extra_notes:
            lines.append("## Notes")
            lines.append(extra_notes)
        return "\n".join(lines)

    def generate_json_summary(self, report: KernelValidationReport) -> dict:
        return report.to_dict()
