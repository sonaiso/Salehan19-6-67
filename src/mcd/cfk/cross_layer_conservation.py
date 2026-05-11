"""Phase 8.1 — Cross-Layer Conservation Checker.

This module extends intra-unit conservation (conservation_law.py) to verify
that conservation properties hold *across* the pipeline layers:

    UnicodeTrace → ArabicSemanticTransform
    MabniOperator → CFK OperatorsInfo
    MurabUnit     → CFK RelationsInfo
    EvidenceTrace → CFK EvidenceInfo
    CertaintyTrace → CFK CertaintyInfo
    ProofObject   → ReverseTrace

The CrossLayerConservationChecker works from three KernelProjections
(statistical, arabic, epistemic) and verifies cross-layer rules:

1. Universal quantifier without evidence → preserve unsupported_generalization risk.
2. Emphasis (mabni) without evidence → must not be treated as evidence.
3. Murab syntactic certainty → must not raise epistemic certainty alone.
4. Evidence missing → Certificate forbidden.
5. Trace present → can explain but not prove truth.

Target: cross_layer_conservation_score >= 0.95
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.cfk_schema import KernelProjection, JudgmentStatus


# ---------------------------------------------------------------------------
# Report schema
# ---------------------------------------------------------------------------

@dataclass
class CrossLayerViolation:
    check_name: str
    description: str
    severity: str           # "warning" | "error" | "blocking"
    source_layers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "check_name": self.check_name,
            "description": self.description,
            "severity": self.severity,
            "source_layers": self.source_layers,
        }


@dataclass
class CrossLayerConservationReport:
    """Full cross-layer conservation report for one pipeline run."""

    report_id: str
    passed: bool

    unit_preserved: bool = True
    relation_preserved: bool = True
    evidence_preserved: bool = True
    certainty_preserved: bool = True
    trace_preserved: bool = True

    violations: list[CrossLayerViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conservation_score: float = 1.0

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "passed": self.passed,
            "unit_preserved": self.unit_preserved,
            "relation_preserved": self.relation_preserved,
            "evidence_preserved": self.evidence_preserved,
            "certainty_preserved": self.certainty_preserved,
            "trace_preserved": self.trace_preserved,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": self.warnings,
            "conservation_score": round(self.conservation_score, 4),
        }


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class CrossLayerConservationChecker:
    """Validates conservation properties across the three CFK projections."""

    _SEVERITY_PENALTY = {
        "warning": 0.01,
        "error": 0.03,
        "blocking": 0.15,
    }

    def check(
        self,
        statistical: KernelProjection,
        arabic: KernelProjection,
        epistemic: KernelProjection,
        kernel_judgment: str = JudgmentStatus.HYPOTHESIS.value,
    ) -> CrossLayerConservationReport:
        violations: list[CrossLayerViolation] = []
        warnings: list[str] = []

        s_unit = statistical.unit
        a_unit = arabic.unit
        e_unit = epistemic.unit

        evidence_state = e_unit.E.evidence_state
        ling_force = a_unit.C.linguistic_force
        logical_function = a_unit.O.logical_function
        epistemic_certainty = e_unit.C.epistemic_certainty
        stat_confidence = s_unit.C.statistical_confidence
        murab_syntactic = a_unit.metadata.get("syntactic_certainty", "unknown")

        unit_ok = True
        relation_ok = True
        evidence_ok = True
        certainty_ok = True
        trace_ok = True

        # ------------------------------------------------------------------
        # Check 1: Universal quantifier without evidence must preserve risk
        # ------------------------------------------------------------------
        if logical_function == "universal_quantifier" and evidence_state == "missing":
            if kernel_judgment == JudgmentStatus.CERTIFICATE.value:
                violations.append(CrossLayerViolation(
                    check_name="universal_without_evidence",
                    description=(
                        "Universal quantifier detected but evidence is missing. "
                        "Kernel judgment must not be 'certificate' — "
                        "unsupported_generalization risk must be preserved."
                    ),
                    severity="blocking",
                    source_layers=["arabic_semantic_transform", "fractal_kernel"],
                ))
                certainty_ok = False
            else:
                warnings.append(
                    "universal_quantifier + no_evidence → judgment correctly downgraded"
                )

        # ------------------------------------------------------------------
        # Check 2: Emphasis (mabni) without evidence must not be treated as evidence
        # ------------------------------------------------------------------
        if ling_force == "emphasis":
            if e_unit.E.evidence_refs:
                # evidence_refs were added — check they are NOT from mabni alone
                if evidence_state == "present" and epistemic_certainty >= 0.75:
                    # This is only a warning: the evidence might be external
                    warnings.append(
                        "emphasis_force + evidence_present: verify evidence is external, "
                        "not derived from linguistic force alone"
                    )
            if evidence_state == "missing" and kernel_judgment == JudgmentStatus.CERTIFICATE.value:
                violations.append(CrossLayerViolation(
                    check_name="emphasis_without_evidence",
                    description=(
                        "Emphasis operator cannot substitute for evidence. "
                        "Certificate forbidden when evidence is missing."
                    ),
                    severity="blocking",
                    source_layers=["arabic_semantic_transform", "proof_object_builder"],
                ))
                evidence_ok = False

        # ------------------------------------------------------------------
        # Check 3: Murab syntactic certainty must not raise epistemic certainty alone
        # ------------------------------------------------------------------
        if murab_syntactic == "certain_syntactic":
            # Syntactic certainty is present; epistemic must still require evidence
            if evidence_state == "missing" and epistemic_certainty > 0.40:
                violations.append(CrossLayerViolation(
                    check_name="murab_syntactic_not_factual",
                    description=(
                        f"Murab reports certain_syntactic but evidence_state=missing. "
                        f"epistemic_certainty={epistemic_certainty:.3f} > 0.40 is forbidden — "
                        "syntactic certainty ≠ factual certainty."
                    ),
                    severity="error",
                    source_layers=["arabic_semantic_transform", "epistemic_transform"],
                ))
                certainty_ok = False

        # ------------------------------------------------------------------
        # Check 4: Evidence missing → Certificate forbidden
        # ------------------------------------------------------------------
        if evidence_state == "missing" and kernel_judgment == JudgmentStatus.CERTIFICATE.value:
            violations.append(CrossLayerViolation(
                check_name="evidence_missing_no_certificate",
                description=(
                    "evidence_state=missing but kernel_judgment=certificate — "
                    "evidence conservation law violated."
                ),
                severity="blocking",
                source_layers=["epistemic_transform", "fractal_kernel"],
            ))
            evidence_ok = False

        # ------------------------------------------------------------------
        # Check 5: Trace present — can explain but must not substitute for evidence
        # ------------------------------------------------------------------
        has_trace = bool(e_unit.T.reverse_path)
        if has_trace and evidence_state == "missing" and epistemic_certainty > 0.50:
            violations.append(CrossLayerViolation(
                check_name="trace_not_evidence",
                description=(
                    "Reverse trace is present but evidence is missing. "
                    f"epistemic_certainty={epistemic_certainty:.3f} > 0.50 is too high — "
                    "trace completeness does not prove truth."
                ),
                severity="error",
                source_layers=["epistemic_transform"],
            ))
            trace_ok = False

        # ------------------------------------------------------------------
        # Check 6: High statistical confidence without evidence
        # ------------------------------------------------------------------
        if stat_confidence >= 0.80 and evidence_state == "missing":
            if kernel_judgment == JudgmentStatus.CERTIFICATE.value:
                violations.append(CrossLayerViolation(
                    check_name="high_stat_no_evidence",
                    description=(
                        f"statistical_confidence={stat_confidence:.3f} ≥ 0.80 but "
                        "evidence_state=missing — certificate forbidden."
                    ),
                    severity="blocking",
                    source_layers=["statistical_transform", "fractal_kernel"],
                ))
                evidence_ok = False
            else:
                warnings.append(
                    f"high_statistical_confidence={stat_confidence:.3f} without evidence — "
                    "correctly handled as non-certificate"
                )

        # ------------------------------------------------------------------
        # Check 7: Unit identity consistency across projections
        # ------------------------------------------------------------------
        for proj, layer in (
            (statistical, "statistical"),
            (arabic, "arabic"),
            (epistemic, "epistemic"),
        ):
            if not proj.unit.unit_id or not proj.unit.surface:
                violations.append(CrossLayerViolation(
                    check_name="unit_identity",
                    description=f"{layer} projection has empty unit_id or surface",
                    severity="error",
                    source_layers=[layer],
                ))
                unit_ok = False

        # ------------------------------------------------------------------
        # Check 8: Relation edges consistency
        # ------------------------------------------------------------------
        for edge in a_unit.R.edges:
            if not edge.get("from") or not edge.get("to"):
                violations.append(CrossLayerViolation(
                    check_name="relation_edge_integrity",
                    description="Arabic projection has incomplete relation edges",
                    severity="warning",
                    source_layers=["arabic_semantic_transform"],
                ))
                relation_ok = False
                break

        # ------------------------------------------------------------------
        # Compute conservation score
        # ------------------------------------------------------------------
        penalty = sum(
            self._SEVERITY_PENALTY.get(v.severity, 0.03) for v in violations
        )
        score = max(0.0, 1.0 - penalty)

        all_passed = len(violations) == 0

        return CrossLayerConservationReport(
            report_id=f"CLCR-{uuid.uuid4().hex[:10]}",
            passed=all_passed,
            unit_preserved=unit_ok,
            relation_preserved=relation_ok,
            evidence_preserved=evidence_ok,
            certainty_preserved=certainty_ok,
            trace_preserved=trace_ok,
            violations=violations,
            warnings=warnings,
            conservation_score=score,
        )
