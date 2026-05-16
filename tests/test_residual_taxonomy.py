from __future__ import annotations

from mcd.core.residual_taxonomy import (
    ResidualFamily,
    ResidualSeverity,
    blocking_residuals,
    classify_residual,
    classify_residuals,
    has_blocking_residuals,
)


def test_classify_known_transition_condition_failed():
    spec = classify_residual("transition_condition_failed")

    assert spec.family is ResidualFamily.TRANSITION
    assert spec.severity is ResidualSeverity.BLOCKER
    assert spec.blocks_certificate is True
    assert spec.remediation_hint is not None


def test_classify_reason_code_alias_variant_phi_transition_condition_failed():
    spec = classify_residual("phi_transition_condition_failed")

    assert spec.family is ResidualFamily.TRANSITION
    assert spec.severity is ResidualSeverity.BLOCKER
    assert spec.blocks_certificate is True


def test_unknown_residual_defaults_to_blocker():
    spec = classify_residual("non_existing_reason_code")

    assert spec.family is ResidualFamily.UNKNOWN
    assert spec.severity is ResidualSeverity.BLOCKER
    assert spec.blocks_certificate is True


def test_certificate_allowed_is_non_blocking_info():
    spec = classify_residual("certificate_allowed")

    assert spec.family is ResidualFamily.CERTIFICATE
    assert spec.severity is ResidualSeverity.INFO
    assert spec.blocks_certificate is False


def test_has_blocking_residuals_mixed_codes():
    codes = ["certificate_allowed", "transition_condition_unknown"]
    assert has_blocking_residuals(codes) is True


def test_blocking_residuals_filters_non_blocking_codes():
    specs = blocking_residuals(["certificate_allowed", "certificate_without_proof_object"])
    assert [spec.code for spec in specs] == ["certificate_without_proof_object"]


def test_classify_residuals_preserves_input_order():
    specs = classify_residuals(["certificate_allowed", "silent_level_skip"])
    assert [spec.code for spec in specs] == ["certificate_allowed", "silent_level_skip"]
