import pytest
from mcd.fractal_kernel import CrossLayerConflictResolver, CrossLayerConflict


def test_resolve_emphasis_vs_evidence():
    resolver = CrossLayerConflictResolver()
    conflict = resolver.resolve("emphasis_vs_evidence", ["mabni", "evidence"])
    assert conflict.winning_layer == "evidence"
    assert len(conflict.warnings) > 0


def test_resolve_syntactic_vs_factual():
    resolver = CrossLayerConflictResolver()
    conflict = resolver.resolve("syntactic_vs_factual_certainty", ["murab", "evidence"])
    assert conflict.certainty_effect == "suspend_factual"


def test_check_emphasis_is_evidence_false():
    resolver = CrossLayerConflictResolver()
    valid, warnings = resolver.check_emphasis_is_evidence(True, False)
    assert valid is False
    assert len(warnings) > 0


def test_check_emphasis_with_independent_evidence():
    resolver = CrossLayerConflictResolver()
    valid, warnings = resolver.check_emphasis_is_evidence(True, True)
    assert valid is True


def test_check_irab_is_factual():
    resolver = CrossLayerConflictResolver()
    valid, warnings = resolver.check_irab_is_factual(True, False)
    # Returns True with warning
    assert valid is True
    assert len(warnings) > 0


def test_check_gpt_as_evidence():
    resolver = CrossLayerConflictResolver()
    valid, warnings = resolver.check_gpt_as_evidence(True)
    assert valid is False
    assert "gpt_not_evidence" in warnings[0]


def test_unknown_conflict_type_raises():
    resolver = CrossLayerConflictResolver()
    with pytest.raises(ValueError):
        resolver.resolve("nonexistent_conflict_xyz", [])


def test_conflict_to_dict():
    resolver = CrossLayerConflictResolver()
    conflict = resolver.resolve("trace_vs_truth", ["trace", "evidence"])
    d = conflict.to_dict()
    assert "conflict_id" in d
    assert d["conflict_type"] == "trace_vs_truth"
