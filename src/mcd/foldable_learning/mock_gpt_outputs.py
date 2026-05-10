"""generate_mock_proposals — loads from JSONL or generates deterministically."""
from __future__ import annotations
import json
from pathlib import Path
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalType

__all__ = ["generate_mock_proposals"]

_DATA_PATH = Path("data/foldable_learning/mock_gpt_proposals_ar.jsonl")


def generate_mock_proposals(n: int = 100) -> list[GPTProposal]:
    """Load mock proposals from JSONL or generate deterministically."""
    path = _DATA_PATH
    if not path.exists():
        for candidate in [
            Path("/home/runner/work/Salehan19-6-67/Salehan19-6-67") / "data/foldable_learning/mock_gpt_proposals_ar.jsonl",
        ]:
            if candidate.exists():
                path = candidate
                break
        else:
            return _generate_deterministic(n)

    proposals = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                proposals.append(GPTProposal.from_dict(json.loads(line)))
    return proposals[:n]


def _generate_deterministic(n: int) -> list[GPTProposal]:
    """Fallback: generate n deterministic proposals."""
    templates = [
        ("fold-det-{i:03d}", "ما حكم هذا؟", "هذا صحيح وفق المصادر", "answer", [], None, "correct_with_evidence"),
        ("fold-det-{i:03d}", "هل هذا صحيح؟", "نعم بالتأكيد", "answer", [], "certain", "false_certainty"),
        ("fold-det-{i:03d}", "ما دليلك؟", "GPT أكد ذلك", "answer", ["gpt_output"], None, "gpt_as_evidence"),
    ]
    result = []
    for i in range(n):
        t = templates[i % len(templates)]
        result.append(GPTProposal(
            proposal_id=t[0].format(i=i),
            input_text=t[1],
            gpt_output=t[2],
            proposal_type=ProposalType(t[3]),
            claimed_evidence=list(t[4]),
            claimed_certainty=t[5],
            metadata={"category": t[6]},
        ))
    return result
