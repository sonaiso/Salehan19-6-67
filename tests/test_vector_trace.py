"""Tests for VectorTrace."""
import pytest
from mcd.traceability.vector_trace import VectorTrace, VECTOR_TYPES


def test_valid_vector_trace():
    vt = VectorTrace(
        vector_id="V-001",
        vector_type="role",
        source_trace_ids=["U-1", "U-2"],
        vector={"root_candidate": 0.8, "affix_candidate": 0.3},
        contribution_weights={"U-1": 0.5, "U-2": 0.5},
        normalization_applied=True,
        explanation="test",
    )
    assert vt.vector_id == "V-001"


def test_invalid_vector_type():
    with pytest.raises(ValueError):
        VectorTrace(
            vector_id="V-bad",
            vector_type="bad_type",
            source_trace_ids=[],
            vector={},
            contribution_weights={},
            normalization_applied=False,
            explanation="",
        )


def test_out_of_range_vector():
    with pytest.raises(ValueError):
        VectorTrace(
            vector_id="V-bad2",
            vector_type="feature",
            source_trace_ids=["U-1"],
            vector={"dim": 1.5},
            contribution_weights={},
            normalization_applied=False,
            explanation="",
        )


def test_to_dict():
    vt = VectorTrace(
        vector_id="V-002",
        vector_type="feature",
        source_trace_ids=["U-1"],
        vector={"dim": 0.5},
        contribution_weights={"U-1": 1.0},
        normalization_applied=True,
        explanation="ok",
    )
    d = vt.to_dict()
    assert "vector_id" in d
    assert "vector" in d
    assert "source_trace_ids" in d


def test_all_vector_types():
    for vtype in VECTOR_TYPES:
        vt = VectorTrace(
            vector_id=f"V-{vtype}",
            vector_type=vtype,
            source_trace_ids=["U-1"],
            vector={"x": 0.5},
            contribution_weights={"U-1": 1.0},
            normalization_applied=False,
            explanation="",
        )
        assert vt.vector_type == vtype
