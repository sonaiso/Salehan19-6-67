"""Properties of :func:`mcd.afu.core.residual_vector.accumulate_residuals`."""
from __future__ import annotations

from mcd.afu.core.residual_vector import accumulate_residuals


def test_empty_inputs_yield_empty_tuple():
    assert accumulate_residuals() == ()
    assert accumulate_residuals(None) == ()
    assert accumulate_residuals((), ()) == ()


def test_strips_and_filters_blank_codes():
    assert accumulate_residuals(["", "  ", "a", "  b "]) == ("a", "b")


def test_no_erasure_every_input_appears():
    out = accumulate_residuals(["a", "b"], ["c"], ["b", "d"])
    assert out == ("a", "b", "c", "d")


def test_idempotent():
    v = ("a", "b", "c")
    assert accumulate_residuals(v, v) == accumulate_residuals(v)


def test_first_seen_order_preserved():
    out = accumulate_residuals(["c", "a", "b"], ["a", "d"])
    assert out == ("c", "a", "b", "d")


def test_associative_under_set_semantics():
    left_first = accumulate_residuals(
        accumulate_residuals(["a", "b"], ["c"]), ["d", "a"]
    )
    right_first = accumulate_residuals(["a", "b"], accumulate_residuals(["c"], ["d", "a"]))
    assert set(left_first) == set(right_first) == {"a", "b", "c", "d"}
