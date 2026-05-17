"""Tests that claims violating AFJG rules produce ZERO verdict."""
from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import Proposal


def _make_proposal(text: str, prompt: str = "") -> Proposal:
    return Proposal(
        prompt=prompt or text,
        raw_text=text,
        provider="echo",
        model="echo-v1",
    )


class TestGovernorZeroOnViolation:
    def setup_method(self) -> None:
        self.governor = AFJGGovernor()

    def test_empty_proposal_yields_zero(self) -> None:
        proposal = _make_proposal("")
        answer = self.governor.govern(proposal)
        assert answer.verdict == "ZERO"

    def test_whitespace_only_proposal_yields_zero(self) -> None:
        proposal = _make_proposal("   ")
        answer = self.governor.govern(proposal)
        assert answer.verdict == "ZERO"

    def test_contradiction_without_evidence_yields_zero(self) -> None:
        proposal = _make_proposal("هذا الادعاء contradiction بدون دليل")
        answer = self.governor.govern(proposal, evidence=[])
        assert answer.verdict == "ZERO"

    def test_impossible_claim_without_evidence_yields_zero(self) -> None:
        proposal = _make_proposal("this claim is impossible without proof")
        answer = self.governor.govern(proposal)
        assert answer.verdict == "ZERO"

    def test_arabic_contradiction_keyword_yields_zero(self) -> None:
        proposal = _make_proposal("الادعاء متناقض")
        answer = self.governor.govern(proposal)
        assert answer.verdict == "ZERO"

    def test_arabic_impossible_keyword_yields_zero(self) -> None:
        proposal = _make_proposal("هذا مستحيل")
        answer = self.governor.govern(proposal)
        assert answer.verdict == "ZERO"

    def test_zero_has_violated_rules(self) -> None:
        proposal = _make_proposal("")
        answer = self.governor.govern(proposal)
        assert answer.violated_rules  # not empty

    def test_zero_verdict_is_valid_governed_answer(self) -> None:
        proposal = _make_proposal("")
        answer = self.governor.govern(proposal)
        # Must not raise — ZERO is a valid AFJG verdict
        assert answer.verdict == "ZERO"
