from __future__ import annotations

from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.types import Proposal


def _proposal() -> Proposal:
    return Proposal(prompt="claim", raw_text="claim", provider="echo", model="echo-v1")


def test_blank_string_evidence_returns_hypothesis() -> None:
    answer = AFJGGovernor().govern(
        _proposal(),
        evidence=["   "],
        reverse_trace=["raw_text_units: claim"],
    )
    assert answer.verdict == "HYPOTHESIS"
    assert "evidence_missing_or_blank" in answer.violated_rules


def test_empty_dict_evidence_returns_hypothesis() -> None:
    answer = AFJGGovernor().govern(
        _proposal(),
        evidence=[{}],
        reverse_trace=["raw_text_units: claim"],
    )
    assert answer.verdict == "HYPOTHESIS"
    assert "evidence_missing_or_blank" in answer.violated_rules
