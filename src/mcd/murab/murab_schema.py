"""MurabUnit — core data model for Arabic I'rab analysis."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MurabUnit:
    unit_id: str
    surface: str
    normalized: str
    token_id: str
    word_type: str  # noun|verb|adjective|participle|masdar|proper_noun|broken_plural|sound_plural|dual|five_nouns|imperfect_verb
    irab_case: str  # nominative|accusative|genitive|jussive|indeclinable_local|unknown
    irab_marker: str  # damma|fatha|kasra|sukun|alif|waw|ya|nun|deleted_nun|estimated|local|none
    marker_visibility: str  # apparent|estimated|local|prevented
    governing_factor_id: Optional[str] = None
    syntactic_role: str = "unknown"
    semantic_role: str = "unknown"
    relation_edges: list = field(default_factory=list)
    certainty_policy: str = "unknown"
    warnings: list = field(default_factory=list)
    trace_ids: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "surface": self.surface,
            "normalized": self.normalized,
            "token_id": self.token_id,
            "word_type": self.word_type,
            "irab_case": self.irab_case,
            "irab_marker": self.irab_marker,
            "marker_visibility": self.marker_visibility,
            "governing_factor_id": self.governing_factor_id,
            "syntactic_role": self.syntactic_role,
            "semantic_role": self.semantic_role,
            "relation_edges": self.relation_edges,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
            "trace_ids": self.trace_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MurabUnit":
        return cls(
            unit_id=d["unit_id"],
            surface=d["surface"],
            normalized=d["normalized"],
            token_id=d["token_id"],
            word_type=d["word_type"],
            irab_case=d["irab_case"],
            irab_marker=d["irab_marker"],
            marker_visibility=d["marker_visibility"],
            governing_factor_id=d.get("governing_factor_id"),
            syntactic_role=d["syntactic_role"],
            semantic_role=d["semantic_role"],
            relation_edges=d.get("relation_edges", []),
            certainty_policy=d.get("certainty_policy", "unknown"),
            warnings=d.get("warnings", []),
            trace_ids=d.get("trace_ids", []),
        )
