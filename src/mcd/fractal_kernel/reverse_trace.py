from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class ReverseTrace:
    reverse_trace_id: str
    final_claim: str
    proof_id: str
    judgment_units: list[str] = field(default_factory=list)
    claim_graph_units: list[str] = field(default_factory=list)
    discourse_graph_units: list[str] = field(default_factory=list)
    full_text_units: list[str] = field(default_factory=list)
    section_units: list[str] = field(default_factory=list)
    paragraph_units: list[str] = field(default_factory=list)
    clause_units: list[str] = field(default_factory=list)
    phrase_units: list[str] = field(default_factory=list)
    morphology_units: list[str] = field(default_factory=list)
    lexeme_units: list[str] = field(default_factory=list)
    orthographic_units: list[str] = field(default_factory=list)
    grapheme_units: list[str] = field(default_factory=list)
    concept_units: list[str] = field(default_factory=list)
    sentence_units: list[str] = field(default_factory=list)
    token_units: list[str] = field(default_factory=list)
    unicode_units: list[str] = field(default_factory=list)
    raw_text_units: list[str] = field(default_factory=list)
    proof_object_units: list[str] = field(default_factory=list)
    final_judgment_units: list[str] = field(default_factory=list)
    evidence_chain: list[str] = field(default_factory=list)
    certainty_chain: list[str] = field(default_factory=list)
    operator_chain: list[str] = field(default_factory=list)
    relation_chain: list[str] = field(default_factory=list)
    complete: bool = False

    @staticmethod
    def make_id() -> str:
        return f"RTRACE-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "reverse_trace_id": self.reverse_trace_id,
            "final_claim": self.final_claim,
            "proof_id": self.proof_id,
            "judgment_units": self.judgment_units,
            "claim_graph_units": self.claim_graph_units,
            "discourse_graph_units": self.discourse_graph_units,
            "full_text_units": self.full_text_units,
            "section_units": self.section_units,
            "paragraph_units": self.paragraph_units,
            "clause_units": self.clause_units,
            "phrase_units": self.phrase_units,
            "morphology_units": self.morphology_units,
            "lexeme_units": self.lexeme_units,
            "orthographic_units": self.orthographic_units,
            "grapheme_units": self.grapheme_units,
            "concept_units": self.concept_units,
            "sentence_units": self.sentence_units,
            "token_units": self.token_units,
            "unicode_units": self.unicode_units,
            "raw_text_units": self.raw_text_units,
            "proof_object_units": self.proof_object_units,
            "final_judgment_units": self.final_judgment_units,
            "evidence_chain": self.evidence_chain,
            "certainty_chain": self.certainty_chain,
            "operator_chain": self.operator_chain,
            "relation_chain": self.relation_chain,
            "complete": self.complete,
        }
