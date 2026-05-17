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

__all__ = [
    "AFJGGovernor",
    "ALLOWED_VERDICTS",
    "EchoProposer",
    "GovernedAnswer",
    "GovernedProposalPipeline",
    "Proposal",
    "Verdict",
]
