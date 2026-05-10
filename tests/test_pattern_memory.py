"""Tests for PatternMemory."""
import pytest
from mcd.foldable_learning.pattern_memory import PatternMemory
from mcd.foldable_learning.fold_schema import FoldSignature
from mcd.foldable_learning.fold_signature import FoldSignatureRegistry
from mcd.residual_learning.residual_schema import CognitiveResidual


def _make_fold(fold_id, residual_types, recall_keys=None):
    return FoldSignature(
        fold_id=fold_id,
        residual_types=residual_types,
        recall_keys=recall_keys or residual_types,
    )


def test_pattern_memory_recalls_by_residual_type():
    mem = PatternMemory()
    f = _make_fold("FOLD-TEST", ["evidence_residual"])
    mem.add_fold_signature(f)
    results = mem.search_by_residual_type("evidence_residual")
    assert len(results) >= 1
    assert results[0].fold_id == "FOLD-TEST"


def test_search_by_domain():
    mem = PatternMemory()
    f = FoldSignature(fold_id="FOLD-MEDICAL", residual_types=["domain_residual"], domain_signature=["medical"], recall_keys=["domain_residual"])
    mem.add_fold_signature(f)
    results = mem.search_by_domain("medical")
    assert any(r.fold_id == "FOLD-MEDICAL" for r in results)


def test_search_by_graph_shape():
    mem = PatternMemory()
    f = _make_fold("FOLD-SHAPE", ["evidence_residual"])
    f.graph_shape = "claim + missing_source"
    mem.add_fold_signature(f)
    results = mem.search_by_graph_shape("missing_source")
    assert results


def test_recall_similar_case():
    mem = PatternMemory()
    for sig in FoldSignatureRegistry.all():
        mem.add_fold_signature(sig)
    r = CognitiveResidual(residual_id="r1", proposal_id="p1", residual_types=["evidence_residual"])
    results = mem.recall_similar_case(r)
    assert results


def test_export_memory():
    mem = PatternMemory()
    f = _make_fold("FOLD-EXPORT", ["metaphor_residual"])
    mem.add_fold_signature(f)
    exported = mem.export_memory()
    assert any(e["fold_id"] == "FOLD-EXPORT" for e in exported)


def test_memory_size():
    mem = PatternMemory()
    assert mem.size() == 0
    mem.add_fold_signature(_make_fold("F1", ["evidence_residual"]))
    assert mem.size() == 1
