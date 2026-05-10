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

    # pre-api-qualification
    paq_parser = subparsers.add_parser(
        "pre-api-qualification",
        help="Phase 5.2: Pre-API Qualification Gate — verify all non-API dimensions ≥ 4.5",
    )
    paq_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")
    paq_parser.add_argument(
        "--tests-pass",
        dest="tests_pass",
        choices=["true", "false"],
        default=None,
        help="Set to 'true' if CI confirms all tests pass (raises test_score above 4.3)",
    )
    paq_parser.add_argument(
        "--readiness-report-exists",
        dest="readiness_report_exists",
        choices=["true", "false"],
        default=None,
        help="Set to 'true' if a pilot readiness report already exists",
    )
    paq_parser.add_argument(
        "--latency-target-ms",
        dest="latency_target_ms",
        type=float,
        default=None,
        help="Documented p95 latency target in milliseconds (raises latency_score above 4.4)",
    )

    # curriculum-validate
    cur_val_parser = subparsers.add_parser("curriculum-validate", help="Validate a curriculum JSONL file")
    cur_val_parser.add_argument("path", nargs="?", default=None, help="Path to JSONL file (optional)")
    cur_val_parser.add_argument("--output", choices=["json", "text", "markdown"], default="text")

    # curriculum-generate
    cur_gen_parser = subparsers.add_parser("curriculum-generate", help="Generate curriculum units")
    cur_gen_parser.add_argument("--level", type=int, default=1)
    cur_gen_parser.add_argument("--count", type=int, default=50)
    cur_gen_parser.add_argument("--seed", type=int, default=42)
    cur_gen_parser.add_argument("--output", choices=["json", "jsonl", "text"], default="jsonl")

    # curriculum-evaluate
    cur_eval_parser = subparsers.add_parser("curriculum-evaluate", help="Evaluate curriculum profile")
    cur_eval_parser.add_argument("--profile", default="full_curriculum")
    cur_eval_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")

    # curriculum-report
    cur_rpt_parser = subparsers.add_parser("curriculum-report", help="Generate curriculum markdown report")
    cur_rpt_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

    # curriculum-export-industrial
    cur_exp_parser = subparsers.add_parser("curriculum-export-industrial", help="Export industrial cases from curriculum")
    cur_exp_parser.add_argument("--profile", default="industrial_curriculum")
    cur_exp_parser.add_argument("--output", default=None, help="Output file path (JSONL). If not given, prints to stdout.")

    # curriculum-contract-check
    cur_cc_parser = subparsers.add_parser("curriculum-contract-check", help="Run mathematical contract checks on curriculum graph")
    cur_cc_parser.add_argument("--profile", default="full_curriculum")
    cur_cc_parser.add_argument("--output", choices=["json", "text"], default="text")

    # curriculum-qualification
    cur_qual_parser = subparsers.add_parser("curriculum-qualification", help="Compute curriculum qualification metrics")
    cur_qual_parser.add_argument("--profile", default="full_curriculum_extended")
    cur_qual_parser.add_argument("--output", choices=["json", "text", "markdown"], default="markdown")

    # curriculum-quality-lock
    cur_ql_parser = subparsers.add_parser(
        "curriculum-quality-lock",
        help="Phase 5.3.2: Run quality lock — verifies contract is governing, not just structural",
    )
    cur_ql_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")

    # curriculum-mutation-test
    cur_mut_parser = subparsers.add_parser(
        "curriculum-mutation-test",
        help="Phase 5.3.2: Run mutation tests — verifies validators catch corrupted examples",
    )
    cur_mut_parser.add_argument("--output", choices=["json", "text"], default="json")

    # api — Phase 6 minimal REST API server
    api_parser = subparsers.add_parser(
        "api",
        help="Phase 6: Start the MCD minimal REST API server (requires uvicorn)",
    )
    api_parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    api_parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    api_parser.add_argument("--reload", action="store_true", default=False, help="Enable auto-reload")

    # api-schema-check — Phase 6.1 schema stability checker
    api_schema_parser = subparsers.add_parser(
        "api-schema-check",
        help="Phase 6.1: Run API schema stability checks (no Enum/dataclass leakage, JSON roundtrip)",
    )
    api_schema_parser.add_argument("--output", choices=["json", "text"], default="json")

    # ── Phase 7: Cognitive Residual Learning ──────────────────────────────
    # residual-analyze
    res_analyze_parser = subparsers.add_parser(
        "residual-analyze",
        help="Phase 7: Analyze GPT proposals and compute cognitive residuals",
    )
    res_analyze_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with GPT proposals",
    )
    res_analyze_parser.add_argument("--output", choices=["json", "markdown", "text"], default="json")

    # residual-report
    res_report_parser = subparsers.add_parser(
        "residual-report",
        help="Phase 7: Generate residual learning summary report",
    )
    res_report_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with GPT proposals",
    )
    res_report_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")

    # residual-build-dataset
    res_build_parser = subparsers.add_parser(
        "residual-build-dataset",
        help="Phase 7: Build dataset from residuals (adversarial / curriculum / calibration)",
    )
    res_build_parser.add_argument(
        "--target",
        choices=["adversarial", "curriculum", "calibration", "regression"],
        default="adversarial",
    )
    res_build_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with GPT proposals",
    )
    res_build_parser.add_argument(
        "--output",
        default=None,
        help="Output JSONL file path. Defaults to data/residual_learning/generated_<target>.jsonl",
    )

    # residual-calibrate
    res_cal_parser = subparsers.add_parser(
        "residual-calibrate",
        help="Phase 7: Generate calibration recommendations from residuals",
    )
    res_cal_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with GPT proposals",
    )
    res_cal_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")

    # residual-test-specs
    res_specs_parser = subparsers.add_parser(
        "residual-test-specs",
        help="Phase 7: Generate test specs from residuals",
    )
    res_specs_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with GPT proposals",
    )
    res_specs_parser.add_argument(
        "--output",
        default="data/residual_learning/generated_test_specs.jsonl",
        help="Output JSONL file path",
    )

    # ── Phase 7.1: Curriculum Deepening ──────────────────────────────────
    # curriculum-depth-report
    cur_depth_parser = subparsers.add_parser(
        "curriculum-depth-report",
        help="Phase 7.1: Compute depth metrics for the curriculum dataset",
    )
    cur_depth_parser.add_argument("--output", choices=["json", "markdown"], default="markdown")

    # curriculum-coverage
    cur_cov_parser = subparsers.add_parser(
        "curriculum-coverage",
        help="Phase 7.1: Compute coverage matrix across curriculum dimensions",
    )
    cur_cov_parser.add_argument("--output", choices=["json", "markdown"], default="json")

    # curriculum-residual-build
    cur_resb_parser = subparsers.add_parser(
        "curriculum-residual-build",
        help="Phase 7.1: Build Level 11 curriculum from mock GPT proposals",
    )
    cur_resb_parser.add_argument(
        "--input",
        default="data/residual_learning/mock_gpt_proposals_ar.jsonl",
        help="Path to JSONL file with mock GPT proposals",
    )
    cur_resb_parser.add_argument(
        "--output",
        default="data/curriculum/level_11_cognitive_residual_learning_ar.jsonl",
        help="Output JSONL path",
    )

    # ── Phase 7.1.2: Unicode-to-Cognition Traceability ───────────────────
    # trace-text
    trace_text_parser = subparsers.add_parser(
        "trace-text",
        help="Phase 7.1.2: Build full Unicode-to-Cognition trace for input text",
    )
    trace_text_parser.add_argument("--text", required=True, help="Arabic text to trace")
    trace_text_parser.add_argument("--output", choices=["json", "markdown", "text"], default="json")

    # trace-validate
    trace_val_parser = subparsers.add_parser(
        "trace-validate",
        help="Phase 7.1.2: Build trace and run validation report",
    )
    trace_val_parser.add_argument("--text", required=True, help="Arabic text to trace and validate")
    trace_val_parser.add_argument("--output", choices=["json", "markdown", "text"], default="markdown")

    # trace-report
    trace_rpt_parser = subparsers.add_parser(
        "trace-report",
        help="Phase 7.1.2: Generate full traceability report for golden examples",
    )
    trace_rpt_parser.add_argument("--output", choices=["markdown", "json"], default="markdown")

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
    elif args.command == "pre-api-qualification":
        from mcd.industrial.pre_api_qualification import PreAPIQualificationGate, render_markdown
        from mcd.industrial.serializers import to_json

        tests_pass = None
        if args.tests_pass is not None:
            tests_pass = args.tests_pass.lower() == "true"

        readiness_report_exists = None
        if args.readiness_report_exists is not None:
            readiness_report_exists = args.readiness_report_exists.lower() == "true"

        latency_target_ms = args.latency_target_ms

        gate = PreAPIQualificationGate()
        report = gate.evaluate(
            tests_pass=tests_pass,
            readiness_report_exists=readiness_report_exists,
            latency_target_ms=latency_target_ms,
        )

        if args.output == "json":
            print(to_json(report.to_dict()))
        else:
            print(render_markdown(report))
    elif args.command == "curriculum-validate":
        from pathlib import Path as _Path
        from mcd.curriculum.curriculum_dataset import CurriculumDataset, _load_jsonl
        from mcd.curriculum.curriculum_validator import CurriculumValidator

        if getattr(args, "path", None):
            units = _load_jsonl(_Path(args.path))
        else:
            units = CurriculumDataset().load_all()
        report = CurriculumValidator().validate(units)

        if args.output == "json":
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Curriculum Validation Report")
            print(f"  Total:   {report.total_units}")
            print(f"  Valid:   {report.valid_units}")
            print(f"  Invalid: {report.invalid_units}")
            print(f"  Status:  {'✅' if report.status == 'valid' else '❌'} {report.status}")
    elif args.command == "curriculum-generate":
        from mcd.curriculum.curriculum_generator import CurriculumGenerator

        gen = CurriculumGenerator()
        units = gen.generate_level(args.level, args.count, args.seed)

        if args.output == "jsonl":
            from mcd.curriculum.serializers import cognitive_units_to_jsonl
            print(cognitive_units_to_jsonl(units))
        elif args.output == "json":
            print(json.dumps([u.to_dict() for u in units], ensure_ascii=False, indent=2))
        else:
            print(f"Generated {len(units)} units for level {args.level}")
            for u in units[:5]:
                print(f"  [{u.unit_id}] {u.input_text[:60]}")
    elif args.command == "curriculum-evaluate":
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
        from mcd.curriculum.learning_profiles import get_profile
        from mcd.curriculum.report import generate_curriculum_report

        profile = get_profile(args.profile)
        units = CurriculumDataset().load_levels(profile.levels)
        eval_report = CurriculumEvaluator().evaluate(units)

        if args.output == "json":
            print(json.dumps(eval_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(generate_curriculum_report(eval_report=eval_report))
    elif args.command == "curriculum-report":
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.curriculum_validator import CurriculumValidator
        from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
        from mcd.curriculum.report import generate_curriculum_report

        units = CurriculumDataset().load_all()
        val_report = CurriculumValidator().validate(units)
        eval_report = CurriculumEvaluator().evaluate(units)

        if args.output == "json":
            print(json.dumps({
                "validation": val_report.to_dict(),
                "evaluation": eval_report.to_dict(),
            }, ensure_ascii=False, indent=2))
        else:
            print(generate_curriculum_report(eval_report=eval_report, val_report=val_report))
    elif args.command == "curriculum-export-industrial":
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.industrial_bridge import IndustrialBridge
        from mcd.curriculum.learning_profiles import get_profile
        import pathlib as _pathlib

        profile = get_profile(args.profile)
        units = CurriculumDataset().load_levels(profile.levels)
        bridge = IndustrialBridge()
        cases = bridge.convert(units)
        jsonl_str = bridge.export_to_jsonl(cases)

        if args.output:
            out_path = _pathlib.Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(jsonl_str, encoding="utf-8")
            print(f"Exported {len(cases)} industrial cases to {args.output}")
        else:
            print(jsonl_str)
    elif args.command == "curriculum-contract-check":
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.cognitive_graph import CognitiveGraph
        from mcd.curriculum.cognitive_node import CognitiveNode
        from mcd.curriculum.cognitive_edge import CognitiveEdge
        from mcd.curriculum.mathematical_contract import check_mathematical_contract
        from mcd.curriculum.learning_profiles import get_profile
        from mcd.curriculum.vector_space import zero_role_vector, zero_domain_vector

        profile = get_profile(args.profile)
        units = CurriculumDataset().load_levels(profile.levels)

        # Build a compact graph: one node per level with valid vectors
        level_ids = sorted({u.level for u in units})
        nodes = []
        for lvl in level_ids:
            rv = zero_role_vector()
            rv["thing"] = 1.0  # "thing" is a valid ROLE_DIMENSION; "domain" is only a node_type
            dv = zero_domain_vector()
            dv["education"] = 1.0
            nodes.append(CognitiveNode(
                node_id=f"level_{lvl}",
                surface=f"Level {lvl}",
                normalized=f"level_{lvl}",
                node_type="domain",
                role_vector=rv,
                domain_vector=dv,
            ))
        # Build root_vector and domain_summary from node vectors
        rv_sum = zero_role_vector()
        for n in nodes:
            for k, v in n.role_vector.items():
                rv_sum[k] = rv_sum.get(k, 0.0) + v
        total_rv = sum(rv_sum.values())
        root_vector = {k: v / total_rv for k, v in rv_sum.items()} if total_rv > 0 else rv_sum
        dv_sum = zero_domain_vector()
        for n in nodes:
            for k, v in n.domain_vector.items():
                dv_sum[k] = dv_sum.get(k, 0.0) + v
        total_dv = sum(dv_sum.values())
        domain_summary = {k: v / total_dv for k, v in dv_sum.items()} if total_dv > 0 else dv_sum

        edges = [
            CognitiveEdge(
                edge_id=f"e_{i}",
                source=f"level_{level_ids[i]}",
                relation="entails",
                target=f"level_{level_ids[i+1]}",
            )
            for i in range(len(level_ids) - 1)
        ]
        graph = CognitiveGraph(
            graph_id="curriculum-contract-check",
            nodes=nodes,
            edges=edges,
            root_vector=root_vector,
            domain_summary=domain_summary,
        )

        result = check_mathematical_contract(graph)

        if args.output == "json":
            print(json.dumps({
                **result.to_dict(),
                "units_checked": len(units),
                "levels": level_ids,
            }, ensure_ascii=False, indent=2))
        else:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"Mathematical Contract Check — {status}")
            print(f"  Units checked:  {len(units)}")
            print(f"  Levels:         {level_ids}")
            print(f"  Graph nodes:    {len(nodes)}")
            print(f"  Graph edges:    {len(edges)}")
            print(f"  Contract score: {result.score:.4f}")
            if result.violations:
                print(f"  Violations ({len(result.violations)}):")
                for v in result.violations[:10]:
                    print(f"    - {v}")
    elif args.command == "curriculum-qualification":
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.qualification_bridge import (
            compute_qualification_metrics,
            DATASET_THRESHOLD, CALIBRATION_THRESHOLD, INDUSTRIAL_THRESHOLD,
            SOURCE_TRUST_THRESHOLD, GRAPH_CONTRACT_THRESHOLD,
            VECTOR_CONTRACT_THRESHOLD, INVARIANT_THRESHOLD, ADVERSARIAL_THRESHOLD,
        )
        from mcd.curriculum.learning_profiles import get_profile

        profile = get_profile(args.profile)
        units = CurriculumDataset().load_levels(profile.levels)
        metrics = compute_qualification_metrics(units)

        if args.output == "json":
            print(json.dumps(metrics.to_dict(), ensure_ascii=False, indent=2))
        elif args.output == "markdown":
            is_qual = metrics.is_qualified()
            status = "✅ QUALIFIED FOR API PHASE" if is_qual else "❌ NOT YET QUALIFIED"
            print(f"# Curriculum Qualification Report — Phase 5.3.1\n")
            print(f"**Status:** {status}  ")
            print(f"**Profile:** {args.profile}  ")
            print(f"**Recommendation:** {metrics.recommendation}\n")
            print(f"## Dataset Coverage\n")
            print(f"| Metric | Value |")
            print(f"|--------|-------|")
            print(f"| Total examples | {metrics.total_examples} |")
            print(f"| Golden examples | {metrics.golden_examples} |")
            print(f"| Adversarial examples | {metrics.adversarial_examples} |")
            print(f"| Coverage score | {metrics.curriculum_coverage_score:.4f} |")
            print(f"\n## Score Estimates vs Thresholds\n")
            print(f"| Metric | Score | Threshold | Status |")
            print(f"|--------|-------|-----------|--------|")
            rows = [
                ("dataset_score_estimate", metrics.dataset_score_estimate, DATASET_THRESHOLD),
                ("calibration_score_estimate", metrics.calibration_score_estimate, CALIBRATION_THRESHOLD),
                ("industrial_testing_score_estimate", metrics.industrial_testing_score_estimate, INDUSTRIAL_THRESHOLD),
                ("source_trust_score_estimate", metrics.source_trust_score_estimate, SOURCE_TRUST_THRESHOLD),
                ("graph_contract_score", metrics.graph_contract_score, GRAPH_CONTRACT_THRESHOLD),
                ("vector_contract_score", metrics.vector_contract_score, VECTOR_CONTRACT_THRESHOLD),
                ("invariant_pass_rate", metrics.invariant_pass_rate, INVARIANT_THRESHOLD),
                ("adversarial_pass_rate", metrics.adversarial_pass_rate, ADVERSARIAL_THRESHOLD),
            ]
            for name, score, threshold in rows:
                st = "✅" if score >= threshold else "❌"
                print(f"| {name} | {score:.4f} | {threshold} | {st} |")
            print(f"\n## API Gate Decision\n")
            print(f"API implementation: **NOT implemented (Phase 5.3.1)**  ")
            print(f"Next phase: {'Phase 5.4 REST API (after qualification)' if is_qual else 'Phase 5.3.1 hardening continues'}")
        else:
            is_qualified = metrics.is_qualified()
            status = "QUALIFIED" if is_qualified else "NOT QUALIFIED"
            print(f"Curriculum Qualification: {status}")
            print(f"  Total units:          {metrics.total_examples}")
            print(f"  Golden examples:      {metrics.golden_examples}")
            print(f"  Adversarial examples: {metrics.adversarial_examples}")
            print(f"  dataset_score:        {metrics.dataset_score_estimate:.4f} (>={DATASET_THRESHOLD})")
            print(f"  calibration_score:    {metrics.calibration_score_estimate:.4f} (>={CALIBRATION_THRESHOLD})")
            print(f"  industrial_score:     {metrics.industrial_testing_score_estimate:.4f} (>={INDUSTRIAL_THRESHOLD})")
            print(f"  source_trust_score:   {metrics.source_trust_score_estimate:.4f} (>={SOURCE_TRUST_THRESHOLD})")
            print(f"  Recommendation:       {metrics.recommendation}")
    elif args.command == "curriculum-quality-lock":
        from mcd.curriculum.quality_lock import run_quality_lock

        ql_report = run_quality_lock()

        if args.output == "json":
            print(json.dumps(ql_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(ql_report.to_markdown())
    elif args.command == "curriculum-mutation-test":
        from mcd.curriculum.mutation_tests import run_mutation_tests

        mut_report = run_mutation_tests()

        if args.output == "json":
            print(json.dumps(mut_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            status = "✅ PASSED" if mut_report.pass_rate >= 0.95 else "❌ FAILED"
            print(f"Mutation Tests — {status}")
            print(f"  Total:     {mut_report.total}")
            print(f"  Passed:    {mut_report.passed}")
            print(f"  Pass rate: {mut_report.pass_rate:.4f}")
            for r in mut_report.results:
                icon = "✅" if r.passed else "❌"
                print(f"  {icon} {r.mutation_name}: {r.explanation}")
    elif args.command == "api":
        try:
            import uvicorn  # type: ignore[import]
        except ImportError:
            print(
                "ERROR: uvicorn is not installed.\n"
                "Install it with:  pip install uvicorn\n"
                "Then run:         python -m mcd.cli api --host 127.0.0.1 --port 8000",
                file=sys.stderr,
            )
            sys.exit(1)

        from mcd.api.app import build_app

        print(f"Starting MCD API on http://{args.host}:{args.port}")
        print("Phase 6.1 — API Hardening & Pilot Verification (pilot-ready candidate, not production-ready)")
        uvicorn.run(
            build_app(),
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    elif args.command == "api-schema-check":
        from mcd.api.app import build_app
        from mcd.api.schema_stability import run_schema_checks
        from fastapi.testclient import TestClient

        test_client = TestClient(build_app())
        result = run_schema_checks(test_client)

        if args.output == "json":
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"API Schema Stability Check — {status}")
            print(f"  Total checks: {result.total}")
            print(f"  Failed:       {result.failed}")
            if not result.passed:
                for c in result.checks:
                    if not c["passed"]:
                        print(f"  ❌ {c['check']}")
    elif args.command in (
        "residual-analyze", "residual-report",
        "residual-build-dataset", "residual-calibrate", "residual-test-specs",
        "curriculum-depth-report", "curriculum-coverage", "curriculum-residual-build",
    ):
        _handle_residual_command(args)
    elif args.command in ("trace-text", "trace-validate", "trace-report"):
        _handle_trace_command(args)
    else:
        parser.print_help()


def _top_labels(d: dict, n: int = 3) -> str:
    """Format top-n labels from a score dict."""
    if not d:
        return "-"
    top = sorted(d.items(), key=lambda x: x[1], reverse=True)[:n]
    return ", ".join(f"{k}({v:.2f})" for k, v in top)


def _handle_residual_command(args) -> None:  # noqa: ANN001
    """Phase 7 — Cognitive Residual Learning CLI handlers."""
    import json as _json
    from pathlib import Path as _Path
    from mcd.residual_learning.proposal_schema import GPTProposal
    from mcd.residual_learning.engine import CognitiveResidualLearningEngine
    from mcd.residual_learning.residual_report import ResidualReport
    from mcd.residual_learning.residual_calibration import ResidualCalibrationEngine
    from mcd.residual_learning.residual_dataset_builder import ResidualDatasetBuilder
    from mcd.residual_learning.residual_test_generator import ResidualTestGenerator

    def _load_proposals(path: str) -> list[GPTProposal]:
        proposals = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    proposals.append(GPTProposal.from_dict(_json.loads(line)))
        return proposals

    engine = CognitiveResidualLearningEngine()

    if args.command == "residual-analyze":
        proposals = _load_proposals(args.input)
        results = engine.analyze_batch(proposals)

        if args.output == "json":
            out = [r.to_dict() for r in results]
            print(_json.dumps(out, ensure_ascii=False, indent=2))
        elif args.output == "markdown":
            report = engine.generate_report(results)
            print(report.to_markdown())
        else:
            report = engine.generate_report(results)
            print(f"Total proposals: {len(proposals)}")
            print(f"Total residuals: {report.total}")
            print(f"Blocking:        {report.blocking_count}")
            print(f"High:            {report.high_count}")
            print(f"Adversarial:     {report.adversarial_candidates}")
            print(f"GPT as evidence: {'YES ❌' if report.gpt_used_as_evidence else 'No ✅'}")

    elif args.command == "residual-report":
        proposals = _load_proposals(args.input)
        results = engine.analyze_batch(proposals)
        report = engine.generate_report(results)

        if args.output == "json":
            print(_json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(report.to_markdown())

    elif args.command == "residual-build-dataset":
        proposals = _load_proposals(args.input)
        results = engine.analyze_batch(proposals)
        builder = ResidualDatasetBuilder()
        target = args.target
        out_path = args.output or f"data/residual_learning/generated_{target}.jsonl"

        records = []
        for r in results:
            if target == "adversarial" and r.residual.severity in ("blocking", "high"):
                records.append(builder.residual_to_adversarial_case(r.residual, r.proposal).to_dict())
            elif target == "curriculum":
                records.append(builder.residual_to_curriculum_unit(r.residual, r.proposal).to_dict())
            elif target == "calibration":
                records.append(builder.residual_to_calibration_case(r.residual, r.proposal).to_dict())
            elif target == "regression" and r.residual.severity in ("blocking", "high"):
                records.append(builder.residual_to_regression_test_spec(r.residual, r.proposal).to_dict())

        _Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(_json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"Written {len(records)} {target} records to {out_path}")

    elif args.command == "residual-calibrate":
        proposals = _load_proposals(args.input)
        results = engine.analyze_batch(proposals)
        residuals = [r.residual for r in results]
        cal_engine = ResidualCalibrationEngine()
        cal_report = cal_engine.generate_report(residuals)

        if args.output == "json":
            print(_json.dumps(cal_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(cal_report.to_markdown())

    elif args.command == "residual-test-specs":
        proposals = _load_proposals(args.input)
        results = engine.analyze_batch(proposals)
        gen = ResidualTestGenerator()
        proposal_map = {r.proposal.proposal_id: r.proposal.input_text for r in results}
        specs = gen.generate_batch(
            [r.residual for r in results],
            proposals=proposal_map,
        )
        out_path = args.output
        _Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            for spec in specs:
                fh.write(_json.dumps(spec.to_dict(), ensure_ascii=False) + "\n")
        print(f"Written {len(specs)} test specs to {out_path}")

    elif args.command == "curriculum-depth-report":
        from mcd.curriculum.depth_metrics import DepthMetricsCalculator

        calc = DepthMetricsCalculator()
        depth_report = calc.calculate()

        if args.output == "json":
            print(_json.dumps(depth_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(depth_report.to_markdown())

    elif args.command == "curriculum-coverage":
        from mcd.curriculum.curriculum_coverage_matrix import CurriculumCoverageMatrix

        matrix = CurriculumCoverageMatrix()
        cov_report = matrix.compute()

        if args.output == "json":
            print(_json.dumps(cov_report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(cov_report.to_markdown())

    elif args.command == "curriculum-residual-build":
        from mcd.curriculum.residual_curriculum_builder import ResidualCurriculumBuilder

        builder = ResidualCurriculumBuilder()
        proposals = builder.load_proposals(args.input)
        units, build_report = builder.build_dataset(proposals)
        out_path = args.output
        _Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        builder.save_units(units, out_path)
        print(f"Built {build_report.built_units} units → {out_path}")
        print(f"Residual types covered: {', '.join(build_report.residual_types_covered)}")
        if build_report.errors:
            print(f"Errors: {len(build_report.errors)}")



def _handle_trace_command(args) -> None:
    """Phase 7.1.2 — Unicode-to-Cognition Traceability CLI handlers."""
    import json as _json
    from mcd.traceability.trace_builder import TraceBuilder
    from mcd.traceability.trace_validator import TraceValidator
    from mcd.traceability.trace_report import TraceReport
    from mcd.traceability.serializers import trace_bundle_to_json

    builder = TraceBuilder()

    if args.command == "trace-text":
        bundle = builder.build(args.text)
        if args.output == "json":
            print(trace_bundle_to_json(bundle))
        elif args.output == "markdown":
            report = TraceReport(bundle)
            print(report.to_markdown())
        else:
            jt = bundle.judgment_trace
            print(f"Text:          {bundle.text}")
            print(f"Unicode units: {len(bundle.unicode_units)}")
            print(f"Graphemes:     {len(bundle.graphemes)}")
            print(f"Tokens:        {len(bundle.tokens)}")
            if jt:
                print(f"Decision:      {jt.final_decision}")
                print(f"Certainty:     {jt.certainty_policy}")

    elif args.command == "trace-validate":
        bundle = builder.build(args.text)
        validator = TraceValidator()
        vr = validator.validate(bundle)
        if args.output == "json":
            print(_json.dumps(vr.to_dict(), ensure_ascii=False, indent=2))
        elif args.output == "markdown":
            print(vr.to_markdown())
        else:
            status = "✅ PASSED" if vr.passed else "❌ FAILED"
            print(f"Trace Validation — {status}")
            print(f"  traceability_score: {vr.traceability_score:.4f}")
            print(f"  total_unicode:      {vr.total_unicode}")
            print(f"  traced_unicode:     {vr.traced_unicode}")
            if vr.violations:
                for v in vr.violations:
                    print(f"  ❌ {v}")

    elif args.command == "trace-report":
        from pathlib import Path as _Path
        golden_path = _Path("data/traceability/trace_golden_examples_ar.jsonl")
        if golden_path.exists():
            lines = [l.strip() for l in golden_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            reports = []
            scores = []
            for line in lines:
                ex = _json.loads(line)
                bun = builder.build(ex.get("text", ""))
                vr = TraceValidator().validate(bun)
                scores.append(vr.traceability_score)
                reports.append({"text": ex.get("text"), "score": vr.traceability_score, "passed": vr.passed})
            avg = sum(scores) / len(scores) if scores else 0.0
            if args.output == "json":
                print(_json.dumps({"avg_score": avg, "examples": reports}, ensure_ascii=False, indent=2))
            else:
                print(f"# Traceability Golden Examples Report")
                print(f"")
                print(f"Total examples: {len(lines)}")
                print(f"Average traceability_score: {avg:.4f}")
                print(f"")
                print(f"| # | Text (truncated) | Score | Passed |")
                print(f"|---|------------------|-------|--------|")
                for i, r in enumerate(reports, 1):
                    t = r['text'][:40].replace('|', '/')
                    icon = "✅" if r['passed'] else "❌"
                    print(f"| {i} | {t} | {r['score']:.4f} | {icon} |")
        else:
            print("No golden examples file found at data/traceability/trace_golden_examples_ar.jsonl")


if __name__ == "__main__":
    main()
