"""EchoProposer — deterministic proposer for CI and testing.

Requires no API key.  Returns a fixed, reproducible Proposal whose
raw_text is ``ECHO::<prompt>``.  This is the default proposer for all
automated tests and local verification runs.
"""
from __future__ import annotations

from mcd.llm_proposer.base import BaseLLMProposer
from mcd.llm_proposer.types import Proposal


class EchoProposer(BaseLLMProposer):
    """Deterministic proposer that echoes the prompt — no API needed."""

    name: str = "echo"
    model: str = "echo-v1"

    def propose(self, prompt: str, **kwargs: object) -> Proposal:
        return Proposal(
            prompt=prompt,
            raw_text=f"ECHO::{prompt}",
            provider=self.name,
            model=self.model,
            metadata={"echo": True},
        )
