"""Tests that no fourth verdict is permitted (AFJG closure rule)."""
from __future__ import annotations

import pytest

from mcd.llm_proposer.types import ALLOWED_VERDICTS, GovernedAnswer, Proposal


def _base_answer(verdict: str) -> GovernedAnswer:
    return GovernedAnswer(
        proposal=Proposal(prompt="x", raw_text="x", provider="echo", model="echo-v1"),
        verdict=verdict,  # type: ignore[arg-type]
        evidence=[],
        reverse_trace=[],
        violated_rules=[],
    )


class TestNoFourthVerdict:
    @pytest.mark.parametrize(
        "forbidden_verdict",
        ["MERGED", "PENDING", "PARTIAL", "PASS", "VALID", "UNKNOWN", "ACCEPTED", "REJECTED"],
    )
    def test_forbidden_verdict_raises_value_error(self, forbidden_verdict: str) -> None:
        with pytest.raises(ValueError, match="Forbidden verdict"):
            _base_answer(forbidden_verdict)

    def test_only_three_verdicts_exist(self) -> None:
        assert len(ALLOWED_VERDICTS) == 3

    def test_zero_does_not_raise(self) -> None:
        answer = _base_answer("ZERO")
        assert answer.verdict == "ZERO"

    def test_hypothesis_does_not_raise(self) -> None:
        answer = _base_answer("HYPOTHESIS")
        assert answer.verdict == "HYPOTHESIS"

    def test_certificate_does_not_raise(self) -> None:
        answer = GovernedAnswer(
            proposal=Proposal(prompt="x", raw_text="x", provider="echo", model="echo-v1"),
            verdict="CERTIFICATE",
            evidence=["evidence"],
            reverse_trace=["trace"],
            violated_rules=[],
        )
        assert answer.verdict == "CERTIFICATE"

    def test_error_message_lists_allowed_verdicts(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            _base_answer("MERGED")
        message = str(exc_info.value)
        assert "CERTIFICATE" in message
        assert "HYPOTHESIS" in message
        assert "ZERO" in message
