"""Re-export proposal schemas for the foldable learning layer."""
from mcd.residual_learning.proposal_schema import (
    GPTProposal,
    ProposalGraph,
    ProposalCognitiveNode,
    ProposalCognitiveEdge,
    ProposalType,
)
__all__ = ["GPTProposal", "ProposalGraph", "ProposalCognitiveNode", "ProposalCognitiveEdge", "ProposalType"]
