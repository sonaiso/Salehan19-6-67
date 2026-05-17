"""CLI entry point for the Governed LLM Proposer.

Usage::

    python -m mcd.llm_proposer --provider echo --prompt "النار محرقة"
    python -m mcd.llm_proposer --provider echo --prompt "ادعاء" \\
        --evidence "دليل 1" --evidence "دليل 2"
    python -m mcd.llm_proposer --replay artifacts/llm_proposer/xxx.json

Exit codes:
  0 — CERTIFICATE
  1 — HYPOTHESIS
  2 — ZERO
"""
from __future__ import annotations

import argparse
import json
import sys

from mcd.llm_proposer import trace as trace_module
from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.types import GovernedAnswer

_EXIT_CODES: dict[str, int] = {
    "CERTIFICATE": 0,
    "HYPOTHESIS": 1,
    "ZERO": 2,
}


def _build_proposer(provider: str) -> object:
    if provider == "echo":
        from mcd.llm_proposer.providers.echo import EchoProposer  # noqa: PLC0415

        return EchoProposer()
    if provider == "openai":
        from mcd.llm_proposer.providers.openai_proposer import OpenAIProposer  # noqa: PLC0415

        return OpenAIProposer()
    if provider == "anthropic":
        from mcd.llm_proposer.providers.anthropic_proposer import AnthropicProposer  # noqa: PLC0415

        return AnthropicProposer()
    raise ValueError(f"Unknown provider: {provider!r}. Choose from: echo, openai, anthropic")


def _print_answer(answer: GovernedAnswer) -> None:
    data = {
        "verdict": answer.verdict,
        "evidence": answer.evidence,
        "reverse_trace": answer.reverse_trace,
        "violated_rules": answer.violated_rules,
        "created_at": answer.created_at,
        "proposal": {
            "prompt": answer.proposal.prompt,
            "raw_text": answer.proposal.raw_text,
            "provider": answer.proposal.provider,
            "model": answer.proposal.model,
        },
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m mcd.llm_proposer",
        description="Governed LLM Proposer — LLMs propose; AFJG governs judgment.",
    )
    parser.add_argument("--provider", default="echo", help="Proposer provider (echo/openai/anthropic)")
    parser.add_argument("--prompt", default="", help="Prompt / claim to evaluate")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence item (repeatable)")
    parser.add_argument("--replay", default="", help="Path to a saved artifact to replay")
    parser.add_argument("--save", action="store_true", help="Save the artifact to artifacts/llm_proposer/")

    args = parser.parse_args(argv)

    governor = AFJGGovernor()

    if args.replay:
        answer = trace_module.replay(args.replay, governor)
    else:
        if not args.prompt:
            parser.error("--prompt is required unless --replay is used")
        proposer = _build_proposer(args.provider)
        pipeline = GovernedProposalPipeline(proposer, governor)  # type: ignore[arg-type]
        answer = pipeline.run(args.prompt, evidence=args.evidence or None)

    if args.save:
        saved_path = trace_module.save(answer)
        import sys as _sys  # noqa: PLC0415

        print(f"[trace saved] {saved_path}", file=_sys.stderr)

    _print_answer(answer)
    return _EXIT_CODES.get(answer.verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
