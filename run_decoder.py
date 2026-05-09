"""run_decoder.py — Epistemic Cognitive Decoder entry point (MVP).

Implements the Minimum Viable Product described in section 10 of the
Epistemic Cognitive Decoder specification:

    1. ontology.yaml   — واقع، حس، معلومات، ربط، فكر، مفهوم، يقين
    2. semiotics.yaml  — دال، مدلول، مطابقة، تضمن، التزام، كلي، جزئي
    3. relations.yaml  — إسناد، تقييد، تضمين، سبب، مسبب، علة، قياس
    4. decoder_policy.md — قواعد السماح والمنع المعرفي
    5. run_decoder.py  — يشغّل الديكودر المعرفي + التحقق + إخراج الجواب

Usage (CLI)::

    python run_decoder.py "ما الفرق بين العلم والثقافة؟"
    python run_decoder.py "هل المفاهيم مرتبطة بالواقع؟" --effort xhigh

Usage (Python API)::

    from bayani.epistemic_decoder import EpistemicCognitiveDecoder

    decoder = EpistemicCognitiveDecoder()
    output = decoder.decode("ما الفرق بين العلم والثقافة؟")
    print(output.final_answer)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Knowledge file paths (MVP — 5 files)
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent
_DECODER_DIR = _ROOT / "bayani" / "epistemic_decoder"

ONTOLOGY_PATH = _DECODER_DIR / "ontology.yaml"
SEMIOTICS_PATH = _DECODER_DIR / "semiotics.yaml"
RELATIONS_PATH = _DECODER_DIR / "relations.yaml"
DECODER_POLICY_PATH = _DECODER_DIR / "decoder_policy.md"


# ---------------------------------------------------------------------------
# Knowledge loader
# ---------------------------------------------------------------------------

def load_knowledge_files() -> dict:
    """Load and validate the four knowledge YAML/MD files.

    Returns a dict with keys: ``ontology``, ``semiotics``, ``relations``,
    ``policy``.  Raises ``FileNotFoundError`` if any file is missing.
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        print(
            "[run_decoder] Warning: PyYAML not installed. "
            "YAML knowledge files will not be loaded. "
            "Install with: pip install pyyaml",
            file=sys.stderr,
        )
        yaml = None  # type: ignore

    knowledge: dict = {}

    for key, path in [
        ("ontology", ONTOLOGY_PATH),
        ("semiotics", SEMIOTICS_PATH),
        ("relations", RELATIONS_PATH),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {path}")
        if yaml is not None:
            with path.open(encoding="utf-8") as f:
                knowledge[key] = yaml.safe_load(f)
        else:
            knowledge[key] = {"path": str(path), "loaded": False}

    if not DECODER_POLICY_PATH.exists():
        raise FileNotFoundError(f"Policy file not found: {DECODER_POLICY_PATH}")
    knowledge["policy"] = DECODER_POLICY_PATH.read_text(encoding="utf-8")

    return knowledge


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(
    query: str,
    reasoning_effort: str = "high",
    context: str = "",
    verbose: bool = False,
) -> dict:
    """Run the Epistemic Cognitive Decoder for *query*.

    Parameters
    ----------
    query:
        The user question or instruction.
    reasoning_effort:
        GPT-5.5 reasoning effort level.
        ``"low"`` | ``"medium"`` | ``"high"`` (default) | ``"xhigh"``.
    context:
        Optional extra context string.
    verbose:
        If True, print intermediate pipeline results.

    Returns
    -------
    dict
        Serialisable summary of the decoder output.
    """
    from bayani.epistemic_decoder import EpistemicCognitiveDecoder

    # Load knowledge files (validation step)
    try:
        knowledge = load_knowledge_files()
        if verbose:
            print(f"[run_decoder] Knowledge files loaded: {list(knowledge.keys())}")
    except FileNotFoundError as exc:
        print(f"[run_decoder] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Run decoder
    decoder = EpistemicCognitiveDecoder()
    output = decoder.decode(query, context=context, reasoning_effort=reasoning_effort)

    if verbose:
        print("\n─── Pipeline Trace ───────────────────────────────────")
        print(f"Task type       : {output.task.task_type if output.task else '—'}")
        print(f"Domain          : {output.task.domain if output.task else '—'}")
        print(f"Reality type    : {output.reality.reality_type if output.reality else '—'}")
        print(
            f"Reality objects : "
            f"{output.reality.reality_objects if output.reality else '—'}"
        )
        if output.semiotic_map:
            print(
                f"Signifiers      : "
                f"{[s.text for s in output.semiotic_map.signifiers]}"
            )
        if output.relation_graph:
            print(
                f"Relations built : {len(output.relation_graph.relations)}"
            )
        if output.evidence:
            print(f"Evidence items  : {len(output.evidence.items)}")
        print(f"Verified thoughts: {len(output.verified_thoughts)}")
        print(f"Certainty level : {output.certainty_level}")
        print(f"Answer score    : {output.answer_score:.2f}")
        print("─────────────────────────────────────────────────────\n")

    # Print final answer
    print(output.final_answer)

    if output.blocked:
        print(f"\n[BLOCKED] {output.block_reason}", file=sys.stderr)

    return {
        "query": query,
        "reasoning_effort": reasoning_effort,
        "task_type": output.task.task_type if output.task else None,
        "domain": output.task.domain if output.task else None,
        "reality_type": output.reality.reality_type if output.reality else None,
        "certainty_level": output.certainty_level,
        "answer_score": output.answer_score,
        "blocked": output.blocked,
        "block_reason": output.block_reason,
        "verified_thoughts_count": len(output.verified_thoughts),
        "final_answer": output.final_answer,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_decoder",
        description=(
            "Epistemic Cognitive Decoder — runs the full epistemic pipeline "
            "for an Arabic (or English) query and outputs a certainty-gated answer."
        ),
    )
    parser.add_argument("query", help="The question or instruction to process.")
    parser.add_argument(
        "--effort",
        choices=["low", "medium", "high", "xhigh"],
        default="high",
        help="Reasoning effort level (default: high).",
    )
    parser.add_argument(
        "--context",
        default="",
        help="Optional extra context for the decoder.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print intermediate pipeline results.",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output the result as JSON.",
    )
    return parser


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    result = run(
        query=args.query,
        reasoning_effort=args.effort,
        context=args.context,
        verbose=args.verbose,
    )

    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
