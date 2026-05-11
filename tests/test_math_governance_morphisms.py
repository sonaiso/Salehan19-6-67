from mcd.math_governance import LevelMorphismRegistry


def test_no_transition_without_morphism():
    reg = LevelMorphismRegistry()
    ok, msgs = reg.validate_transition("unicode", "proof_object")
    assert ok is False
    assert msgs


def test_morphism_preserves_trace():
    reg = LevelMorphismRegistry()
    ok, msgs = reg.validate_transition("unicode", "grapheme")
    assert ok is True
    assert not msgs


def test_morphism_cannot_create_evidence():
    reg = LevelMorphismRegistry()
    ok, msgs = reg.validate_effects("unicode_to_grapheme", create_evidence=True)
    assert ok is False
    assert any("create evidence" in m.lower() for m in msgs)


def test_morphism_cannot_issue_certificate():
    reg = LevelMorphismRegistry()
    ok, msgs = reg.validate_effects("unicode_to_grapheme", issue_certificate=True)
    assert ok is False
    assert any("certificate" in m.lower() for m in msgs)
