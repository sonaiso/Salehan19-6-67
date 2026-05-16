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
from mcd.core.linking_type import LinkingType, LinkingTypeError, certificate_eligible, parse_linking_type
from mcd.core.rank_calculus import (
    FINAL_JUDGMENTS as RANK_FINAL_JUDGMENTS,
    LINKING_MIN_EVIDENCE_RANK,
    RankCalculationError,
    downgrade_judgment_for_residuals,
    enforce_judgment_rank,
    enforce_linking_rank,
    minimum_evidence_rank_for_link,
    rank_at_least,
)
from mcd.core.linking_contract import LinkingContract, LinkingContractError
from mcd.core.public_judgment import (
    PUBLIC_FINAL_JUDGMENTS,
    INTERNAL_SUSPEND,
    INTERNAL_SUSPENDED,
    collapse_to_public_judgment,
    enforce_governed_output_contract,
    is_public_final_judgment,
    normalize_public_judgment_fields,
)
from mcd.core.public_schema import (
    FIELD_GOVERNANCE_AUDIT,
    FIELD_GOVERNANCE_GATE_PASSED,
    FIELD_JUDGMENT,
    FIELD_PROOF_ID,
    FIELD_PROOF_OBJECT_REF,
    FIELD_RAW_TEXT_UNITS,
    FIELD_RESIDUALS,
    FIELD_REVERSE_TRACE_OBJ,
    FIELD_REVERSE_TRACE_REF,
    JUDGMENT_CERTIFICATE,
    JUDGMENT_HYPOTHESIS,
    JUDGMENT_ZERO,
)
from mcd.core.governance_audit import GovernanceAuditEvent
from mcd.core.residual_taxonomy import (
    ResidualFamily,
    ResidualSeverity,
    ResidualSpec,
    blocking_residuals,
    classify_residual,
    classify_residuals,
    has_blocking_residuals,
)
