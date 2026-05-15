from __future__ import annotations

from mcd.cfk.cfk_proof_track import (
    CFK_LAYER_REGISTRY,
    CFK_TRANSITIONS,
    CFKTheoremStatus,
    DecisionLevel,
    EvidenceObject,
    EvidenceStrength,
    GateResult,
    ResidualObject,
    ResidualSeverity,
    ReverseTraceGraph,
    current_cfk_proof_obligations,
    evaluate_transition,
    propagate_residuals,
    resolve_cfk_theorem_status,
)
from mcd.cfk.cfk_pipeline import CognitiveFractalPipeline


def _gate_result(
    *,
    decision: DecisionLevel = DecisionLevel.HYPOTHESIS,
    evidence: list[EvidenceObject] | None = None,
    residual: list[ResidualObject] | None = None,
    reverse_trace_complete: bool = False,
    score_only_certificate: bool = False,
) -> GateResult:
    return GateResult(
        input={"text": "x"},
        candidate={"type": "claim"},
        constraint=["governance_contract"],
        evidence=evidence or [],
        residual=residual or [],
        ranking={"score": 0.95, "score_only_certificate": score_only_certificate},
        decision=decision,
        reverse_trace=ReverseTraceGraph(
            nodes=["a", "b"],
            edges=[("a", "b")],
            path_complete=reverse_trace_complete,
        ),
    )


def test_every_registered_layer_has_same_kernel_fields():
    expected = ("Input", "Candidate", "Constraint", "Evidence", "Residual", "Ranking", "Decision", "ReverseTrace")
    for layer in CFK_LAYER_REGISTRY.values():
        assert layer.gate_contract.kernel_fields == expected


def test_awareness_is_supervisory_meta_gate():
    assert CFK_LAYER_REGISTRY["Awareness"].awareness_meta_gate is True


def test_every_transition_returns_gate_result_shape():
    base = _gate_result()
    for transition in CFK_TRANSITIONS:
        out = evaluate_transition(transition, base)
        assert isinstance(out, GateResult)
        d = out.to_dict()
        for key in ("Input", "Candidate", "Constraint", "Evidence", "Residual", "Ranking", "Decision", "ReverseTrace"):
            assert key in d


def test_no_certificate_without_evidence_and_reverse_trace_and_non_blocking_residual():
    transition = CFK_TRANSITIONS[0]
    blocked = _gate_result(
        decision=DecisionLevel.CERTIFICATE,
        evidence=[],
        residual=[ResidualObject("r1", "evidence_gap", severity=ResidualSeverity.BLOCKING, blocking=True)],
        reverse_trace_complete=False,
    )
    out = evaluate_transition(transition, blocked)
    assert out.decision == DecisionLevel.HYPOTHESIS


def test_residuals_propagate_across_layers():
    prev = _gate_result(
        residual=[ResidualObject("r1", "evidence_gap", severity=ResidualSeverity.WARNING)],
    )
    cur = _gate_result()
    propagated = propagate_residuals(prev, cur)
    assert any(r.propagated_from == "r1" for r in propagated.residual)


def test_zero_in_path_does_not_mean_zero_globally():
    transition = CFK_TRANSITIONS[0]
    result = _gate_result(
        decision=DecisionLevel.ZERO,
        residual=[ResidualObject("r2", "zero_in_path", severity=ResidualSeverity.WARNING)],
    )
    out = evaluate_transition(transition, result)
    assert out.decision == DecisionLevel.HYPOTHESIS


def test_score_threshold_alone_cannot_issue_certificate():
    transition = CFK_TRANSITIONS[0]
    result = _gate_result(
        decision=DecisionLevel.CERTIFICATE,
        evidence=[
            EvidenceObject("e1", "src", strength=EvidenceStrength.STRONG, independent=True),
        ],
        reverse_trace_complete=True,
        score_only_certificate=True,
    )
    out = evaluate_transition(transition, result)
    assert out.decision == DecisionLevel.HYPOTHESIS


def test_theorem_status_domain_values_and_current_status():
    obligations = current_cfk_proof_obligations()
    status = resolve_cfk_theorem_status(obligations)
    allowed = {
        CFKTheoremStatus.INCOMPLETE,
        CFKTheoremStatus.HYPOTHESIS,
        CFKTheoremStatus.STRONG_HYPOTHESIS,
        CFKTheoremStatus.CERTIFICATE_CANDIDATE,
        CFKTheoremStatus.CERTIFICATE,
    }
    assert status in allowed
    assert status == CFKTheoremStatus.STRONG_HYPOTHESIS


def test_pipeline_exposes_theorem_status_and_scope_separation():
    result = CognitiveFractalPipeline().run("زيد كاتب")
    assert result.theorem_status == "STRONG_HYPOTHESIS"
    assert result.theorem_scope["pr_governance_domain"] == "closer_to_certificate"
    assert result.theorem_scope["unicode_to_awareness_theorem"] == "not_yet_certificate"

