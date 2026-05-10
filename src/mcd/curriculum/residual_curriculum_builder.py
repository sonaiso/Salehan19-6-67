"""Residual Curriculum Builder — builds Level 11 examples from mock GPT proposals."""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from typing import Any

from .curriculum_schema import VALID_RESIDUAL_TYPES

GPT_FORBIDDEN = {
    "gpt_as_evidence", "api_as_authority", "tool_as_evidence",
    "llm_as_authority", "gpt_as_truth",
}

RESIDUAL_DETECTION_MAP: dict[str, list[str]] = {
    "all_": ["unsupported_generalization_residual", "certainty_residual"],
    "كل ": ["unsupported_generalization_residual"],
    "دائماً": ["unsupported_generalization_residual", "certainty_residual"],
    "حتماً": ["certainty_residual"],
    "يقيناً": ["certainty_residual"],
    "بالضرورة": ["certainty_residual"],
    "حرام": ["harm_haram_residual"],
    "مباح": ["harm_haram_residual"],
    "تجاهل تعليمات": ["injection_residual"],
    "بلا قيود": ["injection_residual"],
    "api ": ["tool_evidence_residual"],
    "قاعدة البيانات": ["tool_evidence_residual"],
    "gpt ": ["tool_evidence_residual"],
    "النموذج": ["tool_evidence_residual"],
    "مجازاً": ["metaphor_residual"],
    "حرفياً": ["metaphor_residual"],
    "يسبب": ["causality_residual"],
    "بسبب": ["causality_residual"],
}


def _infer_residual_types(gpt_text: str) -> list[str]:
    """Heuristically infer residual types from GPT output text."""
    text_lower = gpt_text.lower()
    found: set[str] = set()
    for trigger, types in RESIDUAL_DETECTION_MAP.items():
        if trigger.lower() in text_lower:
            found.update(types)
    # Default: if nothing detected, use evidence_residual
    if not found:
        found.add("evidence_residual")
    return [r for r in VALID_RESIDUAL_TYPES if r in found]


def _infer_learning_actions(residual_types: list[str]) -> list[str]:
    """Map residual types to learning actions."""
    action_map = {
        "unsupported_generalization_residual": "scope_limitation",
        "certainty_residual": "downgrade_certainty",
        "evidence_residual": "require_evidence",
        "harm_haram_residual": "require_sharia_evidence",
        "tool_evidence_residual": "verify_tool_source",
        "injection_residual": "reject_injection",
        "metaphor_residual": "identify_metaphor",
        "causality_residual": "qualify_causation",
        "structural_residual": "restructure_graph",
        "edge_residual": "verify_relation",
        "vector_residual": "add_domain_vectors",
        "domain_residual": "expand_domain_analysis",
    }
    actions = [action_map[r] for r in residual_types if r in action_map]
    return actions or ["require_evidence"]


def _infer_forbidden_confusions(residual_types: list[str]) -> list[str]:
    """Map residual types to forbidden confusions."""
    confusion_map = {
        "unsupported_generalization_residual": "false_generalization",
        "certainty_residual": "near_certainty_without_evidence",
        "evidence_residual": "gpt_as_evidence",
        "harm_haram_residual": "harm_implies_haram",
        "tool_evidence_residual": "api_as_authority",
        "injection_residual": "injection_bypass",
        "metaphor_residual": "metaphor_as_literal",
        "causality_residual": "correlation_as_causation",
        "structural_residual": "missing_graph",
        "edge_residual": "assumed_relation",
        "vector_residual": "single_domain_vector",
        "domain_residual": "domain_isolation",
    }
    return list({confusion_map[r] for r in residual_types if r in confusion_map})


