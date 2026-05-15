"""Complete Fractal Kernel (CFK) proof-track contracts.

This module formalizes Unicode→Awareness→Judgment as testable contracts.
It does not grant a global certificate by score alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


_KERNEL_FIELDS: tuple[str, ...] = (
    "Input",
    "Candidate",
    "Constraint",
    "Evidence",
    "Residual",
    "Ranking",
    "Decision",
    "ReverseTrace",
)


class KernelStep(str, Enum):
    INPUT = "Input"
    CANDIDATE = "Candidate"
    CONSTRAINT = "Constraint"
    EVIDENCE = "Evidence"
    RESIDUAL = "Residual"
    RANKING = "Ranking"
    DECISION = "Decision"
    REVERSE_TRACE = "ReverseTrace"


class ResidualSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"
    FATAL = "fatal"


class EvidenceStrength(str, Enum):
    NONE = "none"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    CONCLUSIVE = "conclusive"


class DecisionLevel(str, Enum):
    ZERO = "zero"
    HYPOTHESIS = "hypothesis"
    CERTIFICATE = "certificate"


class CFKTheoremStatus(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    HYPOTHESIS = "HYPOTHESIS"
    STRONG_HYPOTHESIS = "STRONG_HYPOTHESIS"
    CERTIFICATE_CANDIDATE = "CERTIFICATE_CANDIDATE"
    CERTIFICATE = "CERTIFICATE"


@dataclass
class EvidenceObject:
    evidence_id: str
    source: str
    strength: EvidenceStrength = EvidenceStrength.NONE
    independent: bool = False

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "strength": self.strength.value,
            "independent": self.independent,
        }


@dataclass
class ResidualObject:
    residual_id: str
    residual_type: str
    severity: ResidualSeverity = ResidualSeverity.WARNING
    blocking: bool = False
    propagated_from: str | None = None

    def to_dict(self) -> dict:
        return {
            "residual_id": self.residual_id,
            "residual_type": self.residual_type,
            "severity": self.severity.value,
            "blocking": self.blocking,
            "propagated_from": self.propagated_from,
        }


@dataclass
class ReverseTraceGraph:
    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    path_complete: bool = False

    def to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": [list(edge) for edge in self.edges],
            "path_complete": self.path_complete,
        }


@dataclass
class GateContract:
    kernel_fields: tuple[str, ...] = _KERNEL_FIELDS
    requires_evidence_for_certificate: bool = True
    requires_reverse_trace_for_certificate: bool = True
    blocks_certificate_on_blocking_residual: bool = True


@dataclass
class FractalInvariant:
    name: str
    kernel_fields: tuple[str, ...] = _KERNEL_FIELDS
    score_threshold_never_sufficient: bool = True
    no_certificate_without_proof_object: bool = True
    no_certificate_without_governance_gate: bool = True
    no_certificate_without_reverse_trace: bool = True


@dataclass
class LayerSpec:
    name: str
    material: str
    allowed_inputs: list[str]
    candidate_types: list[str]
    constraints: list[str]
    evidence_types: list[str]
    residual_types: list[str]
    ranking_rule: str
    decision_rule: str
    reverse_trace_requirements: list[str]
    awareness_meta_gate: bool = False
    gate_contract: GateContract = field(default_factory=GateContract)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "material": self.material,
            "allowed_inputs": self.allowed_inputs,
            "candidate_types": self.candidate_types,
            "constraints": self.constraints,
            "evidence_types": self.evidence_types,
            "residual_types": self.residual_types,
            "ranking_rule": self.ranking_rule,
            "decision_rule": self.decision_rule,
            "reverse_trace_requirements": self.reverse_trace_requirements,
            "awareness_meta_gate": self.awareness_meta_gate,
            "gate_contract": {
                "kernel_fields": list(self.gate_contract.kernel_fields),
                "requires_evidence_for_certificate": self.gate_contract.requires_evidence_for_certificate,
                "requires_reverse_trace_for_certificate": self.gate_contract.requires_reverse_trace_for_certificate,
                "blocks_certificate_on_blocking_residual": self.gate_contract.blocks_certificate_on_blocking_residual,
            },
        }


@dataclass
class TransitionSpec:
    from_layer: str
    to_layer: str
    gate_contract: GateContract = field(default_factory=GateContract)


@dataclass
class GateResult:
    input: dict
    candidate: dict
    constraint: list[str] = field(default_factory=list)
    evidence: list[EvidenceObject] = field(default_factory=list)
    residual: list[ResidualObject] = field(default_factory=list)
    ranking: dict = field(default_factory=dict)
    decision: DecisionLevel = DecisionLevel.HYPOTHESIS
    reverse_trace: ReverseTraceGraph = field(default_factory=ReverseTraceGraph)
    notes: list[str] = field(default_factory=list)

    def has_blocking_residual(self) -> bool:
        return any(r.blocking or r.severity in {ResidualSeverity.BLOCKING, ResidualSeverity.FATAL} for r in self.residual)

    def to_dict(self) -> dict:
        return {
            "Input": self.input,
            "Candidate": self.candidate,
            "Constraint": self.constraint,
            "Evidence": [e.to_dict() for e in self.evidence],
            "Residual": [r.to_dict() for r in self.residual],
            "Ranking": self.ranking,
            "Decision": self.decision.value,
            "ReverseTrace": self.reverse_trace.to_dict(),
            "notes": self.notes,
        }


@dataclass
class CFKProofObligations:
    layer_registry_complete: bool
    structural_recurrence_verified: bool
    transition_contracts_verified: bool
    certificate_gates_verified: bool
    residual_propagation_verified: bool
    awareness_meta_gate_verified: bool
    reverse_trace_verified: bool
    governance_gate_passed: bool = False
    proof_object_present: bool = False
    reverse_trace_reference_present: bool = False


def _make_layer(name: str, material: str, *, awareness_meta_gate: bool = False) -> LayerSpec:
    return LayerSpec(
        name=name,
        material=material,
        allowed_inputs=["str", "dict"],
        candidate_types=["token", "relation", "claim", "judgment_fragment"],
        constraints=["forbidden_transitions", "governance_contract"],
        evidence_types=["observational", "textual", "empirical", "logical"],
        residual_types=["evidence_gap", "constraint_gap", "zero_in_path"],
        ranking_rule="rank_by_evidence_strength_then_constraint_satisfaction",
        decision_rule="zero_or_hypothesis_or_certificate_via_gate",
        reverse_trace_requirements=["origin", "path", "justification"],
        awareness_meta_gate=awareness_meta_gate,
    )


CFK_LAYER_REGISTRY: dict[str, LayerSpec] = {
    "Unicode": _make_layer("Unicode", "code_points"),
    "Grapheme": _make_layer("Grapheme", "grapheme_clusters"),
    "Phonology": _make_layer("Phonology", "phonological_features"),
    "Syllable": _make_layer("Syllable", "syllabic_structure"),
    "Morphology": _make_layer("Morphology", "morphological_patterns"),
    "Lexicon": _make_layer("Lexicon", "lexical_entries"),
    "Syntax": _make_layer("Syntax", "syntactic_relations"),
    "Semantics": _make_layer("Semantics", "semantic_roles"),
    "Pragmatics": _make_layer("Pragmatics", "contextual_implications"),
    "Reality": _make_layer("Reality", "external_world_claims"),
    "Cognition": _make_layer("Cognition", "cognitive_distinctions"),
    "Awareness": _make_layer("Awareness", "supervisory_meta_gate", awareness_meta_gate=True),
    "Judgment": _make_layer("Judgment", "governed_public_judgment"),
}

CFK_LAYER_SEQUENCE: tuple[str, ...] = tuple(CFK_LAYER_REGISTRY.keys())

CFK_TRANSITIONS: list[TransitionSpec] = [
    TransitionSpec(from_layer=CFK_LAYER_SEQUENCE[i], to_layer=CFK_LAYER_SEQUENCE[i + 1])
    for i in range(len(CFK_LAYER_SEQUENCE) - 1)
]


def propagate_residuals(previous: GateResult, current: GateResult) -> GateResult:
    for residual in previous.residual:
        current.residual.append(
            ResidualObject(
                residual_id=f"prop-{residual.residual_id}",
                residual_type=residual.residual_type,
                severity=residual.severity,
                blocking=residual.blocking,
                propagated_from=residual.residual_id,
            )
        )
    return current


def evaluate_transition(spec: TransitionSpec, result: GateResult) -> GateResult:
    # Score/ranking cannot directly create a certificate.
    if result.ranking.get("score_only_certificate", False):
        result.notes.append("score_threshold_alone_cannot_produce_certificate")
        if result.decision == DecisionLevel.CERTIFICATE:
            result.decision = DecisionLevel.HYPOTHESIS

    # ZERO in path is a local residual, not automatic global zero.
    if any(r.residual_type == "zero_in_path" for r in result.residual) and result.decision == DecisionLevel.ZERO:
        result.notes.append("zero_in_path_is_local_not_global")
        result.decision = DecisionLevel.HYPOTHESIS

    if result.decision == DecisionLevel.CERTIFICATE:
        if spec.gate_contract.requires_evidence_for_certificate and not result.evidence:
            result.notes.append("certificate_blocked_missing_evidence")
            result.decision = DecisionLevel.HYPOTHESIS
        if (
            spec.gate_contract.requires_reverse_trace_for_certificate
            and not result.reverse_trace.path_complete
        ):
            result.notes.append("certificate_blocked_missing_reverse_trace")
            result.decision = DecisionLevel.HYPOTHESIS
        if (
            spec.gate_contract.blocks_certificate_on_blocking_residual
            and result.has_blocking_residual()
        ):
            result.notes.append("certificate_blocked_blocking_residual")
            result.decision = DecisionLevel.HYPOTHESIS
    return result


def current_cfk_proof_obligations() -> CFKProofObligations:
    # Current repository state: strong governed kernel exists, full universal proof track is incomplete.
    return CFKProofObligations(
        layer_registry_complete=True,
        structural_recurrence_verified=True,
        transition_contracts_verified=True,
        certificate_gates_verified=True,
        residual_propagation_verified=True,
        awareness_meta_gate_verified=True,
        reverse_trace_verified=False,
        governance_gate_passed=False,
        proof_object_present=False,
        reverse_trace_reference_present=False,
    )


def resolve_cfk_theorem_status(obligations: CFKProofObligations) -> CFKTheoremStatus:
    core_obligations = [
        obligations.layer_registry_complete,
        obligations.structural_recurrence_verified,
        obligations.transition_contracts_verified,
        obligations.certificate_gates_verified,
        obligations.residual_propagation_verified,
        obligations.awareness_meta_gate_verified,
    ]
    if not any(core_obligations):
        return CFKTheoremStatus.INCOMPLETE
    if not all(core_obligations):
        return CFKTheoremStatus.HYPOTHESIS

    if obligations.reverse_trace_verified:
        if (
            obligations.governance_gate_passed
            and obligations.proof_object_present
            and obligations.reverse_trace_reference_present
        ):
            return CFKTheoremStatus.CERTIFICATE
        return CFKTheoremStatus.CERTIFICATE_CANDIDATE

    return CFKTheoremStatus.STRONG_HYPOTHESIS

