import pytest

from mcd.math_governance import CognitiveOperator, OperatorAlgebra


def test_operator_identity():
    op = OperatorAlgebra.identity("token")
    assert op.operator_type == "identity"


def test_operator_associativity():
    a = CognitiveOperator("a", "morphosemantic")
    b = CognitiveOperator("b", "mabni")
    c = CognitiveOperator("c", "murab")
    assert OperatorAlgebra.validate_associativity(a, b, c) is True


def test_emphasis_operator_not_evidence():
    with pytest.raises(ValueError):
        CognitiveOperator("bad", "mabni", creates_evidence=True)


def test_murab_operator_not_factual_certainty():
    op = CognitiveOperator("murab", "murab", certainty_effect="syntactic_only")
    assert op.certainty_effect == "syntactic_only"


def test_mushtaq_operator_not_event_proof():
    op = CognitiveOperator("mushtaq", "mushtaq")
    assert op.can_issue_certificate is False


def test_gpt_operator_not_evidence():
    op = CognitiveOperator("gpt", "gpt")
    assert op.creates_evidence is False
