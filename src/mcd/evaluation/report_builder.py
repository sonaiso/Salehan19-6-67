"""Report Builder — generates Markdown industrial audit reports."""
from __future__ import annotations
import json
from datetime import datetime, timezone

from mcd.evaluation.repository_audit import RepositoryAuditResult
from mcd.evaluation.architecture_audit import ArchitectureAuditResult
from mcd.evaluation.test_audit import TestAuditResult
from mcd.evaluation.cli_audit import CLIAuditResult
from mcd.evaluation.code_quality_audit import CodeQualityAuditResult
from mcd.evaluation.production_readiness import ProductionReadinessReport
from mcd.evaluation.kpi_schema import build_kpi_registry
from mcd.evaluation.evaluation_runner import EvaluationReport


def build_markdown_report(
    repo_audit: RepositoryAuditResult,
    arch_audit: ArchitectureAuditResult,
    test_audit: TestAuditResult,
    cli_audit: CLIAuditResult,
    code_audit: CodeQualityAuditResult,
    readiness: ProductionReadinessReport,
    eval_report: EvaluationReport | None = None,
) -> str:
    """Build a comprehensive Markdown industrial audit report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    lines += [
        "# Repository Industrial Audit Report",
        "",
        f"> Generated: {now}",
        f"> Project: sonaiso/Salehan19-6-67 — Epistemic Reasoning & Grounding Layer",
        "",
    ]

    # 1. Executive Summary
    lines += [
        "## 1. Executive Summary",
        "",
        f"| Dimension | Status |",
        f"|-----------|--------|",
        f"| Repository Structure | {repo_audit.status.upper()} |",
        f"| Architecture Score | {arch_audit.overall_score:.2f} ({arch_audit.maturity_label()}) |",
        f"| Tests Detected | {test_audit.total_tests_detected} ({test_audit.estimated_coverage_quality}) |",
        f"| Production Maturity | {readiness.maturity_level} (avg score: {readiness.average_score}/5) |",
        f"| Code Quality | {code_audit.quality_score:.2f}/1.00 |",
        "",
        f"**Maturity Level: {readiness.maturity_level.replace('_', ' ').title()}**",
        "",
        "This project implements an Epistemic Reasoning and Grounding Layer above LLMs. "
        "It is **not** a replacement for GPT-5.5 but a structured control layer for: "
        "prompt classification, evidence grounding, certainty discipline, and shari/epistemic separation.",
        "",
    ]

    # 2. Implemented Layers
    lines += [
        "## 2. Currently Implemented Layers",
        "",
        "| Layer | Package | Status |",
        "|-------|---------|--------|",
        "| MCD — Minimal Cognitive Decoder | `src/mcd/engines/` | ✅ Implemented |",
        "| NERL — Nabhani Epistemic Reasoning | `src/mcd/nabhani/` | ✅ Implemented |",
        "| FPCL — Fractal Prompt Classification | `src/mcd/classification/` | ✅ Implemented |",
        "| GLCFL — Grounded Lexical Cognitive Frame | `src/mcd/grounding/` | ✅ Implemented |",
        "| EIRL — Evaluation & Industrial Readiness | `src/mcd/evaluation/` | ✅ This PR |",
        "",
    ]

    # 3. Test Status
    lines += [
        "## 3. Test Status",
        "",
        f"- **Total tests detected:** {test_audit.total_tests_detected}",
        f"- **Coverage quality:** {test_audit.estimated_coverage_quality}",
        "",
        "### Tests by Layer",
        "",
        "| Layer | Test Count |",
        "|-------|-----------|",
    ]
    for layer, count in test_audit.tests_by_layer.items():
        status = "✅" if count > 0 else "⚠️"
        lines.append(f"| {layer} | {status} {count} |")
    lines.append("")

    if test_audit.findings:
        lines += ["### Findings", ""]
        for f in test_audit.findings:
            lines.append(f"- {f}")
        lines.append("")

    # 4. Architecture Readiness
    lines += [
        "## 4. Architecture Readiness",
        "",
        f"| Dimension | Score |",
        f"|-----------|-------|",
        f"| Layer Separation | {arch_audit.layer_separation_score:.2f} |",
        f"| Modularity | {arch_audit.modularity_score:.2f} |",
        f"| Dependency Risk | {arch_audit.dependency_risk_score:.2f} |",
        f"| Deterministic Core | {arch_audit.deterministic_core_score:.2f} |",
        f"| Integration | {arch_audit.integration_score:.2f} |",
        f"| **Overall** | **{arch_audit.overall_score:.2f}** |",
        "",
        f"**Label:** {arch_audit.maturity_label()}",
        "",
    ]

    # 5. Production Readiness Scorecard
    lines += [
        "## 5. Production Readiness Scorecard",
        "",
        "Scale: 1=concept, 2=research_prototype, 3=working_prototype, 4=pilot_ready, 5=production_ready",
        "",
        "| Dimension | Score | Rationale |",
        "|-----------|-------|-----------|",
    ]
    for dim in readiness.dimensions:
        lines.append(f"| {dim.name} | {dim.score}/5 | {dim.rationale[:80]}... |")
    lines += [
        "",
        f"**Average Score:** {readiness.average_score}/5",
        f"**Maturity Level:** {readiness.maturity_level.replace('_', ' ').title()}",
        "",
    ]

    # 6. KPI Table
    kpis = build_kpi_registry()
    lines += [
        "## 6. KPI Dashboard",
        "",
        "| ID | Name | Category | Target | Current | Status |",
        "|----|------|----------|--------|---------|--------|",
    ]
    for kpi in kpis:
        current = str(kpi.current_value) if kpi.current_value is not None else "—"
        status_icon = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(kpi.status, "⚪")
        lines.append(f"| {kpi.kpi_id} | {kpi.name} | {kpi.category} | {kpi.target_value} | {current} | {status_icon} {kpi.status} |")
    lines.append("")

    # 7. GPT-5.5 Simulation Benchmark Design
    lines += [
        "## 7. GPT-5.5 Simulation Benchmark Design",
        "",
        "This project is **not** competing with GPT-5.5 in language generation quality.",
        "The comparison measures whether this project adds a **controllable epistemic layer** above LLMs.",
        "",
        "| Dimension | GPT-5.5 | MCD/NERL/FPCL |",
        "|-----------|---------|----------------|",
        "| Prompt Understanding Structure | Implicit | Explicit (PromptFrame JSON) |",
        "| Evidence Discipline | Variable | Enforced (evidence_needs) |",
        "| Certainty Discipline | Variable | Enforced (certainty_policy) |",
        "| Domain Separation | Implicit | Explicit (judgment_types) |",
        "| Arabic Epistemic Semantics | General | Nabhani-grounded |",
        "| Structured Output | Possible | Always JSON |",
        "| Hallucination Resistance | Model-dependent | Deterministic suspension |",
        "| Developer Controllability | API parameters | Full rule control |",
        "| Latency | API latency | Local, fast |",
        "",
    ]

    # 8. Benchmark Results (if available)
    if eval_report:
        lines += [
            "## 8. Benchmark Evaluation Results",
            "",
            f"- **Examples evaluated:** {eval_report.total_examples}",
            f"- **Passed (score ≥ 0.5):** {eval_report.passed}",
            f"- **Failed:** {eval_report.failed}",
            f"- **Average score:** {eval_report.average_score:.3f}",
            "",
        ]
        if eval_report.failures:
            lines += ["### Failures", ""]
            for f in eval_report.failures[:10]:
                lines.append(f"- {f}")
            lines.append("")

    # 9. Current Gaps
    lines += [
        "## 9. Current Gaps",
        "",
        "| Gap | Impact |",
        "|-----|--------|",
        "| No REST API | Cannot integrate with external systems |",
        "| No observability/logging | Cannot monitor production behavior |",
        "| Small evaluation dataset | Cannot measure accuracy at scale |",
        "| No LLM output guardrails | Safety risk in production |",
        "| No latency benchmarks | Unknown performance profile |",
        "",
    ]

    # 10. Top Risks
    lines += [
        "## 10. Top Risks",
        "",
    ]
    for blocker in readiness.top_blockers:
        lines.append(f"- {blocker}")
    lines.append("")

    # 11. Next Steps
    lines += [
        "## 11. Recommended Next Steps",
        "",
        "### 30-Day Plan",
        "",
    ]
    for action in readiness.next_30_days_actions:
        lines.append(f"- {action}")

    lines += [
        "",
        "### 90-Day Plan",
        "",
    ]
    for action in readiness.next_90_days_actions:
        lines.append(f"- {action}")

    lines += [
        "",
        "---",
        "",
        "## Conclusion",
        "",
        "The project demonstrates a **working prototype** of an Epistemic Reasoning and Grounding Layer. "
        "It is **not production-ready** yet. Key missing components before pilot deployment: "
        "REST API, observability, calibrated evaluation dataset, and LLM output guardrails. "
        "The architecture is sound and the deterministic classification layers are well-tested.",
        "",
    ]

    return "\n".join(lines)
