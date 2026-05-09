"""Industrial Report — Markdown report generator."""
from __future__ import annotations

from mcd.industrial.industrial_test_runner import IndustrialTestRunner, IndustrialResult
from mcd.industrial.latency_benchmark import LatencyBenchmark, LatencyBenchmarkResult
from mcd.industrial.pilot_readiness import PilotReadinessGate, PilotReadinessResult
from mcd.industrial.failure_injection import FailureInjector
from mcd.industrial.industrial_test_case import get_default_test_cases


def generate_industrial_report() -> str:
    """Generate full Markdown industrial testing report."""
    cases = get_default_test_cases()
    runner = IndustrialTestRunner()
    results = runner.run_all(cases)
    summary = runner.summary(results)

    bench = LatencyBenchmark()
    bench_result = bench.run(cases[:10])

    fi = FailureInjector()
    fi_results = fi.run_all()

    gate = PilotReadinessGate()
    readiness = gate.evaluate_from_runner()

    lines: list[str] = []

    # 1. Executive Summary
    lines += [
        "# Industrial Testing Report — Phase 5",
        "",
        "## 1. Executive Summary",
        "",
        f"- **Total industrial test cases:** {summary['total']}",
        f"- **Passed:** {summary['passed']}",
        f"- **Failed:** {summary['failed']}",
        f"- **Pass rate:** {summary['pass_rate']:.2%}",
        f"- **False certainty rate:** {summary['false_certainty_rate']:.2%}",
        f"- **Source required detection:** {summary['source_required_detection']:.2%}",
        f"- **Injection detection:** {summary['injection_detection']:.2%}",
        f"- **Ready for pilot:** {'✅ YES' if readiness.ready_for_pilot else '❌ NO'}",
        "",
    ]

    # 2. Current Layer Stack
    lines += [
        "## 2. Current Layer Stack",
        "",
        "| Layer | Module | Status |",
        "|-------|--------|--------|",
        "| FPCL  | `mcd.classification.fractal_prompt_classifier` | ✅ Active |",
        "| NERL  | `mcd.nabhani.nabhani_decoder` | ✅ Active |",
        "| EIRL  | `mcd.evaluation.evaluation_runner` | ✅ Active |",
        "| MCD   | `mcd.engines.decoder` | ✅ Active |",
        "| Industrial | `mcd.industrial` | ✅ Phase 5 |",
        "",
    ]

    # 3. API Prior Knowledge Contract
    lines += [
        "## 3. API Prior Knowledge Contract",
        "",
        "Defined in `mcd.industrial.api_contract`:",
        "",
        "- **SourceQuery**: query_id, text, requested_source_types, domain_hint, evidence_need, max_results, timeout_ms",
        "- **SourceDocument**: source_id, title, content, source_type, authority_level, freshness, retrieved_at, metadata",
        "- **SourceAPIResponse**: query_id, status, documents, latency_ms, error_message, warnings",
        "",
        "Authority levels: `official > high > medium > low`",
        "Freshness levels: `current > acceptable > stale > unknown`",
        "API statuses: `ok | empty | timeout | error | unauthorized`",
        "",
    ]

    # 4. Source API Scenarios
    lines += [
        "## 4. Source API Scenarios",
        "",
        "| Scenario | Expected System Behavior |",
        "|----------|--------------------------|",
        "| ok_with_relevant_docs | answer_with_evidence |",
        "| ok_with_irrelevant_docs | lower_certainty |",
        "| empty | suspend / request_source |",
        "| timeout | suspend |",
        "| error | suspend |",
        "| conflicting_docs | flag_conflict |",
        "| stale_docs | lower_certainty |",
        "| low_authority_docs | lower_certainty |",
        "| injection_contaminated_doc | detect_injection |",
        "| missing_source | request_source |",
        "",
    ]

    # 5. Industrial Test Results
    lines += [
        "## 5. Industrial Test Results",
        "",
        "| Case ID | Behavior | Source Status | Certainty | Evidence | Passed |",
        "|---------|----------|---------------|-----------|----------|--------|",
    ]
    for r, case in zip(results, cases):
        lines.append(
            f"| {r.case_id} | {case.expected_behavior} | {r.source_status} | {r.certainty_policy} "
            f"| {r.evidence_status} | {'✅' if r.passed else '❌'} |"
        )
    lines.append("")

    # 6. Latency Results
    lines += [
        "## 6. Latency Results",
        "",
        f"- **Total cases benchmarked:** {bench_result.total_cases}",
        f"- **Avg latency:** {bench_result.avg_latency_ms:.1f} ms",
        f"- **P50 latency:** {bench_result.p50_latency_ms:.1f} ms",
        f"- **P95 latency:** {bench_result.p95_latency_ms:.1f} ms",
        f"- **Max latency:** {bench_result.max_latency_ms:.1f} ms",
        "",
        "> Note: Component-level breakdown not yet instrumented.",
        "",
    ]

    # 7. Failure Injection Results
    lines += [
        "## 7. Failure Injection Results",
        "",
        "| Scenario | Passed | Certainty Lowered | Suspended | Has Warnings |",
        "|----------|--------|-------------------|-----------|--------------|",
    ]
    for fr in fi_results:
        lines.append(
            f"| {fr.scenario} | {'✅' if fr.passed else '❌'} "
            f"| {'✅' if fr.certainty_lowered else '❌'} "
            f"| {'✅' if fr.suspended else '❌'} "
            f"| {'✅' if fr.has_warnings else '❌'} |"
        )
    lines.append("")

    # 8. False Certainty Analysis
    lines += [
        "## 8. False Certainty Analysis",
        "",
        f"- False certainty rate: **{summary['false_certainty_rate']:.2%}**",
        f"- Threshold: ≤ 5%",
        f"- Status: {'✅ Within threshold' if summary['false_certainty_rate'] <= 0.05 else '❌ Exceeds threshold'}",
        "",
    ]

    # 9. Source Grounding Analysis
    lines += [
        "## 9. Source Grounding Analysis",
        "",
        f"- Source required detection: **{summary['source_required_detection']:.2%}**",
        f"- Injection detection: **{summary['injection_detection']:.2%}**",
        "",
    ]

    # 10. Pilot Readiness Gate
    lines += [
        "## 10. Pilot Readiness Gate",
        "",
        f"**Ready for Pilot:** {'✅ YES' if readiness.ready_for_pilot else '❌ NO'}",
        f"**Score:** {readiness.score:.2%}",
        "",
        "### Passed Criteria",
    ]
    for c in readiness.passed_criteria:
        lines.append(f"- ✅ {c}")
    lines += ["", "### Failed Criteria"]
    for c in readiness.failed_criteria:
        lines.append(f"- ❌ {c}")
    lines.append("")

    # 11. Blockers Before Production
    lines += [
        "## 11. Blockers Before Production",
        "",
    ]
    if readiness.blockers:
        for b in readiness.blockers:
            lines.append(f"- 🚫 {b}")
    else:
        lines.append("- No critical blockers identified.")
    lines.append("")

    # 12. Recommended Next Steps
    lines += [
        "## 12. Recommended Next Steps",
        "",
    ]
    if readiness.next_actions:
        for a in readiness.next_actions:
            lines.append(f"1. {a}")
    else:
        lines.append("1. Proceed to pilot deployment.")
    lines.append("")

    return "\n".join(lines)
