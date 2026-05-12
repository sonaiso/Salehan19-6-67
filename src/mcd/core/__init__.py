from __future__ import annotations

from mcd.core.symbols import *
from mcd.core.measures import clamp, normalize_scores, weighted_average
from mcd.core.evidence import Evidence, EvidenceType
from mcd.core.certainty import Certainty, CERTAINTY_LEVELS
from mcd.core.vectors import FeatureVector
from mcd.core.roles import RoleType, RoleVector
from mcd.core.nodes import KnowledgeNode, NODE_LEVELS
from mcd.core.relations import Relation, RelationType

from mcd.core.collapse_metric import CollapseEvent, collapse_score
from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient, required_rank_for_judgment
from mcd.core.forbidden_transitions import ForbiddenTransition, FORBIDDEN, validate_transition
from mcd.core.legitimacy_state import LegitimacyState
from mcd.core.proof_object import CertificateRequirementError, ProofObject, require_certificate_ready
from mcd.core.trace_graph import TraceGraph, TraceStep
