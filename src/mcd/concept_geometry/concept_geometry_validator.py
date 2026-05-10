"""ConceptGeometryValidator — validates Phase 8.3 concept geometry layer.

Target: concept_geometry_score >= 0.95
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.concept_geometry.jamid_schema import JamidEssence
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit
from mcd.concept_geometry.concept_center import ConceptCenter
from mcd.concept_geometry.concept_geometry_projection import CONCEPT_GEOMETRY_CONTRACT


@dataclass
class ConceptGeometryValidationReport:
    """Result of concept geometry validation."""
    passed: bool
    concept_geometry_score: float
    cfk_contract_score: float
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "concept_geometry_score": self.concept_geometry_score,
            "cfk_contract_score": self.cfk_contract_score,
            "violations": self.violations,
            "warnings": self.warnings,
            "details": self.details,
        }

    def to_markdown(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [
            "# Phase 8.3 — Concept Geometry Validation Report",
            "",
            f"**Status:** {status}",
            f"**Concept Geometry Score:** {self.concept_geometry_score:.3f}",
            f"**CFK Contract Score:** {self.cfk_contract_score:.3f}",
            "",
        ]
        if self.violations:
            lines += ["## Violations"]
            for v in self.violations:
                lines.append(f"- ❌ {v}")
            lines.append("")
        if self.warnings:
            lines += ["## Warnings"]
            for w in self.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")
        if self.details:
            lines += ["## Details"]
            for k, v in self.details.items():
                lines.append(f"- **{k}**: {v}")
        return "\n".join(lines)


class ConceptGeometryValidator:
    """Validates concept geometry layer against CFK contract and hard rules."""

    def validate(
        self,
        jamid_essences: Optional[list[JamidEssence]] = None,
        mushtaq_units: Optional[list[MushtaqUnit]] = None,
        concept_centers: Optional[list[ConceptCenter]] = None,
    ) -> ConceptGeometryValidationReport:
        jamid_essences = jamid_essences or []
        mushtaq_units = mushtaq_units or []
        concept_centers = concept_centers or []

        violations: list[str] = []
        warnings: list[str] = []

        # Validate JamidEssence hard rules
        for je in jamid_essences:
            if je.can_create_evidence:
                violations.append(f"JamidEssence '{je.surface}': can_create_evidence must be False")
            if je.can_issue_certificate:
                violations.append(f"JamidEssence '{je.surface}': can_issue_certificate must be False")

        # Validate MushtaqUnit hard rules
        for mu in mushtaq_units:
            if mu.can_create_evidence:
                violations.append(f"MushtaqUnit '{mu.surface}': can_create_evidence must be False")
            if mu.can_issue_certificate:
                violations.append(f"MushtaqUnit '{mu.surface}': can_issue_certificate must be False")
            if mu.can_prove_event_occurred:
                violations.append(f"MushtaqUnit '{mu.surface}': can_prove_event_occurred must be False")

        # Validate ConceptCenter hard rules
        for cc in concept_centers:
            if cc.can_create_evidence:
                violations.append(f"ConceptCenter '{cc.concept_id}': can_create_evidence must be False")
            if cc.can_issue_certificate:
                violations.append(f"ConceptCenter '{cc.concept_id}': can_issue_certificate must be False")
            if cc.proof_refs:
                warnings.append(f"ConceptCenter '{cc.concept_id}': proof_refs should be empty (no certificate)")

        # Validate CFK contract
        contract_violations: list[str] = []
        if CONCEPT_GEOMETRY_CONTRACT.can_create_evidence:
            contract_violations.append("contract: can_create_evidence must be False")
        if CONCEPT_GEOMETRY_CONTRACT.can_issue_certificate:
            contract_violations.append("contract: can_issue_certificate must be False")
        if "certificate" not in CONCEPT_GEOMETRY_CONTRACT.forbidden_outputs:
            contract_violations.append("contract: 'certificate' must be in forbidden_outputs")
        if "evidence" not in CONCEPT_GEOMETRY_CONTRACT.forbidden_outputs:
            contract_violations.append("contract: 'evidence' must be in forbidden_outputs")

        violations.extend(contract_violations)

        # Compute scores
        total_checks = max(1, len(jamid_essences) * 2 + len(mushtaq_units) * 3 + len(concept_centers) * 2 + 4)
        passed_checks = total_checks - len(violations)
        concept_geometry_score = max(0.0, min(1.0, passed_checks / total_checks))

        # CFK contract score — always 1.0 unless contract itself is violated
        cfk_contract_score = 1.0 if not contract_violations else 0.0

        # If no inputs but contract passes, score is 1.0
        if not jamid_essences and not mushtaq_units and not concept_centers:
            if not contract_violations:
                concept_geometry_score = 1.0
                cfk_contract_score = 1.0

        passed = len(violations) == 0 and concept_geometry_score >= 0.95

        return ConceptGeometryValidationReport(
            passed=passed,
            concept_geometry_score=concept_geometry_score,
            cfk_contract_score=cfk_contract_score,
            violations=violations,
            warnings=warnings,
            details={
                "jamid_essences_checked": len(jamid_essences),
                "mushtaq_units_checked": len(mushtaq_units),
                "concept_centers_checked": len(concept_centers),
                "contract_layer": CONCEPT_GEOMETRY_CONTRACT.source_layer,
            },
        )

    def quick_validate(self) -> ConceptGeometryValidationReport:
        """Run validation with built-in ontology and known words."""
        from mcd.concept_geometry.jamid_essence_ontology import JamidEssenceOntology
        from mcd.concept_geometry.mushtaq_derivation_engine import MushtaqDerivationEngine
        from mcd.concept_geometry.concept_center import build_concept_center

        ont = JamidEssenceOntology()
        engine = MushtaqDerivationEngine()

        jamid_essences = ont.all_essences()
        mushtaq_words = ["كاتب", "مكتوب", "كتابة", "مكتبة", "كتابي", "عالم", "زارع"]
        mushtaq_units = [engine.analyze(w) for w in mushtaq_words]
        cc = build_concept_center(
            "ك ت ب",
            ["كاتب", "مكتوب", "كتابة"],
            mushtaq_units=mushtaq_units[:3],
        )

        return self.validate(
            jamid_essences=jamid_essences,
            mushtaq_units=mushtaq_units,
            concept_centers=[cc],
        )
