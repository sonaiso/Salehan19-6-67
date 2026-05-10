"""TraceContributionMatrix — Phase 7.1.3.

Computes the contribution of every UnicodeTraceUnit / TokenTrace to
the final cognitive judgment.  Each semantic unit is tracked as:

  contributes_to_token_boundary | node | edge | evidence |
  certainty | warning | final_decision

This ensures no semantic unit is "orphaned" — every character participates
in the trace chain with an explicit role.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.traceability.trace_builder import (
    TraceBundle,
    _AMBIGUOUS_TERMS,
    _UNIVERSAL_QUANTIFIERS,
    _MISSING_EVIDENCE_SIGNAL_WORDS,
    _MISSING_EVIDENCE_BIGRAMS,
    _INJECTION_SIGNALS,
    _API_SOURCE_TOKENS,
    _METAPHOR_PAIRS,
)

# Alias for injection detection (single-token check)
_INJECTION_TOKENS = _INJECTION_SIGNALS

# All recognised contribution types
CONTRIBUTION_TYPES = [
    "contributes_to_token_boundary",
    "contributes_to_node",
    "contributes_to_edge",
    "contributes_to_evidence",
    "contributes_to_certainty",
    "contributes_to_warning",
    "contributes_to_final_decision",
]


@dataclass
class TraceContribution:
    """Contribution record for a single token / unicode unit."""

    trace_id: str
    token_id: str
    surface: str
    contribution_types: list[str]
    target_ids: list[str]
    contribution_weight: float
    explanation: str
    is_orphan: bool = False

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "token_id": self.token_id,
            "surface": self.surface,
            "contribution_types": self.contribution_types,
            "target_ids": self.target_ids,
            "contribution_weight": round(self.contribution_weight, 4),
            "explanation": self.explanation,
            "is_orphan": self.is_orphan,
        }


@dataclass
class TraceContributionMatrix:
    """Full contribution matrix for one input text."""

    input_text: str
    contributions: list[TraceContribution] = field(default_factory=list)
    coverage_score: float = 0.0
    decision_support_score: float = 0.0
    orphan_semantic_units: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "input_text": self.input_text,
            "contributions": [c.to_dict() for c in self.contributions],
            "coverage_score": round(self.coverage_score, 4),
            "decision_support_score": round(self.decision_support_score, 4),
            "orphan_semantic_units": self.orphan_semantic_units,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Trace Contribution Matrix",
            "",
            f"**Input:** `{self.input_text}`",
            "",
            f"| Score | Value |",
            f"|-------|-------|",
            f"| coverage_score | {self.coverage_score:.4f} |",
            f"| decision_support_score | {self.decision_support_score:.4f} |",
            f"| total contributions | {len(self.contributions)} |",
            f"| orphan units | {len(self.orphan_semantic_units)} |",
            "",
            "## Contributions",
            "",
            "| Surface | Types | Weight | Orphan |",
            "|---------|-------|--------|--------|",
        ]
        for c in self.contributions:
            types = ", ".join(c.contribution_types) or "-"
            lines.append(
                f"| `{c.surface}` | {types} | {c.contribution_weight:.3f} | "
                f"{'⚠️' if c.is_orphan else '✅'} |"
            )
        return "\n".join(lines)


class ContributionMatrixBuilder:
    """Builds a TraceContributionMatrix from a TraceBundle."""

    def build(self, bundle: TraceBundle) -> TraceContributionMatrix:
        contributions: list[TraceContribution] = []

        jt = bundle.judgment_trace
        ev = bundle.evidence_traces[0] if bundle.evidence_traces else None
        ct = bundle.certainty_trace

        # Build lookup structures
        node_link_by_token: dict[str, list[str]] = {}  # token_id → [node_id]
        for nl in bundle.node_links:
            for tid in nl.token_ids:
                node_link_by_token.setdefault(tid, []).append(nl.node_id)

        edge_link_by_token: dict[str, list[str]] = {}  # token_id → [edge_id]
        for el in bundle.edge_links:
            for tid in el.supporting_token_ids:
                edge_link_by_token.setdefault(tid, []).append(el.edge_id)

        vector_ids = [vt.vector_id for vt in bundle.vector_traces]

        # Precompute word set for signal detection
        word_list = [t.normalized.strip().lower() for t in bundle.tokens if t.normalized.strip()]
        word_set = set(word_list)

        total_semantic = 0
        semantic_with_contribution = 0

        for tok in bundle.tokens:
            tok_id = tok.token_id
            surface = tok.surface
            norm = tok.normalized.strip().lower()
            contrib_types: list[str] = []
            target_ids: list[str] = []
            explanation_parts: list[str] = []

            is_whitespace = tok.token_type == "whitespace"
            is_punctuation = tok.token_type == "punctuation"

            # 1. Token boundary contribution (all tokens)
            contrib_types.append("contributes_to_token_boundary")
            target_ids.append(tok_id)
            explanation_parts.append(f"Forms token boundary (type={tok.token_type})")

            # 2. Node contribution
            node_ids = node_link_by_token.get(tok_id, [])
            if node_ids:
                contrib_types.append("contributes_to_node")
                target_ids.extend(node_ids)
                explanation_parts.append(f"Linked to node(s): {node_ids}")

            # 3. Edge contribution
            edge_ids = edge_link_by_token.get(tok_id, [])
            if edge_ids:
                contrib_types.append("contributes_to_edge")
                target_ids.extend(edge_ids)
                explanation_parts.append(f"Supports edge(s): {edge_ids}")

            # 4. Evidence contribution
            contributes_to_evidence = False

            # Missing evidence signals
            if norm in _MISSING_EVIDENCE_SIGNAL_WORDS:
                contributes_to_evidence = True
                explanation_parts.append("Missing-evidence signal word")
            # Injection signal
            if norm in _INJECTION_TOKENS:
                contributes_to_evidence = True
                explanation_parts.append("Prompt injection signal")
            # API/model source
            if norm in _API_SOURCE_TOKENS:
                contributes_to_evidence = True
                explanation_parts.append("API/model source token")
            # Ambiguous term
            if norm in _AMBIGUOUS_TERMS:
                contributes_to_evidence = True
                explanation_parts.append("Ambiguous term requiring context")
            if contributes_to_evidence and ev:
                contrib_types.append("contributes_to_evidence")
                target_ids.append(ev.evidence_id)

            # 5. Certainty contribution
            contributes_to_certainty = False
            if norm in _UNIVERSAL_QUANTIFIERS:
                contributes_to_certainty = True
                explanation_parts.append("Universal quantifier affects certainty")
            # Metaphor: check if this token is part of a known pair
            for subj, pred in _METAPHOR_PAIRS:
                if norm in (subj, pred):
                    contributes_to_certainty = True
                    explanation_parts.append("Part of metaphor pattern")
                    break
            if contributes_to_certainty and ct:
                contrib_types.append("contributes_to_certainty")
                target_ids.append(ct.certainty_id)

            # 6. Warning contribution
            contributes_to_warning = False
            if jt and jt.warnings:
                if norm in _INJECTION_TOKENS:
                    contributes_to_warning = True
                if norm in _AMBIGUOUS_TERMS:
                    contributes_to_warning = True
                if norm in _UNIVERSAL_QUANTIFIERS:
                    contributes_to_warning = True
                if norm in _API_SOURCE_TOKENS:
                    contributes_to_warning = True
                for subj, pred in _METAPHOR_PAIRS:
                    if norm in (subj, pred):
                        contributes_to_warning = True
                        break
            if contributes_to_warning and jt:
                contrib_types.append("contributes_to_warning")
                target_ids.append(jt.judgment_id)

            # 7. Final decision contribution (semantic tokens only)
            if not is_whitespace and jt:
                contrib_types.append("contributes_to_final_decision")
                target_ids.append(jt.judgment_id)

            # Compute weight
            is_semantic = not is_whitespace and not is_punctuation
            if is_semantic:
                total_semantic += 1
            unique_types = list(dict.fromkeys(contrib_types))
            weight = len([t for t in unique_types
                          if t != "contributes_to_token_boundary"]) / max(1, len(CONTRIBUTION_TYPES) - 1)
            weight = max(0.1, min(1.0, weight))

            # Orphan: semantic token with only boundary contribution
            is_orphan = (
                is_semantic
                and set(unique_types) == {"contributes_to_token_boundary",
                                          "contributes_to_final_decision"}
            )
            if is_semantic and not is_orphan:
                semantic_with_contribution += 1

            contributions.append(TraceContribution(
                trace_id=tok.unicode_trace_ids[0] if tok.unicode_trace_ids else "",
                token_id=tok_id,
                surface=surface,
                contribution_types=unique_types,
                target_ids=list(dict.fromkeys(target_ids)),
                contribution_weight=weight,
                explanation=" | ".join(explanation_parts) or "Token boundary only",
                is_orphan=is_orphan,
            ))

        # Compute scores
        orphan_surfaces = [c.surface for c in contributions if c.is_orphan]
        coverage_score = (
            semantic_with_contribution / total_semantic
            if total_semantic > 0 else 1.0
        )

        # Decision support: fraction of semantic tokens that contribute to final_decision
        decision_supporters = sum(
            1 for c in contributions
            if "contributes_to_final_decision" in c.contribution_types and not c.is_orphan
        )
        decision_support_score = (
            decision_supporters / total_semantic if total_semantic > 0 else 1.0
        )

        return TraceContributionMatrix(
            input_text=bundle.text,
            contributions=contributions,
            coverage_score=coverage_score,
            decision_support_score=decision_support_score,
            orphan_semantic_units=orphan_surfaces,
        )
