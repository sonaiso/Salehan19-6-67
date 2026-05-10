import pytest
from mcd.fractal_kernel import CognitiveFractalUnit, VALID_LEVELS, VALID_FOLD_STATES


def make_unit(**kwargs):
    defaults = dict(unit_id="CFU-001", level="word", unit_type="lexical",
                    fold_state="atomic", metadata={"generated": True})
    defaults.update(kwargs)
    return CognitiveFractalUnit(**defaults)


def test_valid_unit():
    u = make_unit()
    assert u.unit_id == "CFU-001"


def test_every_unit_has_level_and_fold_state():
    u = make_unit(level="token", fold_state="folded")
    assert u.level == "token"
    assert u.fold_state == "folded"


def test_invalid_level_raises():
    with pytest.raises(ValueError):
        make_unit(level="invalid_level")


def test_invalid_fold_state_raises():
    with pytest.raises(ValueError):
        make_unit(fold_state="broken")


def test_missing_unit_id_raises():
    with pytest.raises((ValueError, TypeError)):
        CognitiveFractalUnit(unit_id="", level="word", unit_type="x", fold_state="atomic")


def test_missing_unit_type_raises():
    with pytest.raises(ValueError):
        CognitiveFractalUnit(unit_id="X", level="word", unit_type="", fold_state="atomic")


def test_all_valid_levels():
    for level in VALID_LEVELS:
        u = make_unit(level=level)
        assert u.level == level


def test_all_valid_fold_states():
    for fs in VALID_FOLD_STATES:
        u = make_unit(fold_state=fs)
        assert u.fold_state == fs


def test_to_dict():
    u = make_unit()
    d = u.to_dict()
    assert d["unit_id"] == "CFU-001"
    assert d["level"] == "word"
    assert "fold_state" in d


def test_make_id():
    uid = CognitiveFractalUnit.make_id()
    assert uid.startswith("CFU-")
