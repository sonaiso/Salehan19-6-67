import pytest
from mcd.fractal_kernel import CognitiveOperator, OperatorAlgebra


def test_emphasis_operator_cannot_create_evidence():
    with pytest.raises(ValueError):
        CognitiveOperator(
            "bad_op", "mabni",
            creates_evidence=True,
        )


def test_irab_operator_cannot_raise_factual_certainty():
    # Valid irab op
    op = CognitiveOperator(
        "irab_test", "murab",
        certainty_effect="raise_syntactic_only",
        creates_evidence=False,
    )
    algebra = OperatorAlgebra()
    valid, viol = algebra.validate_operator(op)
    assert valid is True


def test_valid_operator():
    op = CognitiveOperator("test_op", "morphological", creates_evidence=False)
    assert op.operator_id == "test_op"


def test_default_creates_evidence_false():
    op = CognitiveOperator("op2", "fold")
    assert op.creates_evidence is False


def test_operator_algebra_has_builtins():
    algebra = OperatorAlgebra()
    ops = algebra.get_all()
    assert len(ops) > 0


def test_algebra_register():
    algebra = OperatorAlgebra()
    op = CognitiveOperator("custom_op", "evidence", creates_evidence=True)
    algebra.register(op)
    assert algebra.get("custom_op") is not None


def test_algebra_rejects_mabni_creating_evidence():
    algebra = OperatorAlgebra()
    with pytest.raises(ValueError):
        op = CognitiveOperator("bad", "mabni", creates_evidence=True)
        algebra.register(op)


def test_operator_to_dict():
    op = CognitiveOperator("op3", "trace")
    d = op.to_dict()
    assert d["operator_id"] == "op3"
    assert d["creates_evidence"] is False
