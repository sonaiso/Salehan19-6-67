"""Tests that a fully evidenced, traced, violation-free claim yields CERTIFICATE."""
from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer
from mcd.llm_proposer.types import Proposal


def _make_proposal(text: str) -> Proposal:
    return Proposal(prompt=text, raw_text=text, provider="echo", model="echo-v1")


class TestGovernorCertificatePath:
    def setup_method(self) -> None:
        self.governor = AFJGGovernor()

    def _full_evidence(self) -> list[str]:
        return ["empirical observation", "peer review", "reproducible experiment"]

    def _full_trace(self) -> list[str]:
        return [
            "step 1: claim formulated",
            "step 2: evidence gathered",
            "raw_text_units: النار محرقة",
            "step 3: gates passed",
        ]

    def test_evidence_and_trace_yields_certificate(self) -> None:
        proposal = _make_proposal("النار محرقة")
        answer = self.governor.govern(
            proposal,
            evidence=self._full_evidence(),
            reverse_trace=self._full_trace(),
        )
        assert answer.verdict == "CERTIFICATE"

    def test_certificate_has_no_violated_rules(self) -> None:
        proposal = _make_proposal("الماء يغلي عند مئة درجة")
        answer = self.governor.govern(
            proposal,
            evidence=self._full_evidence(),
            reverse_trace=self._full_trace(),
        )
        assert answer.verdict == "CERTIFICATE"
        assert answer.violated_rules == []

    def test_certificate_preserves_evidence(self) -> None:
        proposal = _make_proposal("claim")
        evidence = self._full_evidence()
        answer = self.governor.govern(
            proposal,
            evidence=evidence,
            reverse_trace=self._full_trace(),
        )
        assert answer.verdict == "CERTIFICATE"
        for item in evidence:
            assert item in answer.evidence

    def test_certificate_has_reverse_trace(self) -> None:
        proposal = _make_proposal("claim")
        answer = self.governor.govern(
            proposal,
            evidence=self._full_evidence(),
            reverse_trace=self._full_trace(),
        )
        assert answer.reverse_trace  # non-empty

    def test_pipeline_with_evidence_and_trace_yields_certificate(self) -> None:
        pipeline = GovernedProposalPipeline(EchoProposer(), self.governor)
        answer = pipeline.run(
            "النار محرقة",
            evidence=self._full_evidence(),
            reverse_trace=self._full_trace(),
        )
        assert answer.verdict == "CERTIFICATE"

    def test_single_evidence_and_single_trace_step_yields_certificate(self) -> None:
        proposal = _make_proposal("claim")
        answer = self.governor.govern(
            proposal,
            evidence=["one piece of evidence"],
            reverse_trace=["raw_text_units: claim anchor"],
        )
        assert answer.verdict == "CERTIFICATE"
