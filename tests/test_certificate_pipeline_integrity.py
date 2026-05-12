from __future__ import annotations

from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.core.public_judgment import collapse_to_public_judgment
from mcd.governance import from_cfk_proof


def test_certificate_requires_evidence_gate():
    result = CognitiveFractalPipeline().run("النار حارة")
    record = from_cfk_proof(result.proof)
    if record.judgment == "certificate":
        assert result.proof.evidence_state != "missing"
        assert result.proof.reverse_trace_obj is not None
        assert result.proof.reverse_trace_obj.complete


def test_internal_suspend_collapses_to_public_hypothesis():
    result = CognitiveFractalPipeline().run("كل الشركات تستخدم هذه التقنية")
    public = collapse_to_public_judgment(result.proof.judgment)
    assert public in {"zero", "hypothesis", "certificate"}
    if result.proof.judgment == "suspend":
        assert public == "hypothesis"

