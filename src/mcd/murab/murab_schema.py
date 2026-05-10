"""MurabUnit — core dataclass for Arabic I'rab analysis (Phase 7.5)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MurabUnit:
    """Represents one token's full I'rab (grammatical declension) analysis."""

    unit_id: str
    surface: str
    normalized: str
    token_id: str

    # Grammatical type
    word_type: str  # noun|verb|adjective|participle|masdar|proper_noun|
                    # broken_plural|sound_plural|dual|five_nouns|imperfect_verb

    # I'rab case and marker
    irab_case: str        # nominative|accusative|genitive|jussive|indeclinable_local|unknown
    irab_marker: str      # damma|fatha|kasra|sukun|alif|waw|ya|nun|deleted_nun|
                          # estimated|local|none
    marker_visibility: str  # apparent|estimated|local|prevented

    governing_factor_id: Optional[str]

    # Roles
    syntactic_role: str
    semantic_role: str  # agent|patient|predicate|subject|possessor|possessed|
                        # instrument|time|place|state|specification|cause|
                        # exception|restriction|dependent|unknown

    # Graph edges to other units
    relation_edges: list = field(default_factory=list)  # list[dict]

    # Certainty and diagnostics
    certainty_policy: str = "unknown"
    warnings: list[str] = field(default_factory=list)
    trace_ids: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ #
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
            normalized=d.get("normalized", d["surface"]),
            token_id=d.get("token_id", ""),
            word_type=d.get("word_type", "noun"),
            irab_case=d.get("irab_case", "unknown"),
            irab_marker=d.get("irab_marker", "none"),
            marker_visibility=d.get("marker_visibility", "apparent"),
            governing_factor_id=d.get("governing_factor_id"),
            syntactic_role=d.get("syntactic_role", ""),
            semantic_role=d.get("semantic_role", "unknown"),
            relation_edges=d.get("relation_edges", []),
            certainty_policy=d.get("certainty_policy", "unknown"),
            warnings=d.get("warnings", []),
            trace_ids=d.get("trace_ids", []),
        )
