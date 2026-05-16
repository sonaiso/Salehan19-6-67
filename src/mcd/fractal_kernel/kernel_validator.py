from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from .fractal_unit import CognitiveFractalUnit, VALID_LEVELS, VALID_FOLD_STATES
from .vector_space_registry import UnifiedVector, UnifiedVectorSpaceRegistry
from .operator_algebra import CognitiveOperator
from .proof_object import ProofObject
from .reverse_trace import ReverseTrace


@dataclass
class KernelValidationReport:
    passed: bool = False
    unit_validity_score: float = 0.0
    vector_validity_score: float = 0.0
    morphism_validity_score: float = 0.0
    fold_law_score: float = 0.0
    conflict_resolution_score: float = 0.0
    proof_trace_score: float = 0.0
    jami_mani_score: float = 0.0
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def kernel_validation_score(self) -> float:
        scores = [
            self.unit_validity_score,
            self.vector_validity_score,
            self.morphism_validity_score,
            self.fold_law_score,
            self.conflict_resolution_score,
            self.proof_trace_score,
            self.jami_mani_score,
        ]
        return round(sum(scores) / len(scores), 4)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "kernel_validation_score": self.kernel_validation_score,
            "unit_validity_score": self.unit_validity_score,
            "vector_validity_score": self.vector_validity_score,
            "morphism_validity_score": self.morphism_validity_score,
            "fold_law_score": self.fold_law_score,
            "conflict_resolution_score": self.conflict_resolution_score,
            "proof_trace_score": self.proof_trace_score,
            "jami_mani_score": self.jami_mani_score,
            "violations": self.violations,
            "warnings": self.warnings,
        }


class KernelValidator:
    """Validates that fractal kernel components comply with all laws."""

    def __init__(self) -> None:
        self._vec_registry = UnifiedVectorSpaceRegistry()

    def validate_unit(self, unit: CognitiveFractalUnit) -> tuple[bool, list[str]]:
        violations = []
        if not unit.unit_id:
            violations.append("unit_id missing")
        if unit.level not in VALID_LEVELS:
            violations.append(f"invalid level: {unit.level}")
        if not unit.unit_type:
            violations.append("unit_type missing")
        if unit.fold_state not in VALID_FOLD_STATES:
            violations.append(f"invalid fold_state: {unit.fold_state}")
        if not unit.trace_refs and not unit.metadata.get("generated"):
            violations.append(f"unit {unit.unit_id} has no trace_refs and no 'generated' metadata")
        return len(violations) == 0, violations

    def validate_vector(self, vec: UnifiedVector) -> tuple[bool, list[str]]:
        violations = []
        if not vec.source_unit_ids and not vec.source_trace_refs:
            violations.append(f"vector {vec.vector_id} has no source")
        valid, v = self._vec_registry.validate_vector(vec)
        violations.extend(v)
        return len(violations) == 0, violations

    def validate_operator(self, op: CognitiveOperator) -> tuple[bool, list[str]]:
        violations = []
        if op.creates_evidence and op.operator_type != "evidence":
            violations.append(f"operator {op.operator_id}: only 'evidence' type can create evidence")
        return len(violations) == 0, violations

    def validate_proof_object(self, proof: ProofObject,
                               reverse_traces: dict[str, ReverseTrace]) -> tuple[bool, list[str]]:
        violations = []
        if proof.reverse_trace_id is None:
            violations.append(f"proof {proof.proof_id}: no reverse_trace_id")
        elif proof.reverse_trace_id not in reverse_traces:
            violations.append(f"proof {proof.proof_id}: reverse_trace not found")
        else:
            reverse_trace = reverse_traces[proof.reverse_trace_id]
            if proof.proof_status == "certificate" and not reverse_trace.raw_text_units:
                violations.append(f"proof {proof.proof_id}: certificate reverse_trace missing raw_text_units")
        if proof.proof_status == "certificate":
            if not proof.evidence_refs:
                violations.append(f"proof {proof.proof_id}: Certificate requires evidence_refs")
            if proof.blockers:
                violations.append(f"proof {proof.proof_id}: Certificate cannot have blockers")
        return len(violations) == 0, violations

    def run_full_validation(self,
                             units: list[CognitiveFractalUnit] = None,
                             vectors: list[UnifiedVector] = None,
                             operators: list[CognitiveOperator] = None,
                             proofs: list[ProofObject] = None,
                             reverse_traces: dict[str, ReverseTrace] = None) -> KernelValidationReport:
        units = units or []
        vectors = vectors or []
        operators = operators or []
        proofs = proofs or []
        reverse_traces = reverse_traces or {}

        all_violations: list[str] = []
        all_warnings: list[str] = []

        # Validate units
        unit_scores = []
        for u in units:
            ok, v = self.validate_unit(u)
            unit_scores.append(1.0 if ok else 0.0)
            all_violations.extend(v)
        unit_validity_score = sum(unit_scores) / len(unit_scores) if unit_scores else 1.0

        # Validate vectors
        vec_scores = []
        for v in vectors:
            ok, viol = self.validate_vector(v)
            vec_scores.append(1.0 if ok else 0.0)
            all_violations.extend(viol)
        vector_validity_score = sum(vec_scores) / len(vec_scores) if vec_scores else 1.0

        # Validate operators
        op_scores = []
        for op in operators:
            ok, v = self.validate_operator(op)
            op_scores.append(1.0 if ok else 0.0)
            all_violations.extend(v)

        # Check operator creates_evidence=False by default
        for op in operators:
            if op.creates_evidence:
                all_warnings.append(f"operator {op.operator_id} has creates_evidence=True — verify this is intentional")

        # Morphism validity: placeholder 1.0 (checked via registry separately)
        morphism_validity_score = 1.0

        # Fold law score: no proof from fold alone (operators with fold type)
        fold_law_violations = []
        for op in operators:
            if op.operator_type == "fold" and op.creates_evidence:
                fold_law_violations.append(f"fold operator {op.operator_id} cannot create evidence")
        fold_law_score = 1.0 if not fold_law_violations else 0.0
        all_violations.extend(fold_law_violations)

        # Conflict resolution score: placeholder
        conflict_resolution_score = 1.0

        # Proof+trace score
        proof_scores = []
        for p in proofs:
            ok, v = self.validate_proof_object(p, reverse_traces)
            proof_scores.append(1.0 if ok else 0.0)
            all_violations.extend(v)
        proof_trace_score = sum(proof_scores) / len(proof_scores) if proof_scores else 1.0

        # Jami/Mani: placeholder 1.0 (full calculation done by JamiManiCalculator)
        jami_mani_score = 1.0

        report = KernelValidationReport(
            unit_validity_score=round(unit_validity_score, 4),
            vector_validity_score=round(vector_validity_score, 4),
            morphism_validity_score=morphism_validity_score,
            fold_law_score=fold_law_score,
            conflict_resolution_score=conflict_resolution_score,
            proof_trace_score=round(proof_trace_score, 4),
            jami_mani_score=jami_mani_score,
            violations=all_violations,
            warnings=all_warnings,
        )
        report.passed = report.kernel_validation_score >= 0.98 and len(all_violations) == 0
        return report
