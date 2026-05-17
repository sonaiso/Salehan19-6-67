"""Governed LLM Proposer sub-package.

Implements the AFJG thesis: "LLMs propose; AFJG governs judgment."

Every LLM output enters governance at HYPOTHESIS level and is only
elevated to CERTIFICATE when all AFJG gates pass, evidence is present,
and reverse trace is complete.

Public surface:
  - GovernedProposalPipeline  — main entry point
  - AFJGGovernor              — governance engine
  - EchoProposer              — deterministic proposer (CI/tests)
  - types: Proposal, GovernedAnswer, Verdict
"""
from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import (
    ALLOWED_VERDICTS,
    GovernedAnswer,
    Proposal,
    Verdict,
)
from mcd.llm_proposer.verdict_mapping import (
    PUBLIC_JUDGMENT_TO_VERDICT,
    VERDICT_TO_PUBLIC_JUDGMENT,
    public_judgment_to_verdict,
    verdict_to_public_judgment,
)

__all__ = [
    "AFJGGovernor",
    "ALLOWED_VERDICTS",
    "EchoProposer",
    "GovernedAnswer",
    "GovernedProposalPipeline",
    "Proposal",
    "PUBLIC_JUDGMENT_TO_VERDICT",
    "VERDICT_TO_PUBLIC_JUDGMENT",
    "Verdict",
    "public_judgment_to_verdict",
    "verdict_to_public_judgment",
]
