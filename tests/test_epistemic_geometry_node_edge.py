from mcd.epistemic_geometry import MinimalFractalEdge, MinimalFractalNode
from mcd.epistemic_geometry.validators import (
    validate_edge_morphism,
    validate_gate_score_separation,
    validate_no_silent_skip,
    validate_node_minimum_completeness,
)


def _base_node(**kwargs) -> MinimalFractalNode:
    defaults = dict(
        node_id="node-1",
        rank=1,
        node_type="claim",
        domain="factual",
        gates={"existence": 1},
        scores={"existence": 0.8},
        trace_refs=["t-1"],
        residuals=[],
        relations=[],
        incoming_edges=[],
        outgoing_edges=[],
        allowed_next=[],
        forbidden_transitions=[],
    )
    defaults.update(kwargs)
    return MinimalFractalNode(**defaults)


def _base_edge(**kwargs) -> MinimalFractalEdge:
    defaults = dict(
        edge_id="edge-1",
        source_node="node-1",
        target_node="node-2",
        morphism_id="morph-1",
        relation_type="trace",
        preserves=["trace"],
        adds=[],
        forbids=[],
        gate_requirements={"existence": 1},
        score_effects={"existence": 0.0},
        residual_policy={"mode": "preserve"},
        trace_policy={"mode": "preserve"},
    )
    defaults.update(kwargs)
    return MinimalFractalEdge(**defaults)


def test_node_requires_gate():
    node = _base_node(gates={})
    assert "node_requires_gate" in validate_node_minimum_completeness(node)


def test_node_requires_trace_or_domain_missing_residual():
    node = _base_node(domain="", trace_refs=[], residuals=[])
    violations = validate_node_minimum_completeness(node)
    assert "node_requires_trace_refs" in violations
    assert "node_requires_domain_or_domain_missing_residual" in violations


def test_edge_requires_morphism():
    edge = _base_edge(morphism_id="")
    assert "edge_requires_morphism" in validate_edge_morphism(edge)


def test_edge_requires_relation_type():
    edge = _base_edge(relation_type="")
    assert "edge_requires_relation_type" in validate_edge_morphism(edge)


def test_gate_is_boolean():
    node = _base_node(gates={"existence": 2}, scores={"existence": 0.5})
    assert "gate_not_boolean:existence" in validate_gate_score_separation(node)


def test_score_is_decimal_between_zero_and_one():
    node = _base_node(scores={"existence": 1.5})
    assert "score_out_of_range:existence" in validate_gate_score_separation(node)


def test_score_never_opens_gate():
    node = _base_node(gates={"existence": 0}, scores={"existence": 0.9})
    assert "score_cannot_open_gate:existence" in validate_gate_score_separation(node)


def test_edge_cannot_erase_residual():
    edge = _base_edge(residual_policy={"erase": "silent"})
    assert "edge_cannot_erase_residual" in validate_edge_morphism(edge)


def test_no_silent_level_skip():
    edge = _base_edge(level_step=2)
    assert "no_silent_level_skip" in validate_no_silent_skip(edge)


def test_no_certificate_from_node_alone():
    node = _base_node(judgment="CERTIFICATE")
    assert "no_certificate_from_node_alone" in validate_node_minimum_completeness(node)

