"""Tests for Phase 8 CFK schema (CognitiveFractalUnit and related schemas)."""
from __future__ import annotations

import pytest
from mcd.cfk.cfk_schema import (
    CognitiveFractalUnit,
    KernelProjection,
    JudgmentStatus,
    CoordinateType,
    NodeInfo,
    VectorInfo,
    RelationsInfo,
    OperatorsInfo,
    EvidenceInfo,
    CertaintyInfo,
    ProofInfo,
    TraceInfo,
    ResidualInfo,
)


class TestNodeInfo:
    def test_to_dict(self):
        n = NodeInfo(node_id="N1", level="word", surface="كاتب", unit_type="word")
        d = n.to_dict()
        assert d["node_id"] == "N1"
        assert d["level"] == "word"
        assert d["surface"] == "كاتب"
        assert d["language_origin"] == "arabic"

    def test_default_language_origin(self):
        n = NodeInfo(node_id="x", level="claim", surface="test", unit_type="claim")
        assert n.language_origin == "arabic"

    def test_custom_language_origin(self):
        n = NodeInfo(node_id="x", level="claim", surface="test", unit_type="claim", language_origin="statistical")
        assert n.language_origin == "statistical"


class TestVectorInfo:
    def test_defaults(self):
        v = VectorInfo()
        assert v.statistical_weight == 0.5
        assert v.semantic_weight == 0.5
        assert v.epistemic_weight == 0.5

    def test_to_dict_rounds(self):
        v = VectorInfo(statistical_weight=0.333333)
        d = v.to_dict()
        assert len(str(d["statistical_weight"])) <= 8  # rounded to 4 decimals


class TestEvidenceInfo:
    def test_defaults(self):
        e = EvidenceInfo()
        assert e.evidence_state == "missing"
        assert e.source_trust == 0.0

    def test_to_dict(self):
        e = EvidenceInfo(evidence_state="present", evidence_refs=["ref1"])
        d = e.to_dict()
        assert d["evidence_state"] == "present"
        assert "ref1" in d["evidence_refs"]


class TestCertaintyInfo:
    def test_defaults(self):
        c = CertaintyInfo()
        assert c.epistemic_certainty == 0.0
        assert c.certainty_level == "hypothesis"
        assert c.coordinate_type == "epistemic"

    def test_to_dict(self):
        c = CertaintyInfo(statistical_confidence=0.9, linguistic_force="emphasis")
        d = c.to_dict()
        assert d["linguistic_force"] == "emphasis"
        assert d["statistical_confidence"] == 0.9


class TestCognitiveFractalUnit:
    def test_make(self):
        unit = CognitiveFractalUnit.make("كاتب")
        assert unit.surface == "كاتب"
        assert unit.unit_id.startswith("CFU-")
        assert unit.N.surface == "كاتب"

    def test_to_dict_has_all_nine_dimensions(self):
        unit = CognitiveFractalUnit.make("كاتب")
        d = unit.to_dict()
        for dim in ("N", "V", "R", "O", "E", "C", "P", "T", "Z"):
            assert dim in d, f"Missing dimension {dim}"

    def test_to_dict_source_text(self):
        unit = CognitiveFractalUnit.make("كاتب", source_text="زيد كاتب")
        d = unit.to_dict()
        assert d["source_text"] == "زيد كاتب"

    def test_unique_ids(self):
        u1 = CognitiveFractalUnit.make("كاتب")
        u2 = CognitiveFractalUnit.make("كاتب")
        assert u1.unit_id != u2.unit_id


class TestKernelProjection:
    def test_to_dict(self):
        unit = CognitiveFractalUnit.make("test")
        proj = KernelProjection(
            projection_id="KP-1",
            coordinate_type=CoordinateType.STATISTICAL.value,
            unit=unit,
            comparable_score=0.75,
            judgment=JudgmentStatus.HYPOTHESIS.value,
        )
        d = proj.to_dict()
        assert d["projection_id"] == "KP-1"
        assert d["coordinate_type"] == "statistical"
        assert d["comparable_score"] == 0.75
        assert d["judgment"] == "hypothesis"

    def test_comparable_score_rounded(self):
        unit = CognitiveFractalUnit.make("test")
        proj = KernelProjection(
            projection_id="KP-1",
            coordinate_type="statistical",
            unit=unit,
            comparable_score=0.123456789,
        )
        d = proj.to_dict()
        assert d["comparable_score"] == 0.1235


class TestJudgmentStatus:
    def test_all_values(self):
        assert JudgmentStatus.CERTIFICATE.value == "certificate"
        assert JudgmentStatus.HYPOTHESIS.value == "hypothesis"
        assert JudgmentStatus.SUSPEND.value == "suspend"
        assert JudgmentStatus.ZERO.value == "zero"


class TestCoordinateType:
    def test_all_values(self):
        assert CoordinateType.STATISTICAL.value == "statistical"
        assert CoordinateType.ARABIC.value == "arabic"
        assert CoordinateType.EPISTEMIC.value == "epistemic"
