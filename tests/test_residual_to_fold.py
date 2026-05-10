"""Tests for ResidualToFoldConverter."""
import pytest
from mcd.foldable_learning.residual_to_fold import ResidualToFoldConverter
from mcd.residual_learning.residual_schema import CognitiveResidual


def _make_residual(types, severity="medium"):
    return CognitiveResidual(residual_id="r1", proposal_id="p1", residual_types=types, severity=severity)


def test_residual_converts_to_fold_signature():
    conv = ResidualToFoldConverter()
    r = _make_residual(["evidence_residual"])
    fold = conv.convert(r)
    assert fold.fold_id


def test_fold_signature_has_recall_keys():
    conv = ResidualToFoldConverter()
    r = _make_residual(["unsupported_generalization_residual"])
    fold = conv.convert(r)
    assert fold.recall_keys


def test_fold_signature_has_unfold_plan():
    conv = ResidualToFoldConverter()
    r = _make_residual(["gpt_as_evidence_residual"])
    fold = conv.convert(r)
    assert fold.unfold_plan


def test_gpt_as_evidence_maps_to_correct_fold():
    conv = ResidualToFoldConverter()
    r = _make_residual(["gpt_as_evidence_residual"])
    fold = conv.convert(r)
    assert fold.fold_id == "FOLD-GPT-AS-EVIDENCE"


def test_harm_haram_maps_to_correct_fold():
    conv = ResidualToFoldConverter()
    r = _make_residual(["harm_haram_residual"])
    fold = conv.convert(r)
    assert fold.fold_id == "FOLD-HARM-HARAM"


def test_batch_convert():
    conv = ResidualToFoldConverter()
    residuals = [_make_residual(["evidence_residual"]) for _ in range(5)]
    folds = conv.batch_convert(residuals)
    assert len(folds) == 5


def test_fold_severity_preserved():
    conv = ResidualToFoldConverter()
    r = _make_residual(["harm_haram_residual"], severity="blocking")
    fold = conv.convert(r)
    assert fold.severity == "blocking"
