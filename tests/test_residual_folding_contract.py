import pytest
from mcd.fractal_kernel import GPTResidualFoldingContract, RESIDUAL_TYPES, LEARNING_ACTIONS


def make_contract(**kwargs):
    defaults = dict(
        proposal_unit_id="PROP-001",
        contract_projection_unit_id="PROJ-001",
        residual_unit_id="RES-001",
        residual_types=["missing_evidence"],
        learning_actions=["add_test"],
        proof_effect="none",
    )
    defaults.update(kwargs)
    return GPTResidualFoldingContract(**defaults)


def test_gpt_residual_contract_never_treats_gpt_as_evidence():
    assert GPTResidualFoldingContract.gpt_is_not_evidence() is True


def test_gpt_cannot_raise_certainty():
    assert GPTResidualFoldingContract.gpt_cannot_raise_certainty() is True


def test_valid_contract():
    c = make_contract()
    assert c.proof_effect == "none"


def test_certificate_proof_effect_raises():
    with pytest.raises(ValueError):
        make_contract(proof_effect="certificate")


def test_invalid_residual_type_raises():
    with pytest.raises(ValueError):
        make_contract(residual_types=["unknown_type_xyz"])


def test_invalid_learning_action_raises():
    with pytest.raises(ValueError):
        make_contract(learning_actions=["do_magic"])


def test_contract_to_dict():
    c = make_contract()
    d = c.to_dict()
    assert d["proof_effect"] == "none"
    assert "missing_evidence" in d["residual_types"]


def test_all_valid_residual_types():
    for rt in RESIDUAL_TYPES:
        c = make_contract(residual_types=[rt])
        assert rt in c.residual_types
