"""ConceptGeometryProjection — CFK integration contract for concept geometry layer.

This layer:
  - can_form_concept = True
  - can_create_evidence = False
  - can_raise_epistemic_certainty = False
  - can_issue_certificate = False
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.cfk_integration_contract import CFKIntegrationContract


# The integration contract for concept geometry
CONCEPT_GEOMETRY_CONTRACT = CFKIntegrationContract(
    source_layer="concept_geometry",
    projection_type="concept_formation",
    allowed_outputs=["concept_formation", "essence_projection", "derivational_projection", "domain_attribution"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty", "factual_certainty"],
    can_create_evidence=False,
    can_raise_epistemic_certainty=False,
    can_set_linguistic_force=False,
    can_change_judgment_operation=False,
    can_raise_syntactic_certainty=False,
    can_raise_factual_certainty=False,
    can_evaluate_evidence=False,
    can_issue_certificate=False,
    required_trace_fields=[],
    required_metadata=[],
    fallback_allowed=True,
)


@dataclass
class KernelProjection:
    """Simplified kernel projection for concept geometry (no CognitiveFractalUnit dependency)."""
    projection_id: str
    source_layer: str
    projection_type: str
    surface: str
    kernel_data: dict = field(default_factory=dict)
    comparable_score: float = 0.0
    can_create_evidence: bool = False
    can_issue_certificate: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "can_create_evidence", False)
        object.__setattr__(self, "can_issue_certificate", False)

    def to_dict(self) -> dict:
        return {
            "projection_id": self.projection_id,
            "source_layer": self.source_layer,
            "projection_type": self.projection_type,
            "surface": self.surface,
            "kernel_data": self.kernel_data,
            "comparable_score": self.comparable_score,
            "can_create_evidence": False,
            "can_issue_certificate": False,
        }


@dataclass
class ConceptGeometryProjection:
    """Projects Jamid/Mushtaq concept geometry into CFK."""
    source_layer: str = "concept_geometry"
    projection_type: str = "concept_formation"
    can_create_evidence: bool = False
    can_raise_epistemic_certainty: bool = False
    can_form_concept: bool = True
    can_issue_certificate: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "can_create_evidence", False)
        object.__setattr__(self, "can_issue_certificate", False)

    def jamid_to_projection(self, jamid_essence) -> KernelProjection:
        """Project JamidEssence into CFK-compatible kernel projection."""
        return KernelProjection(
            projection_id=f"KP-JE-{uuid.uuid4().hex[:8]}",
            source_layer=self.source_layer,
            projection_type="essence_projection",
            surface=jamid_essence.surface,
            kernel_data={
                "essence_type": (
                    jamid_essence.essence_type.value
                    if hasattr(jamid_essence.essence_type, "value")
                    else str(jamid_essence.essence_type)
                ),
                "genus": jamid_essence.genus,
                "species": jamid_essence.species,
                "differentia": jamid_essence.differentia,
                "intrinsic_properties": jamid_essence.intrinsic_properties,
                "essence_vector": jamid_essence.essence_vector,
                "domain_vector": jamid_essence.domain_vector,
                "certainty_policy": jamid_essence.certainty_policy,
                "can_create_evidence": False,
                "can_issue_certificate": False,
            },
            comparable_score=0.5,
        )

    def mushtaq_to_projection(self, mushtaq_unit) -> KernelProjection:
        """Project MushtaqUnit into CFK-compatible kernel projection."""
        return KernelProjection(
            projection_id=f"KP-MU-{uuid.uuid4().hex[:8]}",
            source_layer=self.source_layer,
            projection_type="derivational_projection",
            surface=mushtaq_unit.surface,
            kernel_data={
                "root": mushtaq_unit.root,
                "pattern": mushtaq_unit.pattern,
                "derivation_type": (
                    mushtaq_unit.derivation_type.value
                    if hasattr(mushtaq_unit.derivation_type, "value")
                    else str(mushtaq_unit.derivation_type)
                ),
                "folded_event": mushtaq_unit.folded_event,
                "projected_relation": (
                    mushtaq_unit.projected_relation.value
                    if hasattr(mushtaq_unit.projected_relation, "value")
                    else str(mushtaq_unit.projected_relation)
                ),
                "role_vector": mushtaq_unit.role_vector,
                "certainty_policy": mushtaq_unit.certainty_policy,
                "can_create_evidence": False,
                "can_issue_certificate": False,
                "can_prove_event_occurred": False,
            },
            comparable_score=0.6,
        )

    def concept_center_to_projection(self, concept_center) -> KernelProjection:
        """Project ConceptCenter into CFK-compatible kernel projection."""
        return KernelProjection(
            projection_id=f"KP-CC-{uuid.uuid4().hex[:8]}",
            source_layer=self.source_layer,
            projection_type="concept_formation",
            surface=concept_center.root_family,
            kernel_data=concept_center.to_dict(),
            comparable_score=0.7,
        )

    def validate_against_contract(self, projection: KernelProjection) -> dict:
        """Validate projection against CONCEPT_GEOMETRY_CONTRACT."""
        contract = CONCEPT_GEOMETRY_CONTRACT
        violations = []
        if projection.can_create_evidence:
            violations.append("can_create_evidence must be False")
        if projection.can_issue_certificate:
            violations.append("can_issue_certificate must be False")
        if projection.source_layer != contract.source_layer:
            violations.append(f"source_layer mismatch: {projection.source_layer} != {contract.source_layer}")
        for forbidden in contract.forbidden_outputs:
            if projection.projection_type == forbidden:
                violations.append(f"projection_type '{forbidden}' is forbidden")
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "contract": contract.source_layer,
        }
