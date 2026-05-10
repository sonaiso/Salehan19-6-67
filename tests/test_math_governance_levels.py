from mcd.math_governance import ALL_LEVELS, get_level, next_level, previous_level, level_chain


def test_levels_defined():
    assert len(ALL_LEVELS) == 17
    assert get_level("L1_UNICODE") is not None
    assert get_level("unicode") is not None


def test_level_prev_next():
    assert previous_level("unicode").name == "reality"
    assert next_level("unicode").name == "grapheme"


def test_unicode_to_output_chain_has_morphisms():
    chain = level_chain()
    assert chain[1] == "unicode"
    assert chain[-2] == "final_answer"
