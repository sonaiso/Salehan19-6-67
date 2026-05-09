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

    readiness_parser = subparsers.add_parser("readiness-score", help="Print production readiness scorecard")
    readiness_parser.add_argument("--output", choices=["markdown", "json"], default="json")

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
