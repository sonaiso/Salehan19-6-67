from __future__ import annotations

from mcd.llm_proposer.governed_payload import from_governed_payload, to_governed_payload
from mcd.llm_proposer.types import GovernedAnswer, Proposal


def test_core_governance_can_downgrade_certificate() -> None:
    proposal = Proposal(prompt="claim", raw_text="claim", provider="echo", model="echo-v1")
    answer = GovernedAnswer(
        proposal=proposal,
        verdict="CERTIFICATE",
        evidence=["evidence"],
        reverse_trace=["raw_text_units: claim"],
        violated_rules=[],
    )
    payload = to_governed_payload(
        answer,
        governance_gate_passed=False,
        proof_object_ref="PO-1",
        reverse_trace_obj={"complete": True, "raw_text_units": ["claim"]},
    )
    downgraded = from_governed_payload(payload, proposal=proposal)
    assert payload["judgment"] == "hypothesis"
    assert "certificate_without_governance_gate" in payload["residuals"]
    assert downgraded.verdict == "HYPOTHESIS"
