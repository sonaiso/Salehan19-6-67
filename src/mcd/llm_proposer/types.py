"""Types for the Governed LLM Proposer module.

Within AFJG, every LLM output is a *Proposal* — never a judgment.
A Proposal enters AFJG governance at HYPOTHESIS level and can only be
elevated to CERTIFICATE after passing all governance gates.

Only three final verdicts are allowed (AFJG closure rule):
  ZERO        — fatal violation or invalid proof path
  HYPOTHESIS  — plausible structure with incomplete evidence
  CERTIFICATE — evidence + governance + reverse trace completed
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

Verdict = Literal["ZERO", "HYPOTHESIS", "CERTIFICATE"]
ALLOWED_VERDICTS: frozenset[str] = frozenset({"ZERO", "HYPOTHESIS", "CERTIFICATE"})


@dataclass(frozen=True)
class Proposal:
    """LLM-generated proposal.  Never a judgment by itself."""

    prompt: str
    raw_text: str
    provider: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernedAnswer:
    """Final governed output produced by AFJGGovernor from a Proposal."""

    proposal: Proposal
    verdict: Verdict
    evidence: list[Any]
    reverse_trace: list[str]
    violated_rules: list[str]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.verdict not in ALLOWED_VERDICTS:
            raise ValueError(
                f"Forbidden verdict: {self.verdict!r}. "
                f"Only {sorted(ALLOWED_VERDICTS)} are allowed (AFJG closure rule)."
            )
