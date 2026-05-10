from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

CONFLICT_TYPES = {
    "syntactic_vs_factual_certainty",
    "emphasis_vs_evidence",
    "trace_vs_truth",
    "operator_vs_proof",
    "mabni_vs_murab",
    "morphosemantic_vs_context",
    "evidence_conflict",
    "certainty_conflict",
}

# Priority rules: which layer wins in which domain
LAYER_PRIORITY = {
    "factual_certainty": "evidence",
    "syntactic_certainty": "murab",
    "judgment_operation": "mabni",
    "relational_position": "murab",
    "concept_formation": "morphosemantics",
    "explainability": "trace",
    "proof": "proof",
    "emphasis": "mabni",
}


@dataclass
class CrossLayerConflict:
    conflict_id: str
    involved_layers: list[str]
    conflict_type: str
    description: str = ""
    resolution_policy: str = ""
    winning_layer: str = ""
    certainty_effect: str = "none"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "conflict_id": self.conflict_id,
            "involved_layers": self.involved_layers,
            "conflict_type": self.conflict_type,
            "description": self.description,
            "resolution_policy": self.resolution_policy,
            "winning_layer": self.winning_layer,
            "certainty_effect": self.certainty_effect,
            "warnings": self.warnings,
        }


class CrossLayerConflictResolver:
    """Resolves conflicts between layers according to kernel rules."""

    RULES = {
        "emphasis_vs_evidence": {
            "winning_layer": "evidence",
            "resolution_policy": "evidence_beats_emphasis",
            "certainty_effect": "none",
            "warnings": ["Emphasis cannot substitute for evidence"],
        },
        "syntactic_vs_factual_certainty": {
            "winning_layer": "evidence",
            "resolution_policy": "accept_syntactic_suspend_factual",
            "certainty_effect": "suspend_factual",
            "warnings": ["Syntactic certainty ≠ factual certainty"],
        },
        "trace_vs_truth": {
            "winning_layer": "evidence",
            "resolution_policy": "trace_explains_not_proves",
            "certainty_effect": "none",
            "warnings": ["Trace completeness ≠ truth"],
        },
        "operator_vs_proof": {
            "winning_layer": "proof",
            "resolution_policy": "proof_beats_operator",
            "certainty_effect": "none",
            "warnings": ["Operator application ≠ proof"],
        },
        "mabni_vs_murab": {
            "winning_layer": "context",
            "resolution_policy": "mabni_controls_judgment_murab_controls_position",
            "certainty_effect": "none",
            "warnings": [],
        },
        "morphosemantic_vs_context": {
            "winning_layer": "context",
            "resolution_policy": "context_can_override_pattern_candidate",
            "certainty_effect": "none",
            "warnings": [],
        },
        "evidence_conflict": {
            "winning_layer": "evidence",
            "resolution_policy": "strongest_evidence_wins",
            "certainty_effect": "cap",
            "warnings": ["Conflicting evidence detected"],
        },
        "certainty_conflict": {
            "winning_layer": "evidence",
            "resolution_policy": "lower_certainty_wins",
            "certainty_effect": "lower",
            "warnings": ["Certainty conflict: applying conservative policy"],
        },
    }

    def resolve(self, conflict_type: str, involved_layers: list[str],
                description: str = "") -> CrossLayerConflict:
        if conflict_type not in CONFLICT_TYPES:
            raise ValueError(f"Unknown conflict type: {conflict_type}")
        rule = self.RULES.get(conflict_type, {})
        conflict_id = f"CONFLICT-{uuid.uuid4().hex[:8]}"
        return CrossLayerConflict(
            conflict_id=conflict_id,
            involved_layers=involved_layers,
            conflict_type=conflict_type,
            description=description,
            resolution_policy=rule.get("resolution_policy", "unknown"),
            winning_layer=rule.get("winning_layer", "unknown"),
            certainty_effect=rule.get("certainty_effect", "none"),
            warnings=rule.get("warnings", []).copy(),
        )

    def check_emphasis_is_evidence(self, is_emphasis: bool, has_independent_evidence: bool) -> tuple[bool, list[str]]:
        """Return (is_valid, warnings)."""
        if is_emphasis and not has_independent_evidence:
            return False, ["emphasis_not_evidence: emphasis operator cannot substitute for independent evidence"]
        return True, []

    def check_irab_is_factual(self, irab_applied: bool, has_factual_evidence: bool) -> tuple[bool, list[str]]:
        if irab_applied and not has_factual_evidence:
            return True, ["irab_not_factual_certainty: syntactic I'rab does not establish factual certainty"]
        return True, []

    def check_gpt_as_evidence(self, is_gpt_output: bool) -> tuple[bool, list[str]]:
        if is_gpt_output:
            return False, ["gpt_not_evidence: GPT output cannot serve as factual evidence"]
        return True, []
