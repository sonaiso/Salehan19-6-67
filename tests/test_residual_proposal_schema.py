"""Tests for GPTProposal and ProposalGraph schema."""
from __future__ import annotations

import pytest
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalGraph, ProposalType
from mcd.residual_learning.proposal_parser import ProposalParser


def make_proposal(
    pid: str = "test-001",
    input_text: str = "هل هذا صحيح؟",
    gpt_output: str = "نعم هذا صحيح.",
    proposal_type: str = "answer",
    claimed_evidence: list[str] | None = None,
    claimed_certainty: str | None = None,
    metadata: dict | None = None,
) -> GPTProposal:
    return GPTProposal(
        proposal_id=pid,
        input_text=input_text,
        gpt_output=gpt_output,
        proposal_type=ProposalType(proposal_type),
        claimed_evidence=claimed_evidence or [],
        claimed_certainty=claimed_certainty,
        metadata=metadata or {},
    )


class TestGPTProposalSchema:
    def test_basic_creation(self) -> None:
        p = make_proposal()
        assert p.proposal_id == "test-001"
        assert p.proposal_type == ProposalType.ANSWER

    def test_to_dict_roundtrip(self) -> None:
        p = make_proposal(claimed_evidence=["source1"])
        d = p.to_dict()
        p2 = GPTProposal.from_dict(d)
        assert p2.proposal_id == p.proposal_id
        assert p2.claimed_evidence == ["source1"]

    def test_proposal_type_values(self) -> None:
        for pt in ProposalType:
            p = make_proposal(proposal_type=pt.value)
            assert p.proposal_type == pt

    def test_gpt_output_is_not_evidence(self) -> None:
        """GPT output field exists but is never treated as evidence."""
        p = make_proposal(gpt_output="GPT says X is true")
        assert "gpt_output" in p.to_dict()
        # claimed_evidence is separate — GPT text is NOT in claimed_evidence
        assert p.gpt_output not in p.claimed_evidence

    def test_from_dict_unknown_proposal_type_defaults_to_answer(self) -> None:
        d = {
            "proposal_id": "x",
            "input_text": "test",
            "gpt_output": "output",
            "proposal_type": "unknown_type",
        }
        p = GPTProposal.from_dict(d)
        assert p.proposal_type == ProposalType.ANSWER


class TestProposalGraph:
    def test_graph_creation(self) -> None:
        graph = ProposalGraph(graph_id="g1")
        assert graph.graph_id == "g1"
        assert graph.nodes == []
        assert graph.edges == []

    def test_graph_to_dict(self) -> None:
        graph = ProposalGraph(graph_id="g1", certainty_policy="suspend_judgment")
        d = graph.to_dict()
        assert d["certainty_policy"] == "suspend_judgment"

    def test_node_ids(self) -> None:
        from mcd.residual_learning.proposal_schema import ProposalCognitiveNode
        n1 = ProposalCognitiveNode(node_id="n1", surface="test", node_type="claim")
        n2 = ProposalCognitiveNode(node_id="n2", surface="test2", node_type="evidence")
        graph = ProposalGraph(graph_id="g1", nodes=[n1, n2])
        assert graph.node_ids() == {"n1", "n2"}


class TestProposalParser:
    def setup_method(self) -> None:
        self.parser = ProposalParser()

    def test_parse_simple_proposal(self) -> None:
        p = make_proposal()
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert graph.graph_id == "test-001"
        assert len(graph.nodes) >= 1

    def test_no_evidence_triggers_warning(self) -> None:
        p = make_proposal(claimed_evidence=[])
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "no_evidence_provided" in graph.warnings

    def test_evidence_provided_sets_sufficient(self) -> None:
        p = make_proposal(claimed_evidence=["source1"])
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert graph.evidence_status == "sufficient"

    def test_near_certainty_without_evidence_detected(self) -> None:
        p = make_proposal(
            gpt_output="بالتأكيد هذا صحيح ولا شك.",
            claimed_evidence=[],
        )
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "near_certainty_without_evidence" in graph.warnings

    def test_harm_haram_detected(self) -> None:
        p = make_proposal(
            input_text="هل الضار حرام؟",
            gpt_output="نعم، الضار هو حرام.",
        )
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "harm_implies_haram" in graph.warnings

    def test_api_as_evidence_detected(self) -> None:
        p = make_proposal(
            gpt_output="API reliable مصدر موثوق لهذه المعلومة.",
        )
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "tool_api_not_standalone_evidence" in graph.warnings

    def test_metaphor_literal_detected(self) -> None:
        p = make_proposal(
            input_text="المجتمع مريض",
            gpt_output="يجب heal علاجه literally كما نعالج body.",
        )
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "metaphor_as_literal" in graph.warnings

    def test_unsupported_generalization_detected(self) -> None:
        p = make_proposal(
            input_text="هل كل الشركات تستخدم هذا؟",
            gpt_output="نعم كل الشركات تستخدمه.",
            claimed_evidence=[],
        )
        graph = self.parser.parse_text_to_proposal_graph(p)
        assert "unsupported_generalization" in graph.warnings
