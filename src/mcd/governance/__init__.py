"""Canonical governance adapters and contracts."""
from __future__ import annotations

from mcd.governance.adapters import (
    from_cfk_proof,
    from_coding_judgment,
    from_fractal_kernel_proof,
    to_unified_kernel_from_cfk_proof,
    to_unified_kernel_from_coding_judgment,
    to_unified_kernel_from_concept_claim,
    to_unified_kernel_from_fractal_kernel_proof,
)
from mcd.governance.adversarial_validation import (
    AdversarialAttempt,
    AdversarialEvaluation,
    FORBIDDEN_TRANSITIONS,
    evaluate_adversarial_attempt,
)
from mcd.governance.distributed_simulation import (
    DistributedAgentAttempt,
    DistributedSimulationResult,
    run_distributed_governance_simulation,
)
from mcd.governance.contracts import CanonicalGovernanceRecord
from mcd.governance.unified_kernel import UnifiedGovernanceKernel

__all__ = [
    "CanonicalGovernanceRecord",
    "from_cfk_proof",
    "from_fractal_kernel_proof",
    "from_coding_judgment",
    "to_unified_kernel_from_cfk_proof",
    "to_unified_kernel_from_fractal_kernel_proof",
    "to_unified_kernel_from_coding_judgment",
    "to_unified_kernel_from_concept_claim",
    "UnifiedGovernanceKernel",
    "AdversarialAttempt",
    "AdversarialEvaluation",
    "FORBIDDEN_TRANSITIONS",
    "evaluate_adversarial_attempt",
    "DistributedAgentAttempt",
    "DistributedSimulationResult",
    "run_distributed_governance_simulation",
]
