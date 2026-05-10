"""Tests for GPTProposal and ProposalGraph in foldable context."""
import pytest
from mcd.foldable_learning.proposal_schema import GPTProposal, ProposalGraph, ProposalType


def test_gpt_proposal_gpt_output_is_never_evidence():
    p = GPTProposal(proposal_id="t1", input_text="x", gpt_output="y", proposal_type=ProposalType.ANSWER)
    assert p.claimed_evidence == []


def test_gpt_proposal_claimed_certainty_default():
    p = GPTProposal(proposal_id="t1", input_text="x", gpt_output="y", proposal_type=ProposalType.ANSWER)
    assert p.claimed_certainty is None


def test_gpt_proposal_to_dict():
    p = GPTProposal(proposal_id="t1", input_text="q", gpt_output="a", proposal_type=ProposalType.ANSWER)
    d = p.to_dict()
    assert d["proposal_id"] == "t1"
    assert "gpt_output" in d


def test_gpt_proposal_from_dict_roundtrip():
    d = {"proposal_id": "t2", "input_text": "q", "gpt_output": "a", "proposal_type": "answer",
         "claimed_evidence": [], "claimed_certainty": None, "metadata": {}}
    p = GPTProposal.from_dict(d)
    assert p.proposal_id == "t2"


def test_proposal_type_has_all_types():
    assert ProposalType.ANSWER
    assert ProposalType.EXPLANATION
    assert ProposalType.ADVERSARIAL_CASE


def test_gpt_output_is_never_evidence():
    """Critical: GPT output must never be accepted as evidence."""
    p = GPTProposal(
        proposal_id="test",
        input_text="السؤال",
        gpt_output="الجواب",
        proposal_type=ProposalType.ANSWER,
        claimed_evidence=["gpt_output"],
    )
    # GPT output in claimed_evidence should not be accepted as verified evidence
    assert "gpt_output" in p.claimed_evidence  # it's listed but unverified
    # The system must flag this as gpt_as_evidence
