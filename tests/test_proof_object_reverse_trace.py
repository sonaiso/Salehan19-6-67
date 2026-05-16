import pytest
from mcd.fractal_kernel import ProofObject, ReverseTrace, PROOF_STATUSES


def test_hypothesis_proof_valid():
    rtrace_id = ReverseTrace.make_id()
    proof = ProofObject(
        proof_id=ProofObject.make_id(),
        claim_id="CLAIM-001",
        proof_status="hypothesis",
        reverse_trace_id=rtrace_id,
    )
    assert proof.proof_status == "hypothesis"


def test_certificate_requires_evidence():
    with pytest.raises(ValueError):
        ProofObject(
            proof_id="P1", claim_id="C1",
            proof_status="certificate",
            evidence_refs=[],
            reverse_trace_id="RT-001",
        )


def test_certificate_cannot_have_blockers():
    with pytest.raises(ValueError):
        ProofObject(
            proof_id="P1", claim_id="C1",
            proof_status="certificate",
            evidence_refs=["E1"],
            blockers=["B1"],
            reverse_trace_id="RT-001",
        )


def test_proof_object_requires_reverse_trace_for_certificate():
    with pytest.raises(ValueError):
        ProofObject(
            proof_id="P1", claim_id="C1",
            proof_status="certificate",
            evidence_refs=["E1"],
            reverse_trace_id=None,
        )


def test_zero_proof():
    proof = ProofObject(proof_id="P1", claim_id="C1", proof_status="zero")
    assert proof.proof_status == "zero"


def test_valid_certificate():
    rtrace_id = ReverseTrace.make_id()
    proof = ProofObject(
        proof_id=ProofObject.make_id(),
        claim_id="C1",
        proof_status="certificate",
        evidence_refs=["E1", "E2"],
        reverse_trace_id=rtrace_id,
    )
    assert proof.proof_status == "certificate"


def test_reverse_trace_to_dict():
    rt = ReverseTrace(
        reverse_trace_id=ReverseTrace.make_id(),
        final_claim="النار حارة",
        proof_id="P1",
        complete=True,
    )
    d = rt.to_dict()
    assert d["final_claim"] == "النار حارة"
    assert d["complete"] is True


def test_reverse_trace_exposes_unified_layer_channels():
    rt = ReverseTrace(
        reverse_trace_id=ReverseTrace.make_id(),
        final_claim="النار حارة",
        proof_id="P1",
    )
    d = rt.to_dict()
    for key in (
        "grapheme_units",
        "orthographic_units",
        "lexeme_units",
        "morphology_units",
        "phrase_units",
        "clause_units",
        "paragraph_units",
        "section_units",
        "full_text_units",
        "discourse_graph_units",
        "claim_graph_units",
        "proof_object_units",
        "final_judgment_units",
    ):
        assert key in d


def test_proof_to_dict():
    proof = ProofObject(proof_id="P1", claim_id="C1", proof_status="zero")
    d = proof.to_dict()
    assert d["proof_status"] == "zero"
