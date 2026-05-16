from mcd.math_governance import TransitionInput, phi_transition


def _payload(condition):
    return TransitionInput(
        U="0*",
        P="token[0]",
        L="left_context",
        R="right_context",
        G="token_to_lexeme",
        C=condition,
        W=["witness-1"],
        X={"context": "sample"},
    )


def test_phi_transition_suspended_when_condition_unknown():
    out = phi_transition(_payload(None))
    assert out.judgment == "suspended"
    assert out.known == 0
    assert out.passed == 0
    assert "transition_condition_unknown" in out.residuals


def test_phi_transition_blocked_when_condition_fails():
    out = phi_transition(_payload(False))
    assert out.judgment == "blocked"
    assert out.known == 1
    assert out.passed == 0
    assert "transition_condition_failed" in out.residuals


def test_phi_transition_allowed_when_condition_passes():
    out = phi_transition(_payload(True))
    assert out.judgment == "allowed"
    assert out.known == 1
    assert out.passed == 1
    assert out.residuals == []
