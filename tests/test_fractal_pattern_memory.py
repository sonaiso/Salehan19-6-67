import pytest
from mcd.fractal_kernel import FractalPattern, PatternMemory, PATTERN_TYPES


def make_pattern(**kwargs):
    defaults = dict(pattern_id="PAT-001", pattern_type="residual",
                    recall_keys=["missing_source"])
    defaults.update(kwargs)
    return FractalPattern(**defaults)


def test_add_and_recall():
    mem = PatternMemory()
    p = make_pattern()
    mem.add_pattern(p)
    results = mem.recall("missing_source")
    assert len(results) == 1


def test_search_by_type():
    mem = PatternMemory()
    mem.add_pattern(make_pattern(pattern_type="residual"))
    mem.add_pattern(make_pattern(pattern_id="PAT-002", pattern_type="evidence_gap"))
    results = mem.search_by_type("residual")
    assert len(results) == 1


def test_invalid_pattern_type():
    with pytest.raises(ValueError):
        make_pattern(pattern_type="unknown_xyz")


def test_all_valid_pattern_types():
    mem = PatternMemory()
    for pt in PATTERN_TYPES:
        p = FractalPattern(pattern_id=f"PAT-{pt}", pattern_type=pt)
        mem.add_pattern(p)
    assert len(mem) == len(PATTERN_TYPES)


def test_search_by_vector_signature():
    mem = PatternMemory()
    p = make_pattern(vector_signature={"evidence_vector": 0.0, "certainty_vector": 0.3})
    mem.add_pattern(p)
    results = mem.search_by_vector_signature({"evidence_vector": 0.0})
    assert len(results) == 1


def test_export():
    mem = PatternMemory()
    mem.add_pattern(make_pattern())
    exported = mem.export()
    assert len(exported) == 1


def test_len():
    mem = PatternMemory()
    assert len(mem) == 0
