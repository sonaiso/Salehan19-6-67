"""CognitiveResidualLearningEngine — Phase 7 main orchestrator.

GPT suggests. Mathematical Contract judges. Cognitive Residual teaches.

Formula:
    CognitiveResidual = GPTProposal − MathematicalContract
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .proposal_schema import GPTProposal, ProposalGraph
from .proposal_parser import ProposalParser
from .residual_schema import CognitiveResidual
from .residual_calculator import ResidualCalculator, MathematicalContractResult
from .residual_classifier import ResidualClassifier, ResidualClassification
from .learning_action import LearningAction
from .learning_router import LearningRouter
from .residual_report import ResidualReport


@dataclass
class ResidualAnalysisResult:
    proposal: GPTProposal
    proposal_graph: ProposalGraph
    contract_result: MathematicalContractResult
    residual: CognitiveResidual
    classification: ResidualClassification
    actions: list[LearningAction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal.proposal_id,
            "proposal_graph_warnings": self.proposal_graph.warnings,
            "contract_passed": self.contract_result.passed,
            "contract_violations": self.contract_result.violations,
            "residual": self.residual.to_dict(),
            "classification": self.classification.to_dict(),
            "actions": [a.to_dict() for a in self.actions],
        }


class CognitiveResidualLearningEngine:
    """Orchestrates the full residual learning pipeline.

    1. Receive GPT Proposal.
    2. Parse it to ProposalGraph.
    3. Run MathematicalContract checks.
    4. Compute CognitiveResidual.
    5. Classify residual.
    6. Route to LearningActions.
    """

    def __init__(self) -> None:
        self._parser = ProposalParser()
        self._calculator = ResidualCalculator()
        self._classifier = ResidualClassifier()
        self._router = LearningRouter()

    def analyze(
        self,
        proposal: GPTProposal,
        contract_result: MathematicalContractResult | None = None,
    ) -> ResidualAnalysisResult:
        # Step 1 & 2: parse proposal to graph
        proposal_graph = self._parser.parse_text_to_proposal_graph(proposal)

        # Step 3: use provided contract result or create a default one from graph warnings
        if contract_result is None:
            contract_result = self._derive_contract_result(proposal_graph)

        # Step 4: compute residual
        residual = self._calculator.calculate(proposal, proposal_graph, contract_result)

        # Step 5: classify
        classification = self._classifier.classify(residual)

        # Step 6: route
        actions = self._router.route(residual)

        return ResidualAnalysisResult(
            proposal=proposal,
            proposal_graph=proposal_graph,
            contract_result=contract_result,
            residual=residual,
            classification=classification,
            actions=actions,
        )

    def analyze_batch(
        self,
        proposals: list[GPTProposal],
    ) -> list[ResidualAnalysisResult]:
        return [self.analyze(p) for p in proposals]

    def generate_report(self, results: list[ResidualAnalysisResult]) -> ResidualReport:
        residuals = [r.residual for r in results]
        return ResidualReport.build(residuals)

    @staticmethod
    def _derive_contract_result(graph: ProposalGraph) -> MathematicalContractResult:
        """Derive a lightweight contract result from proposal-graph warnings.

        This mirrors the main contract checks but operates on the ProposalGraph
        (not a full CognitiveGraph). Used when no external contract result is provided.
        """
        violations: list[str] = []
        warnings: list[str] = []

        # near_certainty without evidence
        if "near_certainty_without_evidence" in graph.warnings:
            violations.append(
                "Contract[7]: near_certainty requires evidence_refs"
            )
        # harm → haram
        if "harm_implies_haram" in graph.warnings:
            violations.append(
                "Contract[9]: harm does not entail haram — distinct domains"
            )
        # tool/API as evidence
        if "tool_api_not_standalone_evidence" in graph.warnings:
            violations.append(
                "Contract[10]: tool/source used without evidence_refs or trust_policy"
            )
        # ambiguous + near_certainty
        if "ambiguous_requires_context" in graph.warnings and graph.certainty_policy == "near_certainty":
            violations.append(
                "Contract[8]: ambiguous input cannot have near_certainty policy"
            )
        # source without trust policy
        if "no_evidence_provided" in graph.warnings:
            warnings.append("Contract[12]: proposal has no evidence — sourced_from lacks trust policy")

        passed = len(violations) == 0
        score = max(0.0, 1.0 - 0.1 * len(violations) - 0.02 * len(warnings))
        return MathematicalContractResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            score=min(1.0, score),
        )