@dataclass
class ResidualCurriculumUnit:
    unit_id: str
    input_text: str
    mock_gpt_output: str
    proposal_graph: dict[str, Any]
    contract_expected: dict[str, Any]
    expected_residual_types: list[str]
    learning_actions: list[str]
    expected_nodes: list[dict[str, Any]]
    expected_edges: list[dict[str, Any]]
    expected_vectors: list[dict[str, Any]]
    expected_domains: list[str]
    evidence_need: list[str]
    certainty_policy: str
    forbidden_confusions: list[str]
    level: int = 11
    target_layer: str = "cognitive_residual"
    difficulty: str = "hard"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "input_text": self.input_text,
            "level": self.level,
            "target_layer": self.target_layer,
            "mock_gpt_output": self.mock_gpt_output,
            "proposal_graph": self.proposal_graph,
            "contract_expected": self.contract_expected,
            "expected_residual_types": self.expected_residual_types,
            "learning_actions": self.learning_actions,
            "expected_nodes": self.expected_nodes,
            "expected_edges": self.expected_edges,
            "expected_vectors": self.expected_vectors,
            "expected_domains": self.expected_domains,
            "evidence_need": self.evidence_need,
            "certainty_policy": self.certainty_policy,
            "forbidden_confusions": self.forbidden_confusions,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ResidualCurriculumUnit":
        return cls(
            unit_id=d.get("unit_id", str(uuid.uuid4())),
            input_text=d.get("input_text", ""),
            mock_gpt_output=d.get("mock_gpt_output", ""),
            proposal_graph=d.get("proposal_graph", {"nodes": [], "edges": []}),
            contract_expected=d.get("contract_expected", {}),
            expected_residual_types=d.get("expected_residual_types", []),
            learning_actions=d.get("learning_actions", []),
            expected_nodes=d.get("expected_nodes", []),
            expected_edges=d.get("expected_edges", []),
            expected_vectors=d.get("expected_vectors", []),
            expected_domains=d.get("expected_domains", []),
            evidence_need=d.get("evidence_need", []),
            certainty_policy=d.get("certainty_policy", "possible_knowledge"),
            forbidden_confusions=d.get("forbidden_confusions", []),
            level=d.get("level", 11),
            target_layer=d.get("target_layer", "cognitive_residual"),
            difficulty=d.get("difficulty", "hard"),
            tags=d.get("tags", []),
            metadata=d.get("metadata", {}),
        )


@dataclass
class ResidualBuildReport:
    total_proposals: int = 0
    built_units: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    residual_types_covered: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_proposals": self.total_proposals,
            "built_units": self.built_units,
            "skipped": self.skipped,
            "errors": self.errors,
            "residual_types_covered": self.residual_types_covered,
        }


