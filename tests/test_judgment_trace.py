"""Tests for JudgmentTrace."""
import pytest
from mcd.traceability.judgment_trace import JudgmentTrace, FINAL_DECISIONS


def make_judgment(**kwargs):
    defaults = dict(
        judgment_id="J-001",
        input_text="test",
        unicode_trace_ids=["U-1"],
        token_ids=["T-1"],
        node_ids=[],
        edge_ids=[],
        vector_ids=[],
        evidence_status="present",
        certainty_policy="strong_knowledge",
        final_decision="answer",
        warnings=[],
        explanation="ok",
    )
    defaults.update(kwargs)
    return JudgmentTrace(**defaults)


def test_valid_judgment():
    j = make_judgment()
    assert j.judgment_id == "J-001"
    assert j.final_decision == "answer"


def test_invalid_decision():
    with pytest.raises(ValueError):
        make_judgment(final_decision="bad_decision")


def test_all_decisions():
    for d in FINAL_DECISIONS:
        j = make_judgment(final_decision=d)
        assert j.final_decision == d


def test_to_dict():
    j = make_judgment()
    d = j.to_dict()
    required = [
        "judgment_id", "input_text", "unicode_trace_ids", "token_ids",
        "node_ids", "edge_ids", "vector_ids",
        "evidence_status", "certainty_policy", "final_decision",
        "warnings", "explanation",
    ]
    for k in required:
        assert k in d


def test_suspend_with_warnings():
    j = make_judgment(
        final_decision="suspend",
        certainty_policy="suspend",
        warnings=["Judgment suspended: evidence missing"],
    )
    assert j.final_decision == "suspend"
    assert len(j.warnings) > 0
