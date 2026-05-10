"""Depth metrics for the cognitive curriculum."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "curriculum"
)

REQUIRED_FIELDS = [
    "expected_nodes",
    "expected_edges",
    "expected_vectors",
    "expected_domains",
    "evidence_need",
    "certainty_policy",
    "forbidden_confusions",
]

RESIDUAL_TYPES = [
    "structural_residual", "edge_residual", "vector_residual", "evidence_residual",
    "certainty_residual", "domain_residual", "causality_residual", "metaphor_residual",
    "tool_evidence_residual", "harm_haram_residual", "injection_residual",
    "unsupported_generalization_residual",
]

ADVERSARIAL_CATEGORIES = [
    "false_certainty", "missing_evidence", "false_generalization", "injection_attempt",
    "tool_authority_claim", "metaphor_as_literal", "harm_haram_conflation",
    "correlation_causation", "stale_source", "single_source", "circular_reasoning",
    "appeal_to_authority", "appeal_to_popularity", "cherry_picking", "false_dilemma",
    "slippery_slope", "label_only", "domain_conflation", "vector_collapse",
    "post_hoc_fallacy", "false_equivalence", "hasty_generalization",
]


def _load_all_examples() -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    if not os.path.isdir(DATA_DIR):
        return examples
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".jsonl"):
            fpath = os.path.join(DATA_DIR, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            examples.append(json.loads(line))
            except (OSError, json.JSONDecodeError):
                pass
    return examples


@dataclass
class DepthMetricsReport:
    total_examples: int = 0
    cognitive_depth_score: float = 0.0
    graph_density_score: float = 0.0
    domain_coverage_score: float = 0.0
    residual_richness_score: float = 0.0
    evidence_diversity_score: float = 0.0
    certainty_distribution_score: float = 0.0
    adversarial_strength_score: float = 0.0
    contract_strictness_score: float = 0.0
    learning_value_score: float = 0.0
    curriculum_completeness_score: float = 0.0

    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        # Serialize details, converting any sets to sorted lists
        serialized_details: dict[str, Any] = {}
        for k, v in self.details.items():
            if isinstance(v, set):
                serialized_details[k] = sorted(v)
            else:
                serialized_details[k] = v
        return {
            "total_examples": self.total_examples,
            "cognitive_depth_score": round(self.cognitive_depth_score, 4),
            "graph_density_score": round(self.graph_density_score, 4),
            "domain_coverage_score": round(self.domain_coverage_score, 4),
            "residual_richness_score": round(self.residual_richness_score, 4),
            "evidence_diversity_score": round(self.evidence_diversity_score, 4),
            "certainty_distribution_score": round(self.certainty_distribution_score, 4),
            "adversarial_strength_score": round(self.adversarial_strength_score, 4),
            "contract_strictness_score": round(self.contract_strictness_score, 4),
            "learning_value_score": round(self.learning_value_score, 4),
            "curriculum_completeness_score": round(self.curriculum_completeness_score, 4),
            "details": serialized_details,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Curriculum Depth Metrics Report",
            "",
            f"**Total Examples:** {self.total_examples}",
            "",
            "## Scores",
            "",
            f"| Metric | Score |",
            f"|--------|-------|",
            f"| cognitive_depth_score | {self.cognitive_depth_score:.4f} |",
            f"| graph_density_score | {self.graph_density_score:.4f} |",
            f"| domain_coverage_score | {self.domain_coverage_score:.4f} |",
            f"| residual_richness_score | {self.residual_richness_score:.4f} |",
            f"| evidence_diversity_score | {self.evidence_diversity_score:.4f} |",
            f"| certainty_distribution_score | {self.certainty_distribution_score:.4f} |",
            f"| adversarial_strength_score | {self.adversarial_strength_score:.4f} |",
            f"| contract_strictness_score | {self.contract_strictness_score:.4f} |",
            f"| learning_value_score | {self.learning_value_score:.4f} |",
            f"| curriculum_completeness_score | {self.curriculum_completeness_score:.4f} |",
            "",
        ]
        for k, v in self.details.items():
            lines.append(f"## {k.replace('_', ' ').title()}")
            lines.append("")
            if isinstance(v, dict):
                for dk, dv in v.items():
                    lines.append(f"- **{dk}**: {dv}")
            else:
                lines.append(str(v))
            lines.append("")
        return "\n".join(lines)


class DepthMetricsCalculator:
    """Calculates 10 depth metrics over the curriculum dataset."""

    KNOWN_DOMAINS = {
        "technology", "medicine", "religion", "law", "economics", "social",
        "politics", "ethics", "education", "psychology", "science", "linguistics",
        "management", "philosophy", "history", "biology", "epistemology",
        "logic", "mathematics",
    }
    KNOWN_CERTAINTIES = {
        "certain_knowledge", "near_certainty", "probable_knowledge",
        "possible_knowledge", "insufficient_evidence", "suspend_judgment",
        "strong_knowledge", "hypothesis",
    }

    def calculate(self, examples: list[dict[str, Any]] | None = None) -> DepthMetricsReport:
        if examples is None:
            examples = _load_all_examples()

        report = DepthMetricsReport(total_examples=len(examples))
        if not examples:
            return report

        report.cognitive_depth_score = self._cognitive_depth(examples)
        report.graph_density_score = self._graph_density(examples)
        report.domain_coverage_score = self._domain_coverage(examples)
        report.residual_richness_score = self._residual_richness(examples)
        report.evidence_diversity_score = self._evidence_diversity(examples)
        report.certainty_distribution_score = self._certainty_distribution(examples)
        report.adversarial_strength_score = self._adversarial_strength(examples)
        report.contract_strictness_score = self._contract_strictness(examples)
        report.learning_value_score = self._learning_value(examples)
        report.curriculum_completeness_score = self._curriculum_completeness(examples)

        report.details = {
            "levels_present": self._levels_present(examples),
            "domains_found": self._domains_found(examples),
            "residual_types_found": self._residual_types_found(examples),
        }
        return report

    # ── individual metrics ────────────────────────────────────────────────

    def _cognitive_depth(self, examples: list[dict]) -> float:
        """Fraction of examples with full cognitive structure (nodes+edges+vectors+domains)."""
        total = len(examples)
        if total == 0:
            return 0.0
        full_structure = sum(
            1 for e in examples
            if (e.get("expected_nodes") or e.get("expected_frame", {}).get("nodes"))
            and (e.get("expected_edges") or e.get("expected_frame", {}).get("edges"))
            and (e.get("expected_vectors") or e.get("expected_frame", {}).get("vectors"))
            and (e.get("expected_domains") or e.get("expected_frame", {}).get("domains"))
        )
        return full_structure / total

    def _graph_density(self, examples: list[dict]) -> float:
        """Average ratio of edges to nodes across examples that have graphs."""
        ratios = []
        for e in examples:
            nodes = e.get("expected_nodes") or e.get("expected_frame", {}).get("nodes") or []
            edges = e.get("expected_edges") or e.get("expected_frame", {}).get("edges") or []
            if isinstance(nodes, list) and isinstance(edges, list) and len(nodes) > 0:
                ratios.append(min(len(edges) / len(nodes), 1.0))
        return sum(ratios) / len(ratios) if ratios else 0.0

    def _domain_coverage(self, examples: list[dict]) -> float:
        """Fraction of known domains covered by the curriculum."""
        found = self._domains_found(examples)
        return len(found) / len(self.KNOWN_DOMAINS)

    def _residual_richness(self, examples: list[dict]) -> float:
        """Coverage of residual types in the curriculum."""
        found = self._residual_types_found(examples)
        if not RESIDUAL_TYPES:
            return 1.0
        type_coverage = len(found) / len(RESIDUAL_TYPES)
        # Also weight by fraction of examples that are L11
        l11 = [e for e in examples if e.get("level") == 11]
        example_frac = min(len(l11) / max(1, 0.1 * len(examples)), 1.0)
        return min(0.6 * type_coverage + 0.4 * example_frac, 1.0)

    def _evidence_diversity(self, examples: list[dict]) -> float:
        """Diversity of evidence_need values across curriculum."""
        evidence_types: set[str] = set()
        for e in examples:
            ev = e.get("evidence_need") or e.get("expected_frame", {}).get("evidence_need") or []
            if isinstance(ev, list):
                evidence_types.update(str(x) for x in ev)
        # Score by number of distinct evidence types (cap at 20)
        return min(len(evidence_types) / 20.0, 1.0)

    def _certainty_distribution(self, examples: list[dict]) -> float:
        """How evenly distributed are certainty policies (higher = more diverse)."""
        counts: dict[str, int] = {c: 0 for c in self.KNOWN_CERTAINTIES}
        for e in examples:
            cp = e.get("certainty_policy") or e.get("expected_frame", {}).get("certainty_policy") or e.get("expected_certainty_policy")
            if isinstance(cp, str) and cp in counts:
                counts[cp] += 1
        filled = sum(1 for v in counts.values() if v > 0)
        return filled / len(counts)

    def _adversarial_strength(self, examples: list[dict]) -> float:
        """Strength and coverage of adversarial examples."""
        adv = [e for e in examples if "adversarial" in e.get("tags", [])
               or e.get("difficulty") == "adversarial"
               or e.get("adversarial_category")]
        count_score = min(len(adv) / 500.0, 1.0)
        categories = {e.get("adversarial_category") for e in adv if e.get("adversarial_category")}
        cat_score = min(len(categories) / len(ADVERSARIAL_CATEGORIES), 1.0)
        return 0.5 * count_score + 0.5 * cat_score

    def _contract_strictness(self, examples: list[dict]) -> float:
        """Fraction of examples with all required contract fields."""
        total = len(examples)
        if total == 0:
            return 0.0
        strict = sum(
            1 for e in examples
            if all(e.get(f) for f in REQUIRED_FIELDS)
        )
        return strict / total

    def _learning_value(self, examples: list[dict]) -> float:
        """Fraction of examples with actionable learning_actions (L11)."""
        l11 = [e for e in examples if e.get("level") == 11]
        l12 = [e for e in examples if e.get("level") == 12]
        residual_ok = sum(
            1 for e in l11
            if e.get("learning_actions") and e.get("expected_residual_types")
        )
        mixed_ok = sum(
            1 for e in l12
            if e.get("metadata", {}).get("mixed_factors")
        )
        if not l11 and not l12:
            return 0.5
        total_advanced = len(l11) + len(l12)
        return (residual_ok + mixed_ok) / total_advanced if total_advanced > 0 else 0.5

    def _curriculum_completeness(self, examples: list[dict]) -> float:
        """Overall completeness: all 12 levels present, counts met, fields filled."""
        levels_present = self._levels_present(examples)
        level_score = len(levels_present) / 12.0
        count_score = min(len(examples) / 3000.0, 1.0)
        field_score = self._contract_strictness(examples)
        adv_score = self._adversarial_strength(examples)
        return 0.3 * level_score + 0.2 * count_score + 0.3 * field_score + 0.2 * adv_score

    # ── helpers ───────────────────────────────────────────────────────────

    def _levels_present(self, examples: list[dict]) -> list[int]:
        return sorted({e.get("level") for e in examples if isinstance(e.get("level"), int)})

    def _domains_found(self, examples: list[dict]) -> set[str]:
        found: set[str] = set()
        for e in examples:
            domains = e.get("expected_domains") or []
            if isinstance(domains, list):
                found.update(str(d) for d in domains if isinstance(d, str))
        return found & self.KNOWN_DOMAINS

    def _residual_types_found(self, examples: list[dict]) -> set[str]:
        found: set[str] = set()
        for e in examples:
            rts = e.get("expected_residual_types") or []
            if isinstance(rts, list):
                found.update(str(r) for r in rts)
        return found & set(RESIDUAL_TYPES)
