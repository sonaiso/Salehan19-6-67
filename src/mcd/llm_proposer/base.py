"""Base abstract class for LLM proposers within the AFJG-governed pipeline.

A proposer converts a human prompt into a *Proposal* — a structured
candidate for governance.  The proposer has no authority to issue a judgment;
that authority belongs exclusively to AFJGGovernor.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from mcd.llm_proposer.types import Proposal


class BaseLLMProposer(ABC):
    """Abstract base for all LLM proposer implementations."""

    name: str = "base"
    model: str = "unspecified"

    @abstractmethod
    def propose(self, prompt: str, **kwargs: object) -> Proposal:
        """Generate a Proposal from *prompt*.

        Must not perform any governance or judgment logic.
        """
