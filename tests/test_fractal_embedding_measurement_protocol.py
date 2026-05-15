from __future__ import annotations

from mcd.evaluation.fractal_embedding_measurement_protocol import (
    LOCAL_ZERO_IN_PATH,
    REQUIRED_METRICS,
    DecisionGate,
    aggregate_global_status,
    build_ablation_specs,
    can_issue_certificate,
    compute_measurement_metrics,
    decide_status,
    justified_decision_probability,
)


def test_answer_probability_is_not_justified_decision_probability():
    gate = DecisionGate(
        evidence_present=False,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
        blocking_residual_present=False,
    )
    assert justified_decision_probability(0.99, gate) == 0.0


def test_score_alone_cannot_produce_certificate():
    gate = DecisionGate(
        evidence_present=False,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
    )
    assert decide_status(0.99, gate) != "CERTIFICATE"


def test_missing_evidence_blocks_certificate():
    gate = DecisionGate(
        evidence_present=False,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
    )
    assert can_issue_certificate(gate) is False


def test_missing_reverse_trace_blocks_certificate():
    gate = DecisionGate(
        evidence_present=True,
        reverse_trace_complete=False,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
    )
    assert can_issue_certificate(gate) is False


def test_blocking_residual_blocks_certificate():
    gate = DecisionGate(
        evidence_present=True,
        reverse_trace_complete=True,
        governance_gate_passed=True,
        proof_object_ref="PO-1",
        blocking_residual_present=True,
    )
    assert can_issue_certificate(gate) is False


def test_local_zero_in_path_does_not_become_global_zero():
    global_status = aggregate_global_status([LOCAL_ZERO_IN_PATH, "HYPOTHESIS"])
    assert global_status == "HYPOTHESIS"


def test_false_certificate_rate_metric_is_defined():
    metrics = compute_measurement_metrics(
        [
            {
                "issued_certificate": True,
                "certificate_justified": False,
                "decision_confidence": 0.9,
                "decision_correct": False,
            }
        ]
    )
    assert "false_certificate_rate" in metrics
    assert 0.0 <= metrics["false_certificate_rate"] <= 1.0
    assert set(REQUIRED_METRICS).issubset(metrics.keys())


def test_ablation_specs_include_required_governance_components():
    removed = {spec.removed_component for spec in build_ablation_specs()}
    assert {"Evidence", "Residual", "ReverseTrace", "CertificateGate"}.issubset(
        removed
    )
