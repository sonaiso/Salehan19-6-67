"""Tests for FoldUnfoldConsistencyChecker."""
import pytest
from mcd.foldable_learning.fold_unfold_consistency import FoldUnfoldConsistencyChecker
from mcd.foldable_learning.fold_signature import FoldSignatureRegistry


def test_fold_unfold_consistency_above_threshold():
    checker = FoldUnfoldConsistencyChecker()
    sigs = FoldSignatureRegistry.all()
    report = checker.check(sigs)
    assert report.fold_consistency_score >= 0.95


def test_all_registry_folds_pass():
    checker = FoldUnfoldConsistencyChecker()
    sigs = FoldSignatureRegistry.all()
    report = checker.check(sigs)
    assert report.failed_folds == 0


def test_report_has_total_folds():
    checker = FoldUnfoldConsistencyChecker()
    sigs = FoldSignatureRegistry.all()
    report = checker.check(sigs)
    assert report.total_folds == len(sigs)


def test_report_to_dict():
    checker = FoldUnfoldConsistencyChecker()
    sigs = FoldSignatureRegistry.all()
    report = checker.check(sigs)
    d = report.to_dict()
    assert "fold_consistency_score" in d
    assert "total_folds" in d


def test_report_to_markdown():
    checker = FoldUnfoldConsistencyChecker()
    sigs = FoldSignatureRegistry.all()
    report = checker.check(sigs)
    md = report.to_markdown()
    assert "Consistency Score" in md


def test_empty_fold_fails():
    from mcd.foldable_learning.fold_schema import FoldSignature
    checker = FoldUnfoldConsistencyChecker()
    bad_fold = FoldSignature(fold_id="FOLD-BAD", residual_types=[], recall_keys=[])
    report = checker.check([bad_fold])
    assert report.failed_folds > 0
    assert report.fold_consistency_score < 1.0
