"""Tests for InvariantValidator."""
from mcd.curriculum.cognitive_graph import CognitiveGraph
from mcd.curriculum.cognitive_edge import CognitiveEdge
from mcd.curriculum.cognitive_node import CognitiveNode
from mcd.curriculum.invariant_validator import validate_invariants, InvariantValidationResult

def _g(**kw): return CognitiveGraph(graph_id="g", evidence_status="sufficient", certainty_policy="certain_knowledge", **kw)
def _node(nid): return CognitiveNode(node_id=nid, surface=nid, normalized=nid, node_type="thing")

def test_returns_result_instance():
    r = validate_invariants(_g())
    assert isinstance(r, InvariantValidationResult)

def test_pass_rate_between_0_and_1():
    r = validate_invariants(_g())
    assert 0.0 <= r.pass_rate <= 1.0

def test_to_dict_keys():
    r = validate_invariants(_g())
    d = r.to_dict()
    assert "passed" in d

def test_empty_graph_result():
    r = validate_invariants(_g(), has_graph_nodes=False)
    assert isinstance(r, InvariantValidationResult)


def test_cause_has_effect_requires_matching_caused_by_pair():
    g = _g(
        nodes=[_node("cause"), _node("mid"), _node("other")],
        edges=[
            CognitiveEdge(edge_id="e1", source="cause", relation="causes", target="mid"),
            CognitiveEdge(edge_id="e2", source="mid", relation="caused_by", target="other"),
        ],
    )
    r = validate_invariants(g)
    assert any(v.invariant_id == "INV-003" for v in r.violations)