class ResidualCurriculumBuilder:
    """Builds Level 11 curriculum units from mock GPT proposals."""

    def build_from_gpt_proposal(
        self, proposal: dict[str, Any], uid_prefix: str = "L11-BUILT"
    ) -> ResidualCurriculumUnit | None:
        """Build a single ResidualCurriculumUnit from a mock GPT proposal dict."""
        input_text = proposal.get("input_text", "").strip()
        gpt_output = proposal.get("mock_gpt_output", proposal.get("gpt_output", "")).strip()
        if not input_text or not gpt_output:
            return None

        # Use provided residual types or infer them
        residual_types = proposal.get("expected_residual_types") or _infer_residual_types(gpt_output)
        residual_types = [r for r in residual_types if r in VALID_RESIDUAL_TYPES]
        if not residual_types:
            residual_types = ["evidence_residual"]

        learning_actions = proposal.get("learning_actions") or _infer_learning_actions(residual_types)
        forbidden = proposal.get("forbidden_confusions") or _infer_forbidden_confusions(residual_types)
        # Always forbid GPT as evidence
        forbidden = list(set(forbidden) | GPT_FORBIDDEN)

        domains = proposal.get("expected_domains") or ["epistemology"]
        evidence_need = proposal.get("evidence_need") or ["source_verification", "evidence_assessment"]
        certainty = proposal.get("certainty_policy") or "possible_knowledge"

        uid = proposal.get("unit_id") or f"{uid_prefix}-{str(uuid.uuid4())[:8].upper()}"

        # Build or use proposal graph
        pg = proposal.get("proposal_graph") or {
            "nodes": [{"id": "input_concept", "type": "concept"}],
            "edges": [],
        }
        contract = proposal.get("contract_expected") or {
            "certainty_policy": certainty,
            "evidence_need": evidence_need,
            "forbidden_confusions": forbidden,
        }
        expected_nodes = proposal.get("expected_nodes") or [
            {"id": "corrected_concept", "type": "corrected"},
            {"id": "required_evidence", "type": "requirement"},
        ]
        expected_edges = proposal.get("expected_edges") or [
            {"source": "required_evidence", "relation": "required_for", "target": "corrected_concept"}
        ]
        expected_vectors = proposal.get("expected_vectors") or [
            {"dimension": d, "value": 1.0} for d in domains
        ] + [{"dimension": "cognitive_residual", "value": 1.0}]

        tags = list(set(
            ["cognitive_residual", "level_11"] + residual_types[:2] + domains
        ))

        return ResidualCurriculumUnit(
            unit_id=uid,
            input_text=input_text,
            mock_gpt_output=gpt_output,
            proposal_graph=pg,
            contract_expected=contract,
            expected_residual_types=residual_types,
            learning_actions=learning_actions,
            expected_nodes=expected_nodes,
            expected_edges=expected_edges,
            expected_vectors=expected_vectors,
            expected_domains=domains,
            evidence_need=evidence_need,
            certainty_policy=certainty,
            forbidden_confusions=forbidden,
            difficulty="hard",
            tags=tags,
            metadata={"residual_level": 11, "built_from_proposal": True},
        )

    def compute_residual_types(self, gpt_output: str) -> list[str]:
        """Compute residual types from a GPT output string."""
        return _infer_residual_types(gpt_output)

    def residual_to_curriculum_unit(self, proposal: dict[str, Any]) -> ResidualCurriculumUnit | None:
        """Alias for build_from_gpt_proposal for clarity."""
        return self.build_from_gpt_proposal(proposal)

    def residual_to_adversarial_case(self, proposal: dict[str, Any]) -> dict[str, Any] | None:
        """Convert a residual proposal into an adversarial curriculum case."""
        unit = self.build_from_gpt_proposal(proposal)
        if unit is None:
            return None
        return {
            "example_id": f"ADV-RESIDUAL-{unit.unit_id}",
            "input_text": unit.mock_gpt_output,  # The GPT output becomes the adversarial input
            "adversarial_category": unit.expected_residual_types[0] if unit.expected_residual_types else "evidence_residual",
            "expected_detection": unit.learning_actions,
            "forbidden_confusions": unit.forbidden_confusions,
            "expected_certainty_policy": unit.certainty_policy,
            "tags": ["adversarial", "residual_derived"] + unit.expected_residual_types[:2],
        }

    def build_dataset(
        self,
        proposals: list[dict[str, Any]],
        uid_prefix: str = "L11-BUILT",
    ) -> tuple[list[ResidualCurriculumUnit], ResidualBuildReport]:
        """Build a dataset of ResidualCurriculumUnit objects from a list of proposals."""
        report = ResidualBuildReport(total_proposals=len(proposals))
        units: list[ResidualCurriculumUnit] = []
        seen_ids: set[str] = set()

        for proposal in proposals:
            try:
                unit = self.build_from_gpt_proposal(proposal, uid_prefix=uid_prefix)
                if unit is None:
                    report.skipped += 1
                    report.errors.append(f"Skipped proposal: {proposal.get('unit_id', 'unknown')} — missing input_text or gpt_output")
                    continue
                if unit.unit_id in seen_ids:
                    report.skipped += 1
                    continue
                seen_ids.add(unit.unit_id)
                units.append(unit)
                report.built_units += 1
            except Exception as e:  # noqa: BLE001
                report.skipped += 1
                report.errors.append(f"Error building proposal: {e}")

        all_residuals: set[str] = set()
        for u in units:
            all_residuals.update(u.expected_residual_types)
        report.residual_types_covered = sorted(all_residuals)
        return units, report

    def load_proposals(self, path: str) -> list[dict[str, Any]]:
        """Load mock GPT proposals from a JSONL file."""
        proposals: list[dict[str, Any]] = []
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        proposals.append(json.loads(line))
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load proposals from {path}: {e}") from e
        return proposals

    def save_units(self, units: list[ResidualCurriculumUnit], output_path: str) -> None:
        """Save curriculum units to a JSONL file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for unit in units:
                f.write(json.dumps(unit.to_dict(), ensure_ascii=False) + "\n")
