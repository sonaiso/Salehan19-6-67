from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import Proposal


def test_nabhani_suspended_returns_hypothesis() -> None:
    proposal = Proposal(
        prompt="claim",
        raw_text="claim",
        provider="echo",
        model="echo-v1",
        metadata={"nabhani_claim": {"certainty": {"score": 0.2}}},
    )
    answer = AFJGGovernor().govern(
        proposal,
        evidence=["evidence"],
        reverse_trace=["raw_text_units: claim"],
    )
    assert answer.verdict == "HYPOTHESIS"
    assert "nabhani_rational_gate_suspended" in answer.violated_rules


def test_nabhani_rejected_returns_zero() -> None:
    proposal = Proposal(
        prompt="claim",
        raw_text="claim",
        provider="echo",
        model="echo-v1",
        metadata={"nabhani_claim": {"target_reality": ""}},
    )
    answer = AFJGGovernor().govern(
        proposal,
        evidence=["evidence"],
        reverse_trace=["raw_text_units: claim"],
    )
    assert answer.verdict == "ZERO"
