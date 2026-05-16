from mcd.math_governance import (
    ALL_LEVELS,
    get_level,
    next_level,
    previous_level,
    level_chain,
    canonical_level_for_interpretive,
    supported_interpretive_levels,
)


def test_levels_defined():
    assert len(ALL_LEVELS) == 17
    assert get_level("L0_RAW_TEXT") is not None
    assert get_level("unicode") is not None


def test_level_prev_next():
    assert previous_level("unicode").name == "raw_text"
    assert next_level("unicode").name == "grapheme"


def test_unicode_to_output_chain_has_morphisms():
    chain = level_chain()
    assert chain[1] == "unicode"
    assert chain[-2] == "proof_object"
    assert chain[-1] == "final_judgment"


def test_interpretive_levels_are_explicitly_supported():
    aliases = supported_interpretive_levels()
    assert "phoneme" in aliases
    assert "syllable" in aliases
    assert "wazn" in aliases


def test_interpretive_level_maps_to_canonical_runtime_level():
    assert canonical_level_for_interpretive("phoneme") == "grapheme"
    assert canonical_level_for_interpretive("syllable") == "orthographic_unit"
    assert canonical_level_for_interpretive("wazn") == "morphology"
