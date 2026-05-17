"""Tests for types.py — verifies that only the three AFJG verdicts are allowed."""
from __future__ import annotations

import pytest

from mcd.llm_proposer.types import ALLOWED_VERDICTS, GovernedAnswer, Proposal, Verdict


def _make_proposal(text: str = "test claim") -> Proposal:
    return Proposal(prompt=text, raw_text=text, provider="echo", model="echo-v1")


class TestAllowedVerdicts:
    def test_allowed_verdicts_contains_exactly_three(self) -> None:
        assert ALLOWED_VERDICTS == {"ZERO", "HYPOTHESIS", "CERTIFICATE"}

    def test_zero_is_allowed(self) -> None:
        assert "ZERO" in ALLOWED_VERDICTS

    def test_hypothesis_is_allowed(self) -> None:
        assert "HYPOTHESIS" in ALLOWED_VERDICTS

    def test_certificate_is_allowed(self) -> None:
        assert "CERTIFICATE" in ALLOWED_VERDICTS

    def test_no_other_values_allowed(self) -> None:
        forbidden = {"PENDING", "PARTIAL", "MERGED", "PASS", "VALID", "UNKNOWN"}
        assert forbidden.isdisjoint(ALLOWED_VERDICTS)


class TestGovernedAnswerValidation:
    def test_valid_zero(self) -> None:
        answer = GovernedAnswer(
            proposal=_make_proposal(),
            verdict="ZERO",
            evidence=[],
            reverse_trace=[],
            violated_rules=["empty_proposal"],
        )
        assert answer.verdict == "ZERO"

    def test_valid_hypothesis(self) -> None:
        answer = GovernedAnswer(
            proposal=_make_proposal(),
            verdict="HYPOTHESIS",
            evidence=[],
            reverse_trace=[],
            violated_rules=[],
        )
        assert answer.verdict == "HYPOTHESIS"

    def test_valid_certificate(self) -> None:
        answer = GovernedAnswer(
            proposal=_make_proposal(),
            verdict="CERTIFICATE",
            evidence=["evidence item"],
            reverse_trace=["trace step"],
            violated_rules=[],
        )
        assert answer.verdict == "CERTIFICATE"

    def test_invalid_verdict_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Forbidden verdict"):
            GovernedAnswer(
                proposal=_make_proposal(),
                verdict="MERGED",  # type: ignore[arg-type]
                evidence=[],
                reverse_trace=[],
                violated_rules=[],
            )

    def test_created_at_is_populated(self) -> None:
        answer = GovernedAnswer(
            proposal=_make_proposal(),
            verdict="HYPOTHESIS",
            evidence=[],
            reverse_trace=[],
            violated_rules=[],
        )
        assert answer.created_at
        assert "T" in answer.created_at  # ISO-8601 format
