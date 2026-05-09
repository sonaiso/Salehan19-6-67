"""CLI entry point for Minimal Cognitive Decoder."""
from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal Cognitive Decoder — فك التشفير المعرفي")
    subparsers = parser.add_subparsers(dest="command")

    decode_parser = subparsers.add_parser("decode", help="Decode Arabic text")
    decode_parser.add_argument("text", help="Arabic text to decode")
    decode_parser.add_argument("--mode", choices=["knower", "learner"], default="knower")
    decode_parser.add_argument("--output", choices=["text", "json"], default="text")

    nabhani_parser = subparsers.add_parser("nabhani", help="Nabhani epistemic reasoning (NERL)")
    nabhani_parser.add_argument("text", help="Arabic text to analyse epistemically")
    nabhani_parser.add_argument("--output", choices=["text", "json"], default="text")

    classify_parser = subparsers.add_parser("classify", help="Fractal Prompt Classification (FPCL)")
    classify_parser.add_argument("text", help="Arabic prompt to classify")
    classify_parser.add_argument("--output", choices=["text", "json"], default="json")
    classify_parser.add_argument("--debug", action="store_true", default=False)

    ground_parser = subparsers.add_parser("ground", help="Grounded Lexical Cognitive Frame (GLCFL)")
    ground_parser.add_argument("text", help="Arabic text to ground")
    ground_parser.add_argument("--output", choices=["text", "json"], default="json")
    ground_parser.add_argument("--debug", action="store_true", default=False)

    eval_parser = subparsers.add_parser("evaluate-project", help="Run full EIRL project audit")
    eval_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

    bench_parser = subparsers.add_parser("benchmark-simulation", help="Run benchmark evaluation on 10 Arabic examples")
    bench_parser.add_argument("--output", choices=["markdown", "json"], default="json")
    bench_parser.add_argument("--profile", default=None, help="Benchmark profile name (optional)")

    readiness_parser = subparsers.add_parser("readiness-score", help="Print production readiness scorecard")
    readiness_parser.add_argument("--output", choices=["markdown", "json"], default="json")

    validate_parser = subparsers.add_parser("validate-dataset", help="Validate the evaluation dataset")
    validate_parser.add_argument("path", nargs="?", default=None, help="Path to JSONL file (optional)")
    validate_parser.add_argument("--output", choices=["json", "text", "markdown"], default="text")

    gen_parser = subparsers.add_parser("generate-dataset", help="Generate dynamic dataset from templates")
    gen_parser.add_argument("--profile", default="standard", help="Profile name")
    gen_parser.add_argument("--count", type=int, default=100, help="Number of examples to generate")
    gen_parser.add_argument("--output-file", default=None, help="Output file path")
    gen_parser.add_argument("--output", choices=["json", "text", "markdown"], default="text")

    coverage_parser = subparsers.add_parser("dataset-coverage", help="Compute dataset coverage matrix")
    coverage_parser.add_argument("path", nargs="?", default=None, help="Path to JSONL file (optional)")
    coverage_parser.add_argument("--output", choices=["json", "text", "markdown"], default="text")

    calibrate_parser = subparsers.add_parser("calibrate-certainty", help="Calibrate certainty on dataset profile")
    calibrate_parser.add_argument("--profile", default="quick", help="Profile name")
    calibrate_parser.add_argument("--output", choices=["json", "text"], default="text")

    report_parser = subparsers.add_parser("dataset-report", help="Generate dataset Markdown report")
    report_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

    # industrial-test
    ind_test_parser = subparsers.add_parser("industrial-test", help="Run industrial test suite")
    ind_test_parser.add_argument("--profile", choices=["quick", "full"], default="quick")
    ind_test_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

    # source-api-smoke
    smoke_parser = subparsers.add_parser("source-api-smoke", help="Smoke test source API scenarios")
    smoke_parser.add_argument("--scenario", default="ok_with_relevant_docs")
    smoke_parser.add_argument("--output", choices=["markdown", "json"], default="json")

    # pilot-readiness
    pilot_parser = subparsers.add_parser("pilot-readiness", help="Evaluate pilot readiness gate")
    pilot_parser.add_argument("--output", choices=["markdown", "json"], default="json")

    # latency-benchmark
    latency_parser = subparsers.add_parser("latency-benchmark", help="Run latency benchmark")
    latency_parser.add_argument("--cases", type=int, default=20)
    latency_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()

    if args.command == "classify":
        from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
        from mcd.classification.serializers import prompt_frame_to_json

        fpc = FractalPromptClassifier()
        frame = fpc.classify(args.text, include_debug=args.debug)

        if args.output == "json":
            print(prompt_frame_to_json(frame))
        else:
            print(f"المدخل:         {frame.raw_text}")
            print(f"الهدف:          {frame.intent}")
            print(f"الجذر المعرفي:  {_top_labels(frame.root_domain)}")
            print(f"نوع المفهوم:    {_top_labels(frame.concept_types)}")
            print(f"صنف المعرفة:    {_top_labels(frame.knowledge_categories)}")
            print(f"نوع الحكم:      {_top_labels(frame.judgment_types)}")
            print(f"نوع الدليل:     {_top_labels(frame.evidence_needs)}")
            print(f"سياسة اليقين:   {frame.certainty_policy}")
            print(f"محرك التوجيه:   {frame.routing_engine}")
            print(f"المحركات الفرعية: {', '.join(frame.sub_engines)}")
            if frame.warnings:
                print(f"تحذيرات:       {' | '.join(frame.warnings)}")
    elif args.command == "nabhani":
        from mcd.nabhani.nabhani_decoder import NabhaniDecoder

        decoder = NabhaniDecoder()
        result = decoder.decode(args.text)

        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"المدخل:          {result['input']}")
            print(f"نوع الحكم:       {result['domain']['judgment_type']}")
            print(f"حالة النطاق:     {result['domain']['status']}")
            print(f"الحكم العقلي:    {result['rational_judgment']['status']}")
            print(f"المطابقة:        {result['correspondence']['match_score']:.3f} ({result['correspondence']['match_type']})")
            print(f"اليقين:          {result['certainty']['score']:.3f} ({result['certainty']['level']})")
            print(f"الحالة المعرفية: {result['epistemic_status']}")
            print(f"الإجابة:         {result['final_answer']}")
    elif args.command == "decode":
        from mcd.engines.decoder import MinimalCognitiveDecoder
        from mcd.knowledge.prior_store import PriorKnowledgeStore
        from mcd.knowledge.seed_data import load_seed_data

        store = PriorKnowledgeStore()
        load_seed_data(store)
        decoder = MinimalCognitiveDecoder(store=store)
        result = decoder.decode(args.text, mode=args.mode)

        if args.output == "json":
            print(json.dumps({
                "input": result.input,
                "normalized": result.normalized,
                "claims": result.claims,
                "certainty": result.certainty,
                "learning_actions": result.learning_actions,
                "answer": result.answer,
            }, ensure_ascii=False, indent=2))
        else:
            print(f"Input:      {result.input}")
            print(f"Normalized: {result.normalized}")
            print(f"Answer:     {result.answer}")
            print(f"Claims:     {len(result.claims)}")
            print(f"Relations:  {len(result.relations)}")
            print(f"Certainty:  {result.certainty['score']:.3f} ({result.certainty['level']})")
    elif args.command == "ground":
        from mcd.grounding.grounded_reasoning_builder import GroundedReasoningBuilder
        from mcd.grounding.serializers import grounded_frame_to_json
        from mcd.grounding.report import generate_report

        builder = GroundedReasoningBuilder()
        frame = builder.build(args.text, include_debug=args.debug)

        if args.output == "json":
            print(grounded_frame_to_json(frame))
        else:
            print(generate_report(frame))
    elif args.command == "evaluate-project":
        from mcd.evaluation.repository_audit import RepositoryAudit
        from mcd.evaluation.architecture_audit import ArchitectureAudit
        from mcd.evaluation.test_audit import TestAudit
        from mcd.evaluation.cli_audit import CLIAudit
        from mcd.evaluation.code_quality_audit import CodeQualityAudit
        from mcd.evaluation.production_readiness import ProductionReadinessReport
        from mcd.evaluation.report_builder import build_markdown_report
        from mcd.evaluation.serializers import (
            repo_audit_to_json, arch_audit_to_json, test_audit_to_json,
            cli_audit_to_json, code_quality_to_json, readiness_to_json,
        )

        repo = RepositoryAudit().run()
        arch = ArchitectureAudit().run()
        test = TestAudit().run()
        cli = CLIAudit().run()
        code = CodeQualityAudit().run()
        readiness = ProductionReadinessReport.build_default()

        if args.output == "markdown":
            print(build_markdown_report(repo, arch, test, cli, code, readiness))
        else:
            import json as _json
            print(_json.dumps({
                "repository": _json.loads(repo_audit_to_json(repo)),
                "architecture": _json.loads(arch_audit_to_json(arch)),
                "tests": _json.loads(test_audit_to_json(test)),
                "cli": _json.loads(cli_audit_to_json(cli)),
                "code_quality": _json.loads(code_quality_to_json(code)),
                "readiness": _json.loads(readiness_to_json(readiness)),
            }, ensure_ascii=False, indent=2))
    elif args.command == "benchmark-simulation":
        from mcd.evaluation.evaluation_runner import EvaluationRunner
        from mcd.evaluation.serializers import eval_report_to_json

        runner = EvaluationRunner()
        report = runner.run()

        if args.output == "json":
            print(eval_report_to_json(report))
        else:
            print(f"# Benchmark Simulation Results\n")
            print(f"- Examples: {report.total_examples}")
            print(f"- Passed:   {report.passed}")
            print(f"- Failed:   {report.failed}")
            print(f"- Average:  {report.average_score:.3f}")
            if report.failures:
                print(f"\n## Failures\n")
                for f in report.failures:
                    print(f"- {f}")
    elif args.command == "readiness-score":
        from mcd.evaluation.production_readiness import ProductionReadinessReport
        from mcd.evaluation.serializers import readiness_to_json

        readiness = ProductionReadinessReport.build_default()

        if args.output == "json":
            print(readiness_to_json(readiness))
        else:
            print(f"# Production Readiness Scorecard\n")
            print(f"**Maturity Level:** {readiness.maturity_level}")
            print(f"**Average Score:** {readiness.average_score}/5\n")
            print(f"| Dimension | Score |")
            print(f"|-----------|-------|")
            for dim in readiness.dimensions:
                print(f"| {dim.name} | {dim.score}/5 |")
    elif args.command == "validate-dataset":
        from pathlib import Path
        from mcd.evaluation.dataset_loader import load_all, load_jsonl
        from mcd.evaluation.dataset_validator import validate_dataset

        if getattr(args, "path", None):
            examples = load_jsonl(Path(args.path))
        else:
            examples = load_all()
        report = validate_dataset(examples)

        if args.output == "json":
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Dataset Validation Report")
            print(f"  Total:   {report.total}")
            print(f"  Valid:   {report.valid}")
            print(f"  Errors:  {report.error_count}")
            print(f"  Status:  {'✅' if report.is_valid else '❌'}")
            if report.errors:
                print(f"\nErrors:")
                for e in report.errors[:10]:
                    print(f"  - [{e.example_id}] {e.field}: {e.message}")
    elif args.command == "generate-dataset":
        from mcd.evaluation.dynamic_dataset_generator import DynamicDatasetGenerator

        gen = DynamicDatasetGenerator()
        examples = gen.generate_profile(args.profile, args.count)

        if args.output == "json":
            print(json.dumps([ex.to_dict() for ex in examples], ensure_ascii=False, indent=2))
        else:
            print(f"Generated {len(examples)} examples (profile={args.profile})")
            for ex in examples[:5]:
                print(f"  [{ex.example_id}] {ex.input_text[:60]}")
    elif args.command == "dataset-coverage":
        from pathlib import Path
        from mcd.evaluation.dataset_loader import load_all, load_jsonl
        from mcd.evaluation.coverage_matrix import CoverageMatrix

        if getattr(args, "path", None):
            examples = load_jsonl(Path(args.path))
        else:
            examples = load_all()
        matrix = CoverageMatrix(examples)
        cov_report = matrix.compute()

        if args.output == "json":
            print(json.dumps(cov_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Coverage Report ({cov_report.total_examples} examples)")
            print(f"  Coverage Score: {cov_report.coverage_score:.2%}")
            for dim in cov_report.dimension_coverages:
                print(f"  {dim.dimension}: {dim.coverage_ratio:.2%}")
    elif args.command == "calibrate-certainty":
        from mcd.evaluation.benchmark_profiles import BenchmarkProfileManager
        from mcd.evaluation.dataset_validator import validate_dataset

        mgr = BenchmarkProfileManager()
        examples = mgr.get_examples(args.profile)
        cal_report = validate_dataset(examples)

        if args.output == "json":
            print(json.dumps({
                "profile": args.profile,
                "total": cal_report.total,
                "valid": cal_report.valid,
                "is_valid": cal_report.is_valid,
            }, ensure_ascii=False, indent=2))
        else:
            print(f"Calibration Report (profile={args.profile})")
            print(f"  Total:  {cal_report.total}")
            print(f"  Valid:  {cal_report.valid}")
            print(f"  Status: {'✅' if cal_report.is_valid else '❌'}")
    elif args.command == "dataset-report":
        from mcd.evaluation.dataset_loader import load_all
        from mcd.evaluation.dataset_report import DatasetReport

        examples = load_all()
        rpt = DatasetReport(examples=examples)

        if args.output == "json":
            from mcd.evaluation.coverage_matrix import CoverageMatrix
            coverage = CoverageMatrix(examples).compute()
            print(json.dumps(coverage.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(rpt.generate_markdown())
    elif args.command == "industrial-test":
        from mcd.industrial.industrial_test_runner import IndustrialTestRunner
        from mcd.industrial.industrial_test_case import get_default_test_cases
        from mcd.industrial.industrial_report import generate_industrial_report_from_results
        from mcd.industrial.serializers import industrial_result_to_dict, to_json

        cases = get_default_test_cases()
        if args.profile == "quick":
            cases = cases[:10]
        runner = IndustrialTestRunner()
        results = runner.run_all(cases)
        summary = runner.summary(results)

        if args.output == "json":
            print(to_json({"summary": summary, "results": [industrial_result_to_dict(r) for r in results]}))
        else:
            print(generate_industrial_report_from_results(
                profile=args.profile,
                cases=cases,
                results=results,
                summary=summary,
            ))
    elif args.command == "source-api-smoke":
        from mcd.industrial.mock_source_api import MockSourceAPI
        from mcd.industrial.api_contract import SourceQuery
        from mcd.industrial.serializers import source_response_to_dict, to_json

        api = MockSourceAPI(scenario=args.scenario)
        q = SourceQuery(query_id="smoke-001", text="اختبار سريع للمصدر", timeout_ms=3000)
        response = api.search(q)

        if args.output == "json":
            print(to_json(source_response_to_dict(response)))
        else:
            print(f"Scenario: {args.scenario}")
            print(f"Status: {response.status}")
            print(f"Documents: {len(response.documents)}")
            print(f"Latency: {response.latency_ms}ms")
    elif args.command == "pilot-readiness":
        from mcd.industrial.pilot_readiness import PilotReadinessGate
        from mcd.industrial.serializers import pilot_readiness_to_dict, to_json

        gate = PilotReadinessGate()
        result = gate.evaluate_from_runner()

        if args.output == "json":
            print(to_json(pilot_readiness_to_dict(result)))
        else:
            print(f"# Pilot Readiness Gate\n")
            print(f"**Ready for Pilot:** {'✅ YES' if result.ready_for_pilot else '❌ NO'}")
            if result.conditional:
                print(f"**Status:** Conditional")
            print(f"**Score:** {result.score:.2%}")
            if result.blockers:
                print(f"\n## Blockers")
                for b in result.blockers:
                    print(f"- {b}")
    elif args.command == "latency-benchmark":
        from mcd.industrial.latency_benchmark import LatencyBenchmark
        from mcd.industrial.industrial_test_case import get_default_test_cases
        from mcd.industrial.serializers import latency_result_to_dict, to_json

        cases = get_default_test_cases()[:args.cases]
        bench = LatencyBenchmark()
        result = bench.run(cases)

        if args.output == "json":
            print(to_json(latency_result_to_dict(result)))
        else:
            print(f"# Latency Benchmark Results\n")
            print(f"- Total cases: {result.total_cases}")
            print(f"- Avg latency: {result.avg_latency_ms:.1f}ms")
            print(f"- P50 latency: {result.p50_latency_ms:.1f}ms")
            print(f"- P95 latency: {result.p95_latency_ms:.1f}ms")
            print(f"- Max latency: {result.max_latency_ms:.1f}ms")
    else:
        parser.print_help()


def _top_labels(d: dict, n: int = 3) -> str:
    """Format top-n labels from a score dict."""
    if not d:
        return "-"
    top = sorted(d.items(), key=lambda x: x[1], reverse=True)[:n]
    return ", ".join(f"{k}({v:.2f})" for k, v in top)


if __name__ == "__main__":
    main()
