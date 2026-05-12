from __future__ import annotations

import pytest

from mcd.core.rank_calculus import (
    RankCalculationError,
    downgrade_judgment_for_residuals,
    enforce_judgment_rank,
    enforce_linking_rank,
)


def test_insufficient_rank_blocks_judgment() -> None:
    with pytest.raises(RankCalculationError, match="insufficient evidence rank"):
        enforce_judgment_rank("WEAK_EVIDENCE", "CERTIFICATE")


def test_evidence_rank_enforcement_works() -> None:
    enforce_judgment_rank("CERTIFICATE", "CERTIFICATE")
    enforce_linking_rank("EVIDENTIARY", "STRONG_EVIDENCE")


def test_forbidden_transition_rank_enforcement_for_governed_certification() -> None:
    with pytest.raises(RankCalculationError, match="GOVERNED_CERTIFICATION"):
        enforce_linking_rank("GOVERNED_CERTIFICATION", "STRONG_EVIDENCE")


def test_residuals_propagate_through_escalation_payload() -> None:
    from mcd.core.linking_contract import LinkingContract

    residuals = ["ambiguity:r1", "conflict:r2"]
    contract = LinkingContract(
        source="HYPOTHESIS",
        target="CERTIFICATE",
        linking_type="GOVERNED_CERTIFICATION",
        evidence_rank="CERTIFICATE",
        residuals=residuals,
        governance_passed=True,
        proof_object_ref="PO-10",
        trace_graph_ref="TG-10",
        reverse_trace_ref="RT-10",
    )

    payload = contract.apply()
    assert payload["effective_target"] == "HYPOTHESIS"
    assert payload["residuals"] == residuals
    assert payload["proof_object"]["residuals"] == residuals
    assert payload["trace_graph"]["residuals"] == residuals
    assert payload["reverse_trace"]["residuals"] == residuals


def test_downgrade_rule_with_uncertainty() -> None:
    assert downgrade_judgment_for_residuals("CERTIFICATE", ["r1"]) == "HYPOTHESIS"
    assert downgrade_judgment_for_residuals("HYPOTHESIS", ["r1"]) == "ZERO"
    assert downgrade_judgment_for_residuals("ZERO", ["r1"]) == "ZERO"
