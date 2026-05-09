"""Tests for validate_graph."""
from mcd.curriculum.cognitive_graph import CognitiveGraph
from mcd.curriculum.cognitive_node import CognitiveNode
from mcd.curriculum.graph_validator import validate_graph, GraphValidationResult

def _node(nid): return CognitiveNode(node_id=nid, surface=nid, normalized=nid, node_type="thing")
def _g(**kw): return CognitiveGraph(graph_id="g", evidence_status="sufficient", certainty_policy="certain_knowledge", **kw)

def test_empty_graph_fails():
    r = validate_graph(_g())
    assert not r.passed

def test_returns_result_instance():
    r = validate_graph(_g())
    assert isinstance(r, GraphValidationResult)

def test_to_dict_has_passed():
    r = validate_graph(_g())
    assert "passed" in r.to_dict()

def test_score_between_0_and_1():
    r = validate_graph(_g())
    assert 0.0 <= r.score <= 1.0

def test_graph_with_nodes_no_root_vector():
    g = _g(nodes=[_node("n1")])
    r = validate_graph(g)
    assert not r.passed or any("root_vector" in v for v in r.violations)
