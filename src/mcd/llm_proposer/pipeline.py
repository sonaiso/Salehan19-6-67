"""GovernedProposalPipeline — orchestrates propose → govern → certify.

Implements the core AFJG thesis:
  "LLMs propose; AFJG governs judgment."

Every run produces a GovernedAnswer.  The verdict starts at HYPOTHESIS
(LLM output is never trusted directly) and is only elevated to CERTIFICATE
when all governance gates pass, evidence is present, and reverse trace is
complete.
"""
from __future__ import annotations

from mcd.llm_proposer.base import BaseLLMProposer
from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import GovernedAnswer


class GovernedProposalPipeline:
    """End-to-end pipeline: LLM proposal → AFJG governance → final judgment.

    Args:
        proposer: Any BaseLLMProposer implementation.
        governor: An AFJGGovernor instance.
    """

    def __init__(
        self,
        proposer: BaseLLMProposer,
        governor: AFJGGovernor | None = None,
    ) -> None:
        self._proposer = proposer
        self._governor = governor if governor is not None else AFJGGovernor()

    def run(
        self,
        prompt: str,
        *,
        evidence: list[str] | None = None,
        reverse_trace: list[str] | None = None,
    ) -> GovernedAnswer:
        """Propose then govern.

        Args:
            prompt: The claim or question submitted to the LLM.
            evidence: Optional caller-supplied evidence items.
            reverse_trace: Optional caller-supplied trace steps.

        Returns:
            A GovernedAnswer with verdict ZERO / HYPOTHESIS / CERTIFICATE.
        """
        proposal = self._proposer.propose(prompt)
        return self._governor.govern(
            proposal,
            evidence=evidence,
            reverse_trace=reverse_trace,
        )
