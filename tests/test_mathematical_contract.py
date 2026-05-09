"""Tests for check_mathematical_contract."""
from mcd.curriculum.cognitive_graph import CognitiveGraph
from mcd.curriculum.cognitive_node import CognitiveNode
from mcd.curriculum.mathematical_contract import check_mathematical_contract, MathematicalContractResult

def _empty_graph():
    return CognitiveGraph(graph_id="g", evidence_status="sufficient", certainty_policy="certain_knowledge")

def _node(nid, ntype="thing"):
    return CognitiveNode(node_id=nid, surface=nid, normalized=nid, node_type=ntype)

def test_empty_graph_fails():
    r = check_mathematical_contract(_empty_graph())
    assert not r.passed

def test_graph_with_nodes_passes_basic():
    g = CognitiveGraph(graph_id="g", nodes=[_node("n1")], evidence_status="sufficient", certainty_policy="certain_knowledge")
    r = check_mathematical_contract(g)
    assert isinstance(r, MathematicalContractResult)

def test_result_to_dict():
    r = check_mathematical_contract(_empty_graph())
    d = r.to_dict()
    assert "passed" in d and "score" in d

def test_score_between_0_and_1():
    r = check_mathematical_contract(_empty_graph())
    assert 0.0 <= r.score <= 1.0

def test_near_certainty_without_evidence_violation():
    g = CognitiveGraph(graph_id="g", nodes=[_node("n1")], evidence_status="insufficient", certainty_policy="near_certainty")
    r = check_mathematical_contract(g)
    assert any("near_certainty" in v or "evidence" in v for v in r.violations)
