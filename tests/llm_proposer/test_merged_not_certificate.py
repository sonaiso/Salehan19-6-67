"""Tests enforcing the MERGED != CERTIFICATE rule.

A claim that passes through a pipeline but lacks a complete reverse trace
(as a "merged" state implies) must yield HYPOTHESIS, not CERTIFICATE.
"""
from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import Proposal


def _make_proposal(text: str) -> Proposal:
    return Proposal(prompt=text, raw_text=text, provider="echo", model="echo-v1")


class TestMergedNotCertificate:
    def setup_method(self) -> None:
        self.governor = AFJGGovernor()

    def test_merged_style_no_reverse_trace_is_hypothesis(self) -> None:
        """A claim with evidence but no reverse trace → HYPOTHESIS, not CERTIFICATE."""
        proposal = _make_proposal("ادعاء تم دمجه بدون reverse trace")
        answer = self.governor.govern(
            proposal,
            evidence=["evidence provided"],
            reverse_trace=[],  # no reverse trace — merged state, not certified
        )
        assert answer.verdict == "HYPOTHESIS"
        assert answer.verdict != "CERTIFICATE"

    def test_merged_style_no_evidence_is_hypothesis(self) -> None:
        """A claim with reverse trace but no evidence → HYPOTHESIS."""
        proposal = _make_proposal("ادعاء بدون دليل")
        answer = self.governor.govern(
            proposal,
            evidence=[],
            reverse_trace=["step 1"],
        )
        assert answer.verdict == "HYPOTHESIS"

    def test_pipeline_merged_style_is_hypothesis(self) -> None:
        """Pipeline with evidence but missing reverse trace → HYPOTHESIS."""
        pipeline = GovernedProposalPipeline(EchoProposer(), self.governor)
        # Pass evidence but no reverse_trace — merge-style without full trace
        answer = pipeline.run("merged claim", evidence=["some evidence"])
        assert answer.verdict == "HYPOTHESIS"
        assert answer.verdict != "CERTIFICATE"

    def test_merge_cannot_produce_certificate_without_full_governance(self) -> None:
        """Even an explicitly 'accepted' claim without trace is HYPOTHESIS."""
        proposal = _make_proposal("accepted claim")
        answer = self.governor.govern(proposal, evidence=["evidence"], reverse_trace=[])
        assert answer.verdict != "CERTIFICATE"

    def test_three_of_four_checks_not_certificate(self) -> None:
        """Three out of four checks passing is still HYPOTHESIS, never CERTIFICATE.

        Simulates a partial governance scenario by omitting the reverse_trace,
        which represents a missing gate in the full certificate requirements.
        """
        proposal = _make_proposal("claim with partial governance")
        # Supply evidence (check 1) but omit reverse_trace (check 2 missing)
        answer = self.governor.govern(
            proposal,
            evidence=["check1: evidence present", "check2: source verified", "check3: prior info"],
            reverse_trace=[],  # check 4: reverse trace absent
        )
        assert answer.verdict == "HYPOTHESIS"
        assert answer.verdict != "CERTIFICATE"
