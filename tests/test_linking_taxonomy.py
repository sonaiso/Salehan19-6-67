from __future__ import annotations

import pytest

from mcd.core.linking_contract import LinkingContract, LinkingContractError
from mcd.core.linking_type import LinkingType, certificate_eligible


def test_linking_types_include_required_categories() -> None:
    expected = {
        "SYMBOLIC",
        "SEMANTIC",
        "CONTEXTUAL",
        "CAUSAL",
        "INTERPRETIVE",
        "EVIDENTIARY",
        "GOVERNED_CERTIFICATION",
    }
    assert {item.name for item in LinkingType} == expected


def test_semantic_link_cannot_certify() -> None:
    contract = LinkingContract(
        source="HYPOTHESIS",
        target="CERTIFICATE",
        linking_type="SEMANTIC",
        evidence_rank="CERTIFICATE",
        governance_passed=True,
        proof_object_ref="PO-1",
        trace_graph_ref="TG-1",
        reverse_trace_ref="RT-1",
    )
    with pytest.raises(LinkingContractError, match="SEMANTIC_LINK"):
        contract.apply()


def test_interpretive_link_cannot_escalate_to_certificate() -> None:
    contract = LinkingContract(
        source="HYPOTHESIS",
        target="CERTIFICATE",
        linking_type="INTERPRETIVE",
        evidence_rank="CERTIFICATE",
        governance_passed=True,
        proof_object_ref="PO-1",
        trace_graph_ref="TG-1",
        reverse_trace_ref="RT-1",
    )
    with pytest.raises(LinkingContractError, match="INTERPRETATION"):
        contract.apply()


def test_certificate_eligibility_only_for_governed_certification() -> None:
    assert certificate_eligible("GOVERNED_CERTIFICATION")
    assert not certificate_eligible("EVIDENTIARY")


def test_forbidden_zero_to_certificate_transition_raises() -> None:
    contract = LinkingContract(
        source="ZERO",
        target="CERTIFICATE",
        linking_type="GOVERNED_CERTIFICATION",
        evidence_rank="CERTIFICATE",
        governance_passed=True,
        proof_object_ref="PO-1",
        trace_graph_ref="TG-1",
        reverse_trace_ref="RT-1",
    )
    with pytest.raises(LinkingContractError, match="ZERO -> CERTIFICATE"):
        contract.apply()
