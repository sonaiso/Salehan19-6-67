"""Tests for foldable ResidualCalculator."""
import pytest
from mcd.foldable_learning.proposal_parser import ProposalParser
from mcd.foldable_learning.residual_calculator import ResidualCalculator
from mcd.foldable_learning.proposal_schema import GPTProposal, ProposalType


def _make_proposal(proposal_id, gpt_output, evidence=None, certainty=None, category=""):
    return GPTProposal(
        proposal_id=proposal_id,
        input_text="السؤال",
        gpt_output=gpt_output,
        proposal_type=ProposalType.ANSWER,
        claimed_evidence=evidence or [],
        claimed_certainty=certainty,
        metadata={"category": category},
    )


def test_gpt_output_is_never_evidence():
    """Critical: GPT output is never evidence."""
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-never", "هذا صحيح لأن GPT قاله", evidence=["gpt_output"])
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "gpt_as_evidence_residual" in r.residual_types


def test_false_certainty_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-cert", "بالتأكيد كل شيء صحيح", certainty="certain")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "certainty_residual" in r.residual_types or "evidence_residual" in r.residual_types


def test_api_as_authority_creates_tool_evidence_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-api", "واجهة API تؤكد أن هذا صحيح وموثوق")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "tool_evidence_residual" in r.residual_types


def test_gpt_as_evidence_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-gpt", "هذا صحيح لأن GPT أكد ذلك", evidence=["gpt_output"])
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "gpt_as_evidence_residual" in r.residual_types


def test_gpt_evidence_adds_evidence_gap():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-gpt2", "test", evidence=["gpt_output"])
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "gpt_output_used_as_evidence" in r.evidence_gaps


def test_harm_haram_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-hh", "هذا ضار لذلك هو حرام بالتأكيد")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "harm_haram_residual" in r.residual_types


def test_metaphor_literalization_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-meta", "جسد المجتمع مريض ويحتاج علاج حرفيًا كما المريض")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "metaphor_residual" in r.residual_types


def test_unsupported_generalization_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-gen", "كل الشركات تستخدم GraphRAG دائماً")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "unsupported_generalization_residual" in r.residual_types or "evidence_residual" in r.residual_types


def test_stale_source_creates_residual():
    calc = ResidualCalculator()
    parser = ProposalParser()
    p = _make_proposal("p-stale", "المعلومة", category="stale_source_as_current")
    g = parser.parse(p)
    r = calc.calculate(p, g)
    assert "traceability_residual" in r.residual_types or "evidence_residual" in r.residual_types
