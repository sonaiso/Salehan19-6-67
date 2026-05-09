"""Curriculum reporting."""
from __future__ import annotations

from .curriculum_evaluator import CurriculumEvaluationReport
from .curriculum_validator import CurriculumValidationReport
from .curriculum_schema import LEVEL_NAMES


def generate_curriculum_report(
    eval_report: CurriculumEvaluationReport | None = None,
    val_report: CurriculumValidationReport | None = None,
) -> str:
    lines = ["# Curriculum Report — Phase 5.3\n"]

    if val_report:
        lines.append("## Validation Summary\n")
        lines.append(f"- Total units: {val_report.total_units}")
        lines.append(f"- Valid units: {val_report.valid_units}")
        lines.append(f"- Invalid units: {val_report.invalid_units}")
        lines.append(f"- Status: {'✅ valid' if val_report.status == 'valid' else '❌ invalid'}")
        if val_report.errors:
            lines.append(f"\n### Errors ({len(val_report.errors)})\n")
            for e in val_report.errors[:20]:
                lines.append(f"- [{e.unit_id}] {e.field}: {e.message}")
        if val_report.warnings:
            lines.append(f"\n### Warnings ({len(val_report.warnings)})\n")
            for w in val_report.warnings[:10]:
                lines.append(f"- {w}")
        lines.append("")

    if eval_report:
        lines.append("## Evaluation Summary\n")
        lines.append(f"- Total units: {eval_report.total_units}")
        lines.append(f"- Overall score: {eval_report.overall_score:.4f}")
        lines.append(f"- Failed units: {len(eval_report.failed_units)}\n")

        lines.append("### Score by Level\n")
        lines.append("| Level | Name | Total | Score |")
        lines.append("|-------|------|-------|-------|")
        for ls in eval_report.score_by_level:
            name = LEVEL_NAMES.get(ls.level, "")
            lines.append(f"| {ls.level} | {name} | {ls.total} | {ls.score:.4f} |")

        lines.append("\n### Score by Layer\n")
        lines.append("| Layer | Total | Score |")
        lines.append("|-------|-------|-------|")
        for ls in eval_report.score_by_layer:
            lines.append(f"| {ls.layer} | {ls.total} | {ls.score:.4f} |")

        if eval_report.recommendations:
            lines.append("\n### Recommendations\n")
            for r in eval_report.recommendations:
                lines.append(f"- {r}")

    return "\n".join(lines)
