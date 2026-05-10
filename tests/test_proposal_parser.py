"""Tests for ProposalParser in foldable learning."""
import pytest
from mcd.foldable_learning.proposal_parser import ProposalParser
from mcd.foldable_learning.proposal_schema import GPTProposal, ProposalType


def _make(proposal_id, gpt_output, claimed_evidence=None, claimed_certainty=None, category=""):
    return GPTProposal(
        proposal_id=proposal_id,
        input_text="السؤال",
        gpt_output=gpt_output,
        proposal_type=ProposalType.ANSWER,
        claimed_evidence=claimed_evidence or [],
        claimed_certainty=claimed_certainty,
        metadata={"category": category},
    )


def test_parser_returns_proposal_graph():
    parser = ProposalParser()
    p = _make("p1", "هذا صحيح")
    graph = parser.parse(p)
    assert graph is not None
    assert graph.nodes


def test_gpt_as_evidence_detected_via_claimed_evidence():
    parser = ProposalParser()
    p = _make("p2", "هذا صحيح", claimed_evidence=["gpt_output"])
    graph = parser.parse(p)
    assert "gpt_as_evidence" in graph.warnings


def test_api_authority_detected():
    parser = ProposalParser()
    p = _make("p3", "واجهة API تؤكد أن هذا صحيح وموثوق")
    graph = parser.parse(p)
    assert "tool_api_not_standalone_evidence" in graph.warnings


def test_stale_source_detected():
    parser = ProposalParser()
    p = _make("p4", "وفق دراسة 1995 لا تزال سارية ومعتمدة")
    graph = parser.parse(p)
    assert "stale_source_used" in graph.warnings


def test_conflict_ignored_detected():
    parser = ProposalParser()
    p = _make("p5", "الرأي صحيح رغم الخلاف بين العلماء")
    graph = parser.parse(p)
    assert "conflict_ignored" in graph.warnings


def test_category_stale_source_adds_warning():
    parser = ProposalParser()
    p = _make("p6", "المصدر الأول هو المرجع", category="stale_source_as_current")
    graph = parser.parse(p)
    assert "stale_source_used" in graph.warnings


def test_category_wrong_domain_adds_warning():
    parser = ProposalParser()
    p = _make("p7", "هذه القاعدة تنطبق", category="wrong_domain")
    graph = parser.parse(p)
    assert "wrong_domain_application" in graph.warnings


def test_no_warnings_for_valid_proposal():
    parser = ProposalParser()
    p = _make("p8", "وفق الدراسة العلمية الموثقة", claimed_evidence=["verified_source"])
    graph = parser.parse(p)
    # No harmful warnings
    harmful = {"gpt_as_evidence", "harm_implies_haram", "prompt_injection_detected"}
    assert not (harmful & set(graph.warnings))
