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
