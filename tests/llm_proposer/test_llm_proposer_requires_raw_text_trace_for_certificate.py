from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import Proposal


def _proposal() -> Proposal:
    return Proposal(prompt="النار محرقة", raw_text="النار محرقة", provider="echo", model="echo-v1")


def test_evidence_and_trace_without_raw_text_anchor_is_hypothesis() -> None:
    answer = AFJGGovernor().govern(
        _proposal(),
        evidence=["empirical evidence"],
        reverse_trace=["step 1", "step 2"],
    )
    assert answer.verdict == "HYPOTHESIS"
    assert "reverse_trace_missing_raw_text" in answer.violated_rules


def test_evidence_and_raw_text_anchored_trace_can_issue_certificate() -> None:
    answer = AFJGGovernor().govern(
        _proposal(),
        evidence=["empirical evidence"],
        reverse_trace={"complete": True, "raw_text_units": ["النار محرقة"], "trace": ["gate walkthrough"]},
    )
    assert answer.verdict == "CERTIFICATE"
