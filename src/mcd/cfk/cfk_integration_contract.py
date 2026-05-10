"""Phase 8.1 — CFK Integration Contract.

Defines the formal contract that each layer must honour when projecting
into the Cognitive Fractal Kernel.  No layer may issue a Certificate
on its own — only CFK (via ProofObject) can do that.

Key rules:
  1. StatisticalTransform  — candidate/proposal only; never evidence.
  2. ArabicSemanticTransform — linguistic force only; never epistemic certainty.
  3. Mabni layer            — operator effects only; never evidence.
  4. Murab layer            — syntactic certainty only; never factual certainty.
  5. EpistemicTransform     — certainty only from evidence_refs.
  6. ProofObjectBuilder     — certificate only if evidence + conservation + reverse_trace pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class CFKIntegrationContract:
    """Formal projection contract for one source layer.

    Attributes
    ----------
    source_layer:
        Identifier of the layer (e.g. "statistical_transform").
    projection_type:
        The kind of projection this layer produces ("candidate",
        "linguistic_force", "operator_effect", "syntactic_certainty",
        "epistemic_certainty", "certificate").
    allowed_outputs:
        Outputs this layer is permitted to produce.
    forbidden_outputs:
        Outputs this layer must never produce.
    can_create_evidence:
        True only for real-world data sources; all transform layers are False.
    can_raise_epistemic_certainty:
        True only for EpistemicTransform (and only when evidence_refs non-empty).
    can_set_linguistic_force:
        True only for ArabicSemanticTransform.
    can_change_judgment_operation:
        True only for Mabni-based operators.
    can_raise_syntactic_certainty:
        True only for Murab (I'rab) layer.
    can_raise_factual_certainty:
        Always False for purely syntactic layers.
    can_evaluate_evidence:
        True only for EpistemicTransform.
    can_issue_certificate:
        True only for ProofObjectBuilder (after full checks).
    required_trace_fields:
        Trace fields that MUST be populated before the projection is valid.
    required_metadata:
        Metadata keys that MUST be present in the unit's metadata dict.
    fallback_allowed:
        If True, the layer may run in lightweight fallback mode (dev only).
        Fallback mode must be recorded in metadata and caps comparable_score.
    """

    source_layer: str
    projection_type: str
    allowed_outputs: list[str] = field(default_factory=list)
    forbidden_outputs: list[str] = field(default_factory=list)

    can_create_evidence: bool = False
    can_raise_epistemic_certainty: bool = False
    can_set_linguistic_force: bool = False
    can_change_judgment_operation: bool = False
    can_raise_syntactic_certainty: bool = False
    can_raise_factual_certainty: bool = False
    can_evaluate_evidence: bool = False
    can_issue_certificate: bool = False

    required_trace_fields: list[str] = field(default_factory=list)
    required_metadata: list[str] = field(default_factory=list)
    fallback_allowed: bool = False

    def to_dict(self) -> dict:
        return {
            "source_layer": self.source_layer,
            "projection_type": self.projection_type,
            "allowed_outputs": self.allowed_outputs,
            "forbidden_outputs": self.forbidden_outputs,
            "can_create_evidence": self.can_create_evidence,
            "can_raise_epistemic_certainty": self.can_raise_epistemic_certainty,
            "can_set_linguistic_force": self.can_set_linguistic_force,
            "can_change_judgment_operation": self.can_change_judgment_operation,
            "can_raise_syntactic_certainty": self.can_raise_syntactic_certainty,
            "can_raise_factual_certainty": self.can_raise_factual_certainty,
            "can_evaluate_evidence": self.can_evaluate_evidence,
            "can_issue_certificate": self.can_issue_certificate,
            "required_trace_fields": self.required_trace_fields,
            "required_metadata": self.required_metadata,
            "fallback_allowed": self.fallback_allowed,
        }


# ---------------------------------------------------------------------------
# Built-in contracts — one per layer
# ---------------------------------------------------------------------------

STATISTICAL_TRANSFORM_CONTRACT = CFKIntegrationContract(
    source_layer="statistical_transform",
    projection_type="candidate",
    allowed_outputs=["candidate", "proposal", "statistical_weight", "statistical_confidence"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty"],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=False,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=False,
    required_trace_fields=["reverse_path"],
    required_metadata=["proposal_id", "proposal_type"],
    fallback_allowed=False,
)

ARABIC_SEMANTIC_TRANSFORM_CONTRACT = CFKIntegrationContract(
    source_layer="arabic_semantic_transform",
    projection_type="linguistic_force",
    allowed_outputs=["linguistic_force", "operator_effect", "syntactic_role", "semantic_weight"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty"],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=True,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=False,
    required_trace_fields=["reverse_path"],
    required_metadata=["linguistic_force", "murab_units_count"],
    fallback_allowed=True,  # murab/mabni may be unavailable in test environments
)

MABNI_CONTRACT = CFKIntegrationContract(
    source_layer="mabni",
    projection_type="operator_effect",
    allowed_outputs=["operator_type", "judgment_operation", "logical_function"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty", "factual_certainty"],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=False,
    can_change_judgment_operation=True,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=False,
    required_trace_fields=[],
    required_metadata=[],
    fallback_allowed=True,
)

MURAB_CONTRACT = CFKIntegrationContract(
    source_layer="murab",
    projection_type="syntactic_certainty",
    allowed_outputs=["syntactic_certainty", "irab_case", "dependency_role"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty", "factual_certainty"],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=False,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=True,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=False,
    required_trace_fields=[],
    required_metadata=[],
    fallback_allowed=True,
)

EPISTEMIC_TRANSFORM_CONTRACT = CFKIntegrationContract(
    source_layer="epistemic_transform",
    projection_type="epistemic_certainty",
    allowed_outputs=["epistemic_certainty", "evidence_evaluation", "certainty_level"],
    forbidden_outputs=["certificate"],  # certificate is for ProofObjectBuilder only
    can_create_evidence=False,
    can_raise_epistemic_certainty=True,  # only when evidence_refs non-empty
    can_set_linguistic_force=False,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=True,
    can_issue_certificate=False,
    required_trace_fields=["reverse_path"],
    required_metadata=["evidence_state", "judgment"],
    fallback_allowed=False,
)

PROOF_OBJECT_BUILDER_CONTRACT = CFKIntegrationContract(
    source_layer="proof_object_builder",
    projection_type="certificate",
    allowed_outputs=["certificate", "hypothesis", "suspend", "zero"],
    forbidden_outputs=[],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=False,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=True,  # only after evidence + conservation + reverse_trace
    required_trace_fields=["reverse_trace_id"],
    required_metadata=[],
    fallback_allowed=False,
)

# Registry — ordered from upstream to downstream
ALL_CONTRACTS: list[CFKIntegrationContract] = [
    STATISTICAL_TRANSFORM_CONTRACT,
    ARABIC_SEMANTIC_TRANSFORM_CONTRACT,
    MABNI_CONTRACT,
    MURAB_CONTRACT,
    EPISTEMIC_TRANSFORM_CONTRACT,
    PROOF_OBJECT_BUILDER_CONTRACT,
]

CONTRACTS_BY_LAYER: dict[str, CFKIntegrationContract] = {
    c.source_layer: c for c in ALL_CONTRACTS
}


# ---------------------------------------------------------------------------
# Validator — checks that a projection respects its contract
# ---------------------------------------------------------------------------

@dataclass
class ContractViolation:
    source_layer: str
    rule: str
    description: str
    severity: str  # "warning" | "error"

    def to_dict(self) -> dict:
        return {
            "source_layer": self.source_layer,
            "rule": self.rule,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class ContractCheckResult:
    source_layer: str
    passed: bool
    violations: list[ContractViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_layer": self.source_layer,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
        }


class ContractValidator:
    """Validates a KernelProjection or unit against its layer contract."""

    def validate_arabic_projection(
        self,
        projection,  # KernelProjection
        contract: CFKIntegrationContract | None = None,
    ) -> ContractCheckResult:
        """Validate an ArabicSemanticTransform projection against its contract."""
        contract = contract or ARABIC_SEMANTIC_TRANSFORM_CONTRACT
        violations: list[ContractViolation] = []

        unit = projection.unit

        # epistemic_certainty must remain 0.0
        if unit.C.epistemic_certainty > 0.0:
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="no_epistemic_certainty",
                description=(
                    f"ArabicSemanticTransform set epistemic_certainty="
                    f"{unit.C.epistemic_certainty:.3f} — contract violation"
                ),
                severity="error",
            ))

        # comparable_score must be ≤ 0.55 when fallback used
        murab_fallback = unit.metadata.get("murab_fallback", False)
        mabni_fallback = unit.metadata.get("mabni_fallback", False)
        if (murab_fallback or mabni_fallback) and projection.comparable_score > 0.55:
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="fallback_score_cap",
                description=(
                    f"Fallback active but comparable_score={projection.comparable_score:.3f} > 0.55"
                ),
                severity="error",
            ))

        # evidence_state must be "missing"
        if unit.E.evidence_state != "missing":
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="no_evidence",
                description=(
                    f"ArabicSemanticTransform set evidence_state="
                    f"'{unit.E.evidence_state}' — only 'missing' is allowed"
                ),
                severity="error",
            ))

        # required metadata keys
        for key in contract.required_metadata:
            if key not in unit.metadata:
                violations.append(ContractViolation(
                    source_layer=contract.source_layer,
                    rule="missing_metadata",
                    description=f"Required metadata key '{key}' not found",
                    severity="warning",
                ))

        return ContractCheckResult(
            source_layer=contract.source_layer,
            passed=len(violations) == 0,
            violations=violations,
        )

    def validate_statistical_projection(
        self,
        projection,  # KernelProjection
        contract: CFKIntegrationContract | None = None,
    ) -> ContractCheckResult:
        """Validate a StatisticalTransform projection against its contract."""
        contract = contract or STATISTICAL_TRANSFORM_CONTRACT
        violations: list[ContractViolation] = []

        unit = projection.unit

        # epistemic_certainty must remain 0.0
        if unit.C.epistemic_certainty > 0.0:
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="no_epistemic_certainty",
                description=(
                    f"StatisticalTransform set epistemic_certainty="
                    f"{unit.C.epistemic_certainty:.3f} — must be 0.0"
                ),
                severity="error",
            ))

        # produces_proof must be False
        if unit.P.produces_proof:
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="no_proof",
                description="StatisticalTransform must not set produces_proof=True",
                severity="error",
            ))

        return ContractCheckResult(
            source_layer=contract.source_layer,
            passed=len(violations) == 0,
            violations=violations,
        )

    def validate_epistemic_projection(
        self,
        projection,  # KernelProjection
        contract: CFKIntegrationContract | None = None,
    ) -> ContractCheckResult:
        """Validate an EpistemicTransform projection against its contract."""
        contract = contract or EPISTEMIC_TRANSFORM_CONTRACT
        violations: list[ContractViolation] = []

        unit = projection.unit

        # If evidence missing, certainty must stay ≤ 0.40
        if unit.E.evidence_state == "missing" and unit.C.epistemic_certainty > 0.40:
            violations.append(ContractViolation(
                source_layer=contract.source_layer,
                rule="evidence_gate",
                description=(
                    f"epistemic_certainty={unit.C.epistemic_certainty:.3f} > 0.40 "
                    "with evidence_state=missing — evidence gate violated"
                ),
                severity="error",
            ))

        # required metadata
        for key in contract.required_metadata:
            if key not in unit.metadata:
                violations.append(ContractViolation(
                    source_layer=contract.source_layer,
                    rule="missing_metadata",
                    description=f"Required metadata key '{key}' not found",
                    severity="warning",
                ))

        return ContractCheckResult(
            source_layer=contract.source_layer,
            passed=len(violations) == 0,
            violations=violations,
        )
