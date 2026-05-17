"""Tests that valid proposals without complete evidence yield HYPOTHESIS."""
from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import Proposal


def _make_proposal(text: str) -> Proposal:
    return Proposal(prompt=text, raw_text=text, provider="echo", model="echo-v1")


class TestGovernorHypothesisDefault:
    def setup_method(self) -> None:
        self.governor = AFJGGovernor()

    def test_valid_text_no_evidence_is_hypothesis(self) -> None:
        proposal = _make_proposal("النار محرقة")
        answer = self.governor.govern(proposal, evidence=[], reverse_trace=[])
        assert answer.verdict == "HYPOTHESIS"

    def test_valid_text_with_evidence_but_no_trace_is_hypothesis(self) -> None:
        proposal = _make_proposal("النار محرقة")
        answer = self.governor.govern(
            proposal,
            evidence=["التجربة تثبت ذلك"],
            reverse_trace=[],
        )
        assert answer.verdict == "HYPOTHESIS"

    def test_valid_text_with_trace_but_no_evidence_is_hypothesis(self) -> None:
        proposal = _make_proposal("النار محرقة")
        answer = self.governor.govern(
            proposal,
            evidence=[],
            reverse_trace=["step 1"],
        )
        assert answer.verdict == "HYPOTHESIS"

    def test_hypothesis_has_no_violated_rules_for_clean_claim(self) -> None:
        proposal = _make_proposal("الماء يغلي عند مئة درجة")
        answer = self.governor.govern(proposal)
        # Should be HYPOTHESIS (no evidence) with no rule violations
        assert answer.verdict == "HYPOTHESIS"

    def test_pipeline_default_is_hypothesis(self) -> None:
        pipeline = GovernedProposalPipeline(EchoProposer(), self.governor)
        answer = pipeline.run("simple claim")
        assert answer.verdict == "HYPOTHESIS"

    def test_echo_pipeline_no_evidence_is_hypothesis(self) -> None:
        pipeline = GovernedProposalPipeline(EchoProposer())
        answer = pipeline.run("another claim")
        assert answer.verdict == "HYPOTHESIS"
