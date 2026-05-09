"""Grounded Frame dataclasses — core containers for GLCFL."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GroundingStatus(str, Enum):
    UNGROUNDED = "ungrounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    GROUNDED = "grounded"
    VERIFIED = "verified"


@dataclass
class GroundedLexeme:
    lexeme_id: str
    surface: str
    normalized: str
    dal: str
    madlul: Optional[str] = None
    grounding_status: GroundingStatus = GroundingStatus.UNGROUNDED
    reality_ref: Optional[str] = None
    prior_knowledge_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    certainty: float = 0.0
    notes: str = ""


@dataclass
class GroundedReasoningFrame:
    input_text: str
    prompt_frame: Optional[dict] = None
    mcd_analysis: Optional[dict] = None
    nabhani_analysis: Optional[dict] = None
    grounded_lexemes: list = field(default_factory=list)
    role_frames: list = field(default_factory=list)
    nisbah_frames: list = field(default_factory=list)
    manat_results: list = field(default_factory=list)
    usul_semantics: list = field(default_factory=list)
    tarjih_results: list = field(default_factory=list)
    social_frames: list = field(default_factory=list)
    system_frames: list = field(default_factory=list)
    civilization_frames: list = field(default_factory=list)
    value_frames: list = field(default_factory=list)
    final_status: str = "pending"
    final_answer: str = ""
    certainty_summary: float = 0.0
    warnings: list[str] = field(default_factory=list)
