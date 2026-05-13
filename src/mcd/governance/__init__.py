"""Canonical governance adapters and contracts."""
from __future__ import annotations

from mcd.governance.adapters import (
    from_cfk_proof,
    from_coding_judgment,
    from_fractal_kernel_proof,
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

__all__ = [
    "CanonicalGovernanceRecord",
    "from_cfk_proof",
    "from_fractal_kernel_proof",
    "from_coding_judgment",
    "AdversarialAttempt",
    "AdversarialEvaluation",
    "FORBIDDEN_TRANSITIONS",
    "evaluate_adversarial_attempt",
    "DistributedAgentAttempt",
    "DistributedSimulationResult",
    "run_distributed_governance_simulation",
]
