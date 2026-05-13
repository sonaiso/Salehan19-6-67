from __future__ import annotations

from types import SimpleNamespace

from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline
from mcd.coding_copilot.coding_judgment import CodingJudgment
from mcd.coding_copilot.coding_status import CodingStatus
from mcd.coding_copilot.issue_understanding import IssueUnderstanding
from mcd.coding_copilot.patch_artifact import PatchArtifact
from mcd.coding_copilot.patch_plan import PatchPlan
from mcd.coding_copilot.repo_context import RepoContextMap
from mcd.fractal_kernel.proof_object import ProofObject as FractalProofObject
from mcd.governance import from_cfk_proof, from_coding_judgment, from_fractal_kernel_proof


def test_cross_runtime_judgments_collapse_to_public_triad():
    cfk = CognitiveFractalPipeline().run("كل الشركات تستخدم هذه التقنية")
    cfk_record = from_cfk_proof(cfk.proof)
    fractal_record = from_fractal_kernel_proof(
        FractalProofObject(
            proof_id="P-1",
            claim_id="C-1",
            proof_status="hypothesis",
        )
    )
    coding_record = from_coding_judgment(
        CodingJudgment(
            judgment_id="CJ-1",
            issue=IssueUnderstanding(issue_id="ISS-1", raw_text="doc", task_type="docs", requested_behavior="x", observed_behavior=""),
            repo_context=RepoContextMap(repo_snapshot_id="R1", relevant_files=["README.md"]),
            claims=[],
            patch_plan=PatchPlan(plan_id="PP-1", claims=[], steps=["s"], expected_tests=[], rollback_plan="r"),
            patch_artifact=PatchArtifact(
                patch_id="PA-1",
                changed_files=["README.md"],
                additions=1,
                deletions=0,
                touched_layers=["docs"],
                declared_reason="docs",
                linked_claims={},
            ),
            final_judgment=CodingStatus.HYPOTHESIS.value,
        )
    )
    for record in (cfk_record, fractal_record, coding_record):
        assert record.judgment in {"zero", "hypothesis", "certificate"}


def test_cross_runtime_governance_record_has_canonical_fields():
    cfk = CognitiveFractalPipeline().run("النار حارة", evidence_refs=["e1", "e2"])
    record = from_cfk_proof(cfk.proof).to_dict()
    assert set(record.keys()) == {
        "runtime",
        "judgment",
        "proof_object_ref",
        "governance_gate_passed",
        "reverse_trace_ref",
        "trace_graph_ref",
        "legitimacy_state",
        "rank_calculus_state",
        "residuals",
    }


def test_cfk_adapter_preserves_existing_residuals():
    proof = SimpleNamespace(
        judgment="hypothesis",
        proof_id="PO-42",
        conservation=SimpleNamespace(passed=True),
        reverse_trace_obj=SimpleNamespace(reverse_trace_id="RT-42", blocking_violations=[]),
        residual_type="none",
        residuals=["certificate_blocked", "reverse_trace_missing"],
    )
    record = from_cfk_proof(proof)
    assert "certificate_blocked" in record.residuals
    assert "reverse_trace_missing" in record.residuals
