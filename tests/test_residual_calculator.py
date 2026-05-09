"""Tests for ResidualCalculator — core residual computation."""
from __future__ import annotations

import pytest
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalType
from mcd.residual_learning.proposal_parser import ProposalParser
from mcd.residual_learning.residual_calculator import ResidualCalculator, MathematicalContractResult
from mcd.residual_learning.residual_schema import ResidualType, Severity


def make_proposal(**kwargs) -> GPTProposal:
    defaults = {
        "proposal_id": "calc-test",
        "input_text": "سؤال",
        "gpt_output": "إجابة",
        "proposal_type": ProposalType.ANSWER,
        "claimed_evidence": [],
        "claimed_certainty": None,
        "metadata": {},
    }
    defaults.update(kwargs)
    return GPTProposal(**defaults)


class TestResidualCalculator:
    def setup_method(self) -> None:
        self.parser = ProposalParser()
        self.calculator = ResidualCalculator()

    def _calc(self, proposal: GPTProposal, contract: MathematicalContractResult | None = None):
        graph = self.parser.parse_text_to_proposal_graph(proposal)
        return self.calculator.calculate(proposal, graph, contract)

    def test_gpt_output_not_evidence(self) -> None:
        """Core rule: GPT output is NEVER evidence."""
        p = make_proposal(
            claimed_evidence=["gpt_said_so"],
        )
        residual = self._calc(p)
        assert ResidualType.TOOL_EVIDENCE.value in residual.residual_types
        assert any("gpt_output_as_evidence_rejected" in g for g in residual.evidence_gaps)

    def test_false_certainty_creates_certainty_residual(self) -> None:
        p = make_proposal(
            gpt_output="بالتأكيد هذا صحيح ولا شك فيه.",
            claimed_evidence=[],
            claimed_certainty="certain",
        )
        residual = self._calc(p)
        assert ResidualType.CERTAINTY.value in residual.residual_types
        assert ResidualType.EVIDENCE.value in residual.residual_types
        assert len(residual.certainty_errors) > 0

    def test_harm_haram_creates_residual(self) -> None:
        p = make_proposal(
            input_text="هل الضار harm حرام haram؟",
            gpt_output="نعم، الضار harm هو حرام haram.",
        )
        residual = self._calc(p)
        assert ResidualType.HARM_HARAM.value in residual.residual_types
        assert len(residual.safety_errors) > 0
        assert "harm_haram_invariant" in residual.invariant_violations

    def test_api_as_authority_creates_tool_evidence_residual(self) -> None:
        p = make_proposal(
            gpt_output="API reliable مصدر موثوق، إذا قالت API فهو صحيح.",
        )
        residual = self._calc(p)
        assert ResidualType.TOOL_EVIDENCE.value in residual.residual_types
        assert any("tool_api_as_evidence_rejected" in g for g in residual.evidence_gaps)

    def test_metaphor_as_literal_creates_metaphor_residual(self) -> None:
        p = make_proposal(
            input_text="المجتمع مريض",
            gpt_output="يجب heal علاجه literally كما نعالج body sick.",
        )
        residual = self._calc(p)
        assert ResidualType.METAPHOR.value in residual.residual_types
        assert len(residual.metaphor_errors) > 0

    def test_unsupported_generalization_creates_evidence_residual(self) -> None:
        p = make_proposal(
            input_text="هل كل الشركات تستخدم GraphRAG؟",
            gpt_output="نعم، كل الشركات تقريبًا تستخدم GraphRAG الآن.",
            claimed_evidence=[],
        )
        residual = self._calc(p)
        assert ResidualType.UNSUPPORTED_GENERALIZATION.value in residual.residual_types
        assert ResidualType.EVIDENCE.value in residual.residual_types

    def test_no_residual_for_clean_proposal(self) -> None:
        p = make_proposal(
            gpt_output="هذا الماء يغلي عند 100 درجة.",
            claimed_evidence=["physics_textbook"],
            claimed_certainty=None,
        )
        residual = self._calc(p)
        # Should have no or minimal residuals
        assert residual.residual_score < 0.3

    def test_contract_violation_maps_to_residual(self) -> None:
        p = make_proposal()
        graph = self.parser.parse_text_to_proposal_graph(p)
        contract = MathematicalContractResult(
            passed=False,
            violations=["Contract[7]: near_certainty requires evidence_refs"],
            warnings=[],
            score=0.9,
        )
        residual = self.calculator.calculate(p, graph, contract)
        assert ResidualType.CERTAINTY.value in residual.residual_types
        assert ResidualType.EVIDENCE.value in residual.residual_types

    def test_blocking_severity_for_harm_haram(self) -> None:
        p = make_proposal(
            input_text="harm ضار haram حرام",
            gpt_output="harm ضار يعني haram حرام.",
        )
        residual = self._calc(p)
        assert residual.severity == Severity.BLOCKING.value

    def test_residual_score_positive_when_errors(self) -> None:
        p = make_proposal(
            gpt_output="بالتأكيد هذا صحيح.",
            claimed_evidence=[],
            claimed_certainty="certain",
        )
        residual = self._calc(p)
        assert residual.residual_score > 0.0

    def test_residual_id_generated(self) -> None:
        p = make_proposal()
        residual = self._calc(p)
        assert len(residual.residual_id) > 0

    def test_proposal_id_preserved(self) -> None:
        p = make_proposal(proposal_id="unique-123")
        residual = self._calc(p)
        assert residual.proposal_id == "unique-123"
