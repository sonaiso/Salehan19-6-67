"""GPTProposal and ProposalGraph schema — Phase 7."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProposalType(str, Enum):
    ANSWER = "answer"
    EXPLANATION = "explanation"
    DATASET_EXAMPLE = "dataset_example"
    ADVERSARIAL_CASE = "adversarial_case"
    GRAPH_SUGGESTION = "graph_suggestion"
    SCHEMA_SUGGESTION = "schema_suggestion"


@dataclass
class GPTProposal:
    """A proposal emitted by an external LLM (e.g. GPT-5.5).

    GPT output is never evidence.  It is a *proposal* that must pass the
    MathematicalContract before any part of it can become learning signal.
    """
    proposal_id: str
    input_text: str
    gpt_output: str
    proposal_type: ProposalType
    claimed_evidence: list[str] = field(default_factory=list)
    claimed_certainty: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "input_text": self.input_text,
            "gpt_output": self.gpt_output,
            "proposal_type": self.proposal_type.value if isinstance(self.proposal_type, ProposalType) else self.proposal_type,
            "claimed_evidence": self.claimed_evidence,
            "claimed_certainty": self.claimed_certainty,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GPTProposal":
        pt = d.get("proposal_type", "answer")
        try:
            pt = ProposalType(pt)
        except ValueError:
            pt = ProposalType.ANSWER
        return cls(
            proposal_id=d["proposal_id"],
            input_text=d["input_text"],
            gpt_output=d["gpt_output"],
            proposal_type=pt,
            claimed_evidence=d.get("claimed_evidence", []),
            claimed_certainty=d.get("claimed_certainty"),
            metadata=d.get("metadata", {}),
        )


@dataclass
class ProposalCognitiveNode:
    """A lightweight node inside a ProposalGraph (not a full CognitiveNode)."""
    node_id: str
    surface: str
    node_type: str
    certainty: float = 0.5
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "surface": self.surface,
            "node_type": self.node_type,
            "certainty": self.certainty,
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class ProposalCognitiveEdge:
    """A lightweight edge inside a ProposalGraph."""
    edge_id: str
    source: str
    relation: str
    target: str
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class ProposalGraph:
    """A graph representation of a GPTProposal, built by the ProposalParser."""
    graph_id: str
    nodes: list[ProposalCognitiveNode] = field(default_factory=list)
    edges: list[ProposalCognitiveEdge] = field(default_factory=list)
    root_vector: dict[str, float] = field(default_factory=dict)
    evidence_status: str = "missing"
    certainty_policy: str = "probable_knowledge"
    warnings: list[str] = field(default_factory=list)

    def node_ids(self) -> set[str]:
        return {n.node_id for n in self.nodes}

    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "root_vector": self.root_vector,
            "evidence_status": self.evidence_status,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }
