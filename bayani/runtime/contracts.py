"""Typed data models for the Bayani Mustadil Runtime Engine.

All pipeline inputs, intermediate results, trace records and final outputs
are represented as frozen (or mutable where accumulation is needed)
dataclasses so that every component can exchange structured, type-checked
data without requiring an external library such as Pydantic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

@dataclass
class PromptInput:
    """Raw prompt submitted by the caller."""
    prompt: str
    mode: str = "analysis"  # "analysis" | "application" | "construction"


# ---------------------------------------------------------------------------
# Classifier outputs
# ---------------------------------------------------------------------------

@dataclass
class PromptTypeResult:
    """Result of the Prompt-Type Classifier (PT-01 .. PT-10)."""
    type_id: str          # e.g. "PT-07"
    type_name: str        # e.g. "Mafhoom Prompt"
    confidence: str       # "high" | "medium" | "low"
    matched_rule: str     # human-readable description of the matched rule


@dataclass
class IntentClassificationResult:
    """Result of the Mustadil Prompt Classifier (MPC-01 .. MPC-11)."""
    primary_purpose: str               # e.g. "hukm_knowledge"
    secondary_purposes: List[str] = field(default_factory=list)
    thinking_level: str = "standard"   # "shallow" | "standard" | "deep"
    malakah_mode: bool = False
    hukm_mode: str = "knowledge"       # "knowledge" | "istinbat"
    evidence_required: bool = False
    tarjih_required: bool = False
    tahqeeq_manat_required: bool = False
    construction_intent: bool = False
    mpc_layers_activated: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pipeline layer result
# ---------------------------------------------------------------------------

@dataclass
class PipelineLayerResult:
    """Structured output produced by a single pipeline layer."""
    layer_name: str
    status: str                             # "passed" | "failed" | "deferred"
    claims: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    required_next: List[str] = field(default_factory=list)
    forbidden_jumps_checked: List[str] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Epistemic trace
# ---------------------------------------------------------------------------

@dataclass
class EpistemicTraceStep:
    """One layer-to-layer transition recorded by the trace engine."""
    from_layer: str
    to_layer: str
    bridge: str              # logical reason that connects the two layers
    validated: bool
    forbidden_jump_checked: str = ""


@dataclass
class EpistemicTrace:
    """Full trace of all layer transitions for one prompt execution."""
    steps: List[EpistemicTraceStep] = field(default_factory=list)

    def add(self, step: EpistemicTraceStep) -> None:
        self.steps.append(step)

    def as_list(self) -> List[dict]:
        return [
            {
                "from": s.from_layer,
                "to": s.to_layer,
                "bridge": s.bridge,
                "validated": s.validated,
                "forbidden_jump_checked": s.forbidden_jump_checked,
            }
            for s in self.steps
        ]


# ---------------------------------------------------------------------------
# Audit result
# ---------------------------------------------------------------------------

@dataclass
class AuditResult:
    """Outcome of the runtime invariant audit."""
    passed: bool
    violations: List[str] = field(default_factory=list)
    certainty_map: dict = field(default_factory=dict)
    jumps_prevented: List[str] = field(default_factory=list)
    final_rank: str = "structured_answer_allowed"
    # Possible final_rank values:
    #   "structured_answer_allowed"
    #   "hypothesis_only"
    #   "deferred_pending_classification"
    #   "blocked_epistemic_violation"


# ---------------------------------------------------------------------------
# ZeroGuard result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZeroResult:
    """Blocking governance result for invalid product-equivalence claims."""
    zero_type: str
    severity: str
    required_layer: str
    claim: str
    reason: str
    allowed_reframe: str
    blocks: List[str] = field(default_factory=list)

    def format_blocking_message(self) -> str:
        return (
            f"Zero[{self.zero_type}] {self.reason} "
            f"Allowed reframe: {self.allowed_reframe}"
        )


# ---------------------------------------------------------------------------
# Final output
# ---------------------------------------------------------------------------

@dataclass
class MustadilOutput:
    """Structured final output of the MustadilRuntimeEngine."""
    prompt_type: str
    intent: IntentClassificationResult
    required_layers: List[str]
    layer_results: List[PipelineLayerResult]
    trace: EpistemicTrace
    audit: AuditResult
    final_response: Optional[str] = None
    governance_zero: Optional[ZeroResult] = None
    # None means the engine defers to a downstream decoder/LLM
