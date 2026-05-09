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

    args = parser.parse_args()

    if args.command == "nabhani":
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


if __name__ == "__main__":
    main()
