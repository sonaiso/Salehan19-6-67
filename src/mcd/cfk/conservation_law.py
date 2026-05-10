"""Conservation Law checker — Preserve(Unit, Relation, Evidence, Certainty, Trace).

The five conservation laws are:
  1. Unit       — حفظ الوحدة    — identity is preserved across levels
  2. Relation   — حفظ العلاقة   — edges are not lost in composition
  3. Evidence   — حفظ الدليل   — evidence chain is not broken
  4. Certainty  — حفظ اليقين   — certainty cannot jump without cause
  5. Trace      — حفظ التتبع   — every judgment has a reverse path

If a transition violates any law, the result is a ConservationViolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.cfk.cfk_schema import CognitiveFractalUnit


# ---------------------------------------------------------------------------
# Violation schema
# ---------------------------------------------------------------------------

@dataclass
class ConservationViolation:
    law: str          # unit|relation|evidence|certainty|trace
    description: str
    severity: str     # low|medium|high|blocking

    def to_dict(self) -> dict:
        return {
            "law": self.law,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class ConservationCheckResult:
    unit_id: str
    passed: bool
    violations: list[ConservationViolation] = field(default_factory=list)
    conservation_score: float = 1.0

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "conservation_score": round(self.conservation_score, 4),
        }


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class ConservationLawChecker:
    """Checks all five conservation laws against a CognitiveFractalUnit."""

    def check(self, unit: CognitiveFractalUnit) -> ConservationCheckResult:
        violations: list[ConservationViolation] = []

        # Law 1: Unit — node_id and surface must be present
        if not unit.unit_id or not unit.surface:
            violations.append(ConservationViolation(
                law="unit",
                description="unit_id or surface is missing — unit identity lost",
                severity="blocking",
            ))

        if not unit.N.node_id:
            violations.append(ConservationViolation(
                law="unit",
                description="N.node_id is empty — cannot trace unit identity",
                severity="high",
            ))

        # Law 2: Relation — edges must reference valid endpoints (non-empty strings)
        for i, edge in enumerate(unit.R.edges):
            if not edge.get("from") or not edge.get("to") or not edge.get("type"):
                violations.append(ConservationViolation(
                    law="relation",
                    description=f"edge[{i}] has empty from/type/to — relation lost",
                    severity="medium",
                ))

        # Law 3: Evidence — if certainty > 0.6, evidence must not be "missing"
        if (
            unit.C.epistemic_certainty > 0.60
            and unit.E.evidence_state == "missing"
        ):
            violations.append(ConservationViolation(
                law="evidence",
                description=(
                    f"epistemic_certainty={unit.C.epistemic_certainty:.2f} "
                    "but evidence_state=missing — evidence law violated"
                ),
                severity="high",
            ))

        # Law 4: Certainty — certainty cannot be raised by emphasis alone
        if (
            unit.C.linguistic_force == "emphasis"
            and unit.C.epistemic_certainty >= 0.75
            and unit.E.evidence_state == "missing"
        ):
            violations.append(ConservationViolation(
                law="certainty",
                description=(
                    "emphasis_operator used to raise epistemic_certainty "
                    "without evidence — certainty law violated"
                ),
                severity="high",
            ))

        # Law 4b: statistical_confidence alone cannot set epistemic_certainty high
        if (
            unit.V.statistical_weight > 0.80
            and unit.C.epistemic_certainty > 0.70
            and unit.E.evidence_state == "missing"
        ):
            violations.append(ConservationViolation(
                law="certainty",
                description=(
                    "high statistical_confidence without evidence cannot yield "
                    "high epistemic_certainty — certainty law violated"
                ),
                severity="high",
            ))

        # Law 5: Trace — reverse_path must be non-empty for non-trivial claims
        if (
            unit.N.level in ("claim", "sentence", "judgment")
            and not unit.T.reverse_path
        ):
            violations.append(ConservationViolation(
                law="trace",
                description=(
                    f"unit level={unit.N.level} has no reverse_path — trace law violated"
                ),
                severity="medium",
            ))

        # Compute score
        penalty = sum(
            {"low": 0.02, "medium": 0.05, "high": 0.10, "blocking": 0.30}.get(v.severity, 0.05)
            for v in violations
        )
        score = max(0.0, 1.0 - penalty)

        return ConservationCheckResult(
            unit_id=unit.unit_id,
            passed=len(violations) == 0,
            violations=violations,
            conservation_score=score,
        )
