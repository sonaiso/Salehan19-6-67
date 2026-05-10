"""Curriculum Coverage Matrix — computes coverage across all curriculum dimensions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "curriculum"
)

KNOWN_LEVELS = list(range(1, 13))
KNOWN_DOMAINS = [
    "technology", "medicine", "religion", "law", "economics", "social",
    "politics", "ethics", "education", "psychology", "science", "linguistics",
    "management", "philosophy", "history", "biology", "epistemology",
    "logic", "mathematics",
]
KNOWN_NODE_TYPES = [
    "concept", "action", "property", "relation", "evidence", "agent", "patient",
    "instrument", "time", "place", "cause", "effect", "claim", "tool",
    "requirement", "authority", "judgment", "domain_concept", "generalization",
    "metaphor", "stale_source", "contaminated_input", "complex_case",
]
KNOWN_EDGE_TYPES = [
    "is_a", "has", "causes", "requires", "supports", "contradicts",
    "is_not", "enables", "leads_to", "not_substitute_for", "requires_evidence_for",
    "involves", "based_on", "derived_from", "conflicts_with", "is_part_of",
    "associated_with", "produces", "prevents", "outdated_for",
]
KNOWN_VECTOR_DIMS = list(KNOWN_DOMAINS) + ["cognitive_residual", "mixed_deep_reasoning", "graph_vector"]
KNOWN_EVIDENCE_TYPES = [
    "empirical_survey", "industry_data", "quran_text", "authenticated_hadith",
    "scholarly_consensus", "source_verification", "data_validation",
    "contextual_analysis", "metaphor_identification", "injection_detection",
    "replication", "systematic_review", "medical_consensus_data", "guideline_review",
    "longitudinal_study", "graph_construction", "vector_composition",
    "multi_source", "domain_expert", "causal_analysis", "conflict_resolution",
    "evidence_strength_assessment",
]
KNOWN_CERTAINTY_POLICIES = [
    "certain_knowledge", "near_certainty", "probable_knowledge",
    "possible_knowledge", "insufficient_evidence", "suspend_judgment",
    "strong_knowledge", "hypothesis",
]
KNOWN_RESIDUAL_TYPES = [
    "structural_residual", "edge_residual", "vector_residual", "evidence_residual",
    "certainty_residual", "domain_residual", "causality_residual", "metaphor_residual",
    "tool_evidence_residual", "harm_haram_residual", "injection_residual",
    "unsupported_generalization_residual",
]
KNOWN_FORBIDDEN_CONFUSIONS = [
    "gpt_as_evidence", "api_as_authority", "label_only", "missing_graph",
    "missing_vectors", "false_generalization", "near_certainty_without_evidence",
    "metaphor_as_literal", "harm_implies_haram", "tool_as_evidence",
    "stale_source_as_current", "correlation_as_causation", "single_source_certainty",
    "domain_blind_spot", "injection_bypass",
]
KNOWN_DIFFICULTIES = ["easy", "medium", "hard", "adversarial"]


def _load_all_examples(data_dir: str = DATA_DIR) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    if not os.path.isdir(data_dir):
        return examples
    for fname in sorted(os.listdir(data_dir)):
        if fname.endswith(".jsonl"):
            fpath = os.path.join(data_dir, fname)
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
class CurriculumCoverageReport:
    total_examples: int = 0
    coverage_by_level: dict[int, int] = field(default_factory=dict)
    coverage_by_domain: dict[str, int] = field(default_factory=dict)
    coverage_by_node_type: dict[str, int] = field(default_factory=dict)
    coverage_by_edge_type: dict[str, int] = field(default_factory=dict)
    coverage_by_vector_dim: dict[str, int] = field(default_factory=dict)
    coverage_by_evidence_type: dict[str, int] = field(default_factory=dict)
    coverage_by_certainty_policy: dict[str, int] = field(default_factory=dict)
    coverage_by_residual_type: dict[str, int] = field(default_factory=dict)
    coverage_by_forbidden_confusion: dict[str, int] = field(default_factory=dict)
    coverage_by_difficulty: dict[str, int] = field(default_factory=dict)
    missing_coverage: dict[str, list[str]] = field(default_factory=dict)
    underrepresented_areas: list[str] = field(default_factory=list)
    curriculum_completeness_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_examples": self.total_examples,
            "coverage_by_level": self.coverage_by_level,
            "coverage_by_domain": self.coverage_by_domain,
            "coverage_by_node_type": self.coverage_by_node_type,
            "coverage_by_edge_type": self.coverage_by_edge_type,
            "coverage_by_vector_dim": self.coverage_by_vector_dim,
            "coverage_by_evidence_type": self.coverage_by_evidence_type,
            "coverage_by_certainty_policy": self.coverage_by_certainty_policy,
            "coverage_by_residual_type": self.coverage_by_residual_type,
            "coverage_by_forbidden_confusion": self.coverage_by_forbidden_confusion,
            "coverage_by_difficulty": self.coverage_by_difficulty,
            "missing_coverage": self.missing_coverage,
            "underrepresented_areas": self.underrepresented_areas,
            "curriculum_completeness_score": round(self.curriculum_completeness_score, 4),
        }

    def to_markdown(self) -> str:
        lines = [
            "# Curriculum Coverage Report",
            "",
            f"**Total Examples:** {self.total_examples}",
            f"**Completeness Score:** {self.curriculum_completeness_score:.4f}",
            "",
            "## Coverage by Level",
            "",
        ]
        for lvl in sorted(self.coverage_by_level):
            lines.append(f"- Level {lvl}: {self.coverage_by_level[lvl]} examples")
        lines.extend(["", "## Coverage by Domain", ""])
        for dom in sorted(self.coverage_by_domain, key=lambda d: -self.coverage_by_domain[d]):
            lines.append(f"- {dom}: {self.coverage_by_domain[dom]}")
        lines.extend(["", "## Coverage by Residual Type", ""])
        for rt in sorted(self.coverage_by_residual_type, key=lambda r: -self.coverage_by_residual_type[r]):
            lines.append(f"- {rt}: {self.coverage_by_residual_type[rt]}")
        if self.missing_coverage:
            lines.extend(["", "## Missing Coverage", ""])
            for dim, missing in self.missing_coverage.items():
                if missing:
                    lines.append(f"- **{dim}**: {', '.join(missing[:5])}" + (" ..." if len(missing) > 5 else ""))
        if self.underrepresented_areas:
            lines.extend(["", "## Underrepresented Areas", ""])
            for area in self.underrepresented_areas:
                lines.append(f"- {area}")
        return "\n".join(lines)


class CurriculumCoverageMatrix:
    """Computes coverage matrix across all curriculum dimensions."""

    UNDER_THRESHOLD = 5  # Examples below this count → underrepresented

    def compute(self, examples: list[dict[str, Any]] | None = None) -> CurriculumCoverageReport:
        if examples is None:
            examples = _load_all_examples()

        report = CurriculumCoverageReport(total_examples=len(examples))

        # by level
        for lvl in KNOWN_LEVELS:
            report.coverage_by_level[lvl] = sum(1 for e in examples if e.get("level") == lvl)

        # by domain
        for dom in KNOWN_DOMAINS:
            report.coverage_by_domain[dom] = sum(
                1 for e in examples
                if dom in (e.get("expected_domains") or [])
            )

        # by node type
        for ntype in KNOWN_NODE_TYPES:
            report.coverage_by_node_type[ntype] = sum(
                1 for e in examples
                if any(n.get("type") == ntype for n in (e.get("expected_nodes") or []))
            )

        # by edge type
        for etype in KNOWN_EDGE_TYPES:
            report.coverage_by_edge_type[etype] = sum(
                1 for e in examples
                if any(ed.get("relation") == etype for ed in (e.get("expected_edges") or []))
            )

        # by vector dim
        for vdim in KNOWN_VECTOR_DIMS:
            report.coverage_by_vector_dim[vdim] = sum(
                1 for e in examples
                if any(v.get("dimension") == vdim for v in (e.get("expected_vectors") or []))
            )

        # by evidence type
        for etype in KNOWN_EVIDENCE_TYPES:
            report.coverage_by_evidence_type[etype] = sum(
                1 for e in examples
                if etype in (e.get("evidence_need") or [])
            )

        # by certainty policy
        for cp in KNOWN_CERTAINTY_POLICIES:
            report.coverage_by_certainty_policy[cp] = sum(
                1 for e in examples if e.get("certainty_policy") == cp
            )

        # by residual type
        for rt in KNOWN_RESIDUAL_TYPES:
            report.coverage_by_residual_type[rt] = sum(
                1 for e in examples
                if rt in (e.get("expected_residual_types") or [])
            )

        # by forbidden confusion
        for fc in KNOWN_FORBIDDEN_CONFUSIONS:
            report.coverage_by_forbidden_confusion[fc] = sum(
                1 for e in examples
                if fc in (e.get("forbidden_confusions") or [])
            )

        # by difficulty
        for diff in KNOWN_DIFFICULTIES:
            report.coverage_by_difficulty[diff] = sum(
                1 for e in examples if e.get("difficulty") == diff
            )

        # missing coverage
        missing: dict[str, list[str]] = {}
        missing["levels"] = [str(lvl) for lvl in KNOWN_LEVELS if report.coverage_by_level.get(lvl, 0) == 0]
        missing["domains"] = [d for d in KNOWN_DOMAINS if report.coverage_by_domain.get(d, 0) == 0]
        missing["node_types"] = [n for n in KNOWN_NODE_TYPES if report.coverage_by_node_type.get(n, 0) == 0]
        missing["edge_types"] = [e for e in KNOWN_EDGE_TYPES if report.coverage_by_edge_type.get(e, 0) == 0]
        missing["residual_types"] = [r for r in KNOWN_RESIDUAL_TYPES if report.coverage_by_residual_type.get(r, 0) == 0]
        missing["certainty_policies"] = [c for c in KNOWN_CERTAINTY_POLICIES if report.coverage_by_certainty_policy.get(c, 0) == 0]
        report.missing_coverage = {k: v for k, v in missing.items() if v}

        # underrepresented
        under: list[str] = []
        for lvl in KNOWN_LEVELS:
            if 0 < report.coverage_by_level.get(lvl, 0) < self.UNDER_THRESHOLD:
                under.append(f"level_{lvl} (only {report.coverage_by_level[lvl]} examples)")
        for dom in KNOWN_DOMAINS:
            if 0 < report.coverage_by_domain.get(dom, 0) < self.UNDER_THRESHOLD:
                under.append(f"domain:{dom} (only {report.coverage_by_domain[dom]} examples)")
        for rt in KNOWN_RESIDUAL_TYPES:
            if 0 < report.coverage_by_residual_type.get(rt, 0) < self.UNDER_THRESHOLD:
                under.append(f"residual:{rt} (only {report.coverage_by_residual_type[rt]} examples)")
        report.underrepresented_areas = under

        # completeness score
        level_cov = sum(1 for lvl in KNOWN_LEVELS if report.coverage_by_level.get(lvl, 0) > 0) / len(KNOWN_LEVELS)
        domain_cov = sum(1 for d in KNOWN_DOMAINS if report.coverage_by_domain.get(d, 0) > 0) / len(KNOWN_DOMAINS)
        residual_cov = sum(1 for r in KNOWN_RESIDUAL_TYPES if report.coverage_by_residual_type.get(r, 0) > 0) / len(KNOWN_RESIDUAL_TYPES)
        certainty_cov = sum(1 for c in KNOWN_CERTAINTY_POLICIES if report.coverage_by_certainty_policy.get(c, 0) > 0) / len(KNOWN_CERTAINTY_POLICIES)
        count_score = min(report.total_examples / 3000.0, 1.0)
        report.curriculum_completeness_score = (
            0.25 * level_cov + 0.20 * domain_cov + 0.20 * residual_cov
            + 0.15 * certainty_cov + 0.20 * count_score
        )
        return report
