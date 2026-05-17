from __future__ import annotations

from pathlib import Path

from mcd.core.public_judgment import enforce_governed_output_contract
from mcd.llm_proposer import trace as trace_module
from mcd.llm_proposer.governor import AFJGGovernor
from mcd.llm_proposer.pipeline import GovernedProposalPipeline
from mcd.llm_proposer.providers.echo import EchoProposer


def test_saved_artifact_is_replay_audit_not_proof_authority(tmp_path: Path) -> None:
    pipeline = GovernedProposalPipeline(EchoProposer(), AFJGGovernor())
    answer = pipeline.run(
        "claim",
        evidence=["evidence"],
        reverse_trace=["raw_text_units: claim"],
    )
    artifact_path = trace_module.save(answer, base_dir=tmp_path)
    artifact = trace_module.load(artifact_path)
    assert artifact["artifact_role"] == "audit_replay_artifact"

    governed = enforce_governed_output_contract(
        {
            "judgment": "certificate",
            "proof_object_ref": "",
            "governance_gate_passed": True,
            "reverse_trace_obj": {"complete": True, "raw_text_units": ["claim"]},
            "residuals": [],
            "artifact_path": str(artifact_path),
        }
    )
    assert governed["judgment"] == "hypothesis"
    assert "certificate_without_proof_object" in governed["residuals"]
