"""Formal Epistemic Transition Core primitives."""
from __future__ import annotations

from mcd.core.collapse_metric import CollapseEvent, collapse_score
from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient, required_rank_for_judgment
from mcd.core.forbidden_transitions import ForbiddenTransition, FORBIDDEN, validate_transition
from mcd.core.legitimacy_state import LegitimacyState
from mcd.core.proof_object import CertificateRequirementError, ProofObject, require_certificate_ready
from mcd.core.trace_graph import TraceGraph, TraceStep

__all__ = [
    "CollapseEvent",
    "collapse_score",
    "EpistemicRank",
    "is_rank_sufficient",
    "required_rank_for_judgment",
    "ForbiddenTransition",
    "FORBIDDEN",
    "validate_transition",
    "LegitimacyState",
    "CertificateRequirementError",
    "ProofObject",
    "require_certificate_ready",
    "TraceGraph",
    "TraceStep",
]
