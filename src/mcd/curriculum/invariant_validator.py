"""InvariantValidator — reads cognitive_invariants.json and validates CognitiveUnits."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .cognitive_graph import CognitiveGraph

_CONTRACTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "contracts"


def _load_invariants() -> list[dict]:
    path = _CONTRACTS_DIR / "cognitive_invariants.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("invariants", [])
    return []


INVARIANTS: list[dict] = _load_invariants()


@dataclass
class InvariantViolation:
    invariant_id: str
    description: str
    severity: str

    def to_dict(self) -> dict:
        return {
            "invariant_id": self.invariant_id,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class InvariantValidationResult:
    passed: bool
    violations: list[InvariantViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 1.0
    pass_rate: float = 1.0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": self.warnings,
            "score": round(self.score, 4),
            "pass_rate": round(self.pass_rate, 4),
        }


def validate_invariants(graph: CognitiveGraph, has_graph_nodes: bool = True) -> InvariantValidationResult:
    """Check all invariants against a CognitiveGraph."""
    violations: list[InvariantViolation] = []
    warnings: list[str] = []

    node_ids = graph.node_ids()

    for inv in INVARIANTS:
        inv_id = inv["id"]
        check = inv.get("check", "")
        desc = inv.get("description", "")
        severity = inv.get("severity", "blocking")

        passed_check = True

        if check == "has_graph_nodes":
            passed_check = len(graph.nodes) > 0

        elif check == "edge_endpoints_in_graph":
            for edge in graph.edges:
                if edge.source not in node_ids or edge.target not in node_ids:
                    passed_check = False
                    break

        elif check == "cause_has_effect":
            cause_edges = [e for e in graph.edges if e.relation == "causes"]
            for ce in cause_edges:
                effect_edges = [e for e in graph.edges if e.source == ce.target or e.relation == "caused_by"]
                if not effect_edges:
                    warnings.append(f"cause node '{ce.source}' may lack explicit effect (INV-003)")

        elif check == "near_certainty_has_evidence":
            if graph.certainty_policy == "near_certainty":
                has_ev = any(n.evidence_refs for n in graph.nodes)
                passed_check = has_ev

        elif check == "tool_api_not_standalone_evidence":
            tool_nodes = {n.node_id for n in graph.nodes if n.node_type in ("tool", "source")}
            for edge in graph.edges:
                if edge.relation == "supports" and edge.source in tool_nodes and not edge.evidence_refs:
                    passed_check = False
                    warnings.append(f"tool/source node '{edge.source}' used as evidence without trust policy (INV-005)")
                    break

        elif check == "harm_haram_not_conflated":
            harm_nodes = {n.node_id for n in graph.nodes if "harm" in n.surface.lower() or "ضار" in n.surface}
            haram_nodes = {n.node_id for n in graph.nodes if "haram" in n.surface.lower() or "حرام" in n.surface}
            for edge in graph.edges:
                if edge.relation == "entails" and edge.source in harm_nodes and edge.target in haram_nodes:
                    passed_check = False
                    break

        elif check == "ambiguity_caps_certainty":
            has_ambiguity = "ambiguous" in graph.warnings or "ambiguity" in graph.warnings
            if has_ambiguity and graph.certainty_policy == "near_certainty":
                passed_check = False

        elif check == "metaphor_not_literal":
            metaphor_nodes = {n.node_id for n in graph.nodes if "metaphor" in n.metadata or "مجاز" in n.surface}
            if metaphor_nodes and "metaphor_treated_as_literal" in graph.warnings:
                passed_check = False
                warnings.append("metaphor treated as literal (INV-008)")

        elif check == "source_trust_required":
            for edge in graph.edges:
                if edge.relation == "sourced_from" and not edge.evidence_refs and not edge.metadata.get("trust_policy"):
                    warnings.append(f"edge '{edge.edge_id}' sourced_from without trust policy (INV-009)")

        elif check == "graph_json_serializable":
            passed_check = graph.is_json_serializable()

        elif check == "vector_matches_registry":
            # Checked externally by VectorValidator
            pass

        elif check == "domain_judgment_has_domain_vector":
            judgment_nodes = [n for n in graph.nodes if n.node_type == "judgment"]
            for jn in judgment_nodes:
                if not jn.domain_vector:
                    passed_check = False
                    warnings.append(f"judgment node '{jn.node_id}' missing domain_vector (INV-012)")
                    break

        if not passed_check:
            violations.append(InvariantViolation(
                invariant_id=inv_id,
                description=desc,
                severity=severity,
            ))

    total = len(INVARIANTS)
    failed = len(violations)
    pass_rate = (total - failed) / total if total > 0 else 1.0
    score = pass_rate
    passed = failed == 0

    return InvariantValidationResult(
        passed=passed,
        violations=violations,
        warnings=warnings,
        score=score,
        pass_rate=pass_rate,
    )
