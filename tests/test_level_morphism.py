import pytest
from mcd.fractal_kernel import LevelMorphism, LevelMorphismRegistry


def test_registry_has_default_morphisms():
    registry = LevelMorphismRegistry()
    morphisms = registry.get_all()
    assert len(morphisms) > 0


def test_find_unicode_to_grapheme():
    registry = LevelMorphismRegistry()
    m = registry.find("unicode", "grapheme")
    assert m is not None
    assert m.source_level == "unicode"


def test_validate_known_transition():
    registry = LevelMorphismRegistry()
    valid, warnings = registry.validate_transition("unicode", "grapheme")
    assert valid is True


def test_validate_unknown_transition():
    registry = LevelMorphismRegistry()
    valid, warnings = registry.validate_transition("unicode", "proof")
    assert valid is False
    assert len(warnings) > 0


def test_register_custom_morphism():
    registry = LevelMorphismRegistry()
    m = LevelMorphism("M-custom", "word", "judgment",
                      preserves=["trace"], allowed_loss=[])
    registry.register(m)
    assert registry.get("M-custom") is not None


def test_morphism_to_dict():
    m = LevelMorphism("M-test", "token", "word", preserves=["trace"])
    d = m.to_dict()
    assert d["morphism_id"] == "M-test"
    assert "trace" in d["preserves"]
