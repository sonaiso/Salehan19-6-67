"""Tests for RecallEngine."""
import pytest
from mcd.foldable_learning.recall_engine import RecallEngine, RecallResult
from mcd.foldable_learning.pattern_memory import PatternMemory
from mcd.foldable_learning.fold_signature import FoldSignatureRegistry
from mcd.foldable_learning.proposal_parser import ProposalParser
from mcd.foldable_learning.proposal_schema import GPTProposal, ProposalType


def _make_memory():
    mem = PatternMemory()
    for sig in FoldSignatureRegistry.all():
        mem.add_fold_signature(sig)
    return mem


def _make_graph(gpt_output, evidence=None):
    p = GPTProposal(
        proposal_id="test",
        input_text="السؤال",
        gpt_output=gpt_output,
        proposal_type=ProposalType.ANSWER,
        claimed_evidence=evidence or [],
    )
    parser = ProposalParser()
    return parser.parse(p)


def test_recall_returns_result():
    mem = _make_memory()
    eng = RecallEngine(mem)
    result = eng.recall(text="test text")
    assert isinstance(result, RecallResult)


def test_recall_unsupported_generalization():
    mem = _make_memory()
    eng = RecallEngine(mem)
    graph = _make_graph("كل الشركات تستخدم GraphRAG دائماً")
    result = eng.recall(graph=graph)
    assert result.recommended_certainty_policy in ("suspend", "hypothesis", "probable_knowledge")


def test_recall_gpt_as_evidence():
    mem = _make_memory()
    eng = RecallEngine(mem)
    graph = _make_graph("هذا صحيح", evidence=["gpt_output"])
    result = eng.recall(graph=graph)
    assert result.recalled_fold_signatures or result.recommended_warnings


def test_recall_precision_estimate_positive():
    mem = _make_memory()
    eng = RecallEngine(mem)
    result = eng.recall(text="أي نص")
    assert result.recall_precision_estimate > 0


def test_recall_has_explanation():
    mem = _make_memory()
    eng = RecallEngine(mem)
    result = eng.recall(text="test")
    assert result.explanation
