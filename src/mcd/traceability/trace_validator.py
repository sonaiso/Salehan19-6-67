"""TraceValidator — validates the full trace chain for completeness and correctness."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from mcd.traceability.trace_builder import TraceBundle


@dataclass
class TraceValidationReport:
    passed: bool
    total_unicode: int
    traced_unicode: int
    orphan_tokens: int
    orphan_nodes: int
    orphan_edges: int
    orphan_vectors: int
    violations: list[str]
    traceability_score: float

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total_unicode": self.total_unicode,
            "traced_unicode": self.traced_unicode,
            "orphan_tokens": self.orphan_tokens,
            "orphan_nodes": self.orphan_nodes,
            "orphan_edges": self.orphan_edges,
            "orphan_vectors": self.orphan_vectors,
            "violations": self.violations,
            "traceability_score": self.traceability_score,
        }

    def to_markdown(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [
            f"# Trace Validation Report — {status}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| total_unicode | {self.total_unicode} |",
            f"| traced_unicode | {self.traced_unicode} |",
            f"| orphan_tokens | {self.orphan_tokens} |",
            f"| orphan_nodes | {self.orphan_nodes} |",
            f"| orphan_edges | {self.orphan_edges} |",
            f"| orphan_vectors | {self.orphan_vectors} |",
            f"| traceability_score | {self.traceability_score:.4f} |",
            "",
        ]
        if self.violations:
            lines.append("## Violations")
            for v in self.violations:
                lines.append(f"- {v}")
        return "\n".join(lines)


class TraceValidator:
    """Validates a TraceBundle for completeness and correctness."""

    def validate(self, bundle: TraceBundle) -> TraceValidationReport:
        violations: list[str] = []
        total_u = len(bundle.unicode_units)
        traced_u = 0
        orphan_tokens = 0
        orphan_nodes = 0
        orphan_edges = 0
        orphan_vectors = 0

        # 1. Every Unicode unit must have a trace_id
        known_u_ids: set[str] = set()
        for u in bundle.unicode_units:
            if not u.trace_id:
                violations.append(f"Unicode unit at index {u.char_index} has no trace_id")
            else:
                known_u_ids.add(u.trace_id)
                traced_u += 1

        # 2. Every token must have unicode_trace_ids
        known_t_ids: set[str] = set()
        for tok in bundle.tokens:
            if not tok.token_id:
                violations.append(f"Token '{tok.surface}' has no token_id")
            else:
                known_t_ids.add(tok.token_id)
            if not tok.unicode_trace_ids:
                orphan_tokens += 1
                violations.append(f"Token '{tok.surface}' ({tok.token_id}) has no unicode_trace_ids")

        # 3. Every node link must have token origin or generated reason
        known_n_ids: set[str] = set()
        for nl in bundle.node_links:
            known_n_ids.add(nl.node_id)
            if not nl.token_ids and not nl.is_generated:
                orphan_nodes += 1
                violations.append(
                    f"NodeTraceLink '{nl.node_id}' has no token_ids and is not marked generated"
                )

        # 4. Every edge link must have source/target
        for el in bundle.edge_links:
            if not el.source_node_id or not el.target_node_id:
                orphan_edges += 1
                violations.append(f"EdgeTraceLink '{el.edge_id}' missing source or target")

        # 5. Every vector trace must have source_trace_ids
        for vt in bundle.vector_traces:
            if not vt.source_trace_ids:
                orphan_vectors += 1
                violations.append(f"VectorTrace '{vt.vector_id}' has no source_trace_ids")
            # All values in [0,1]
            for k, v in vt.vector.items():
                if not (0.0 <= v <= 1.0):
                    violations.append(f"VectorTrace '{vt.vector_id}' dimension '{k}'={v} out of [0,1]")

        # 6. Judgment trace must exist and have full chain
        if bundle.judgment_trace is None:
            violations.append("No judgment_trace present")
        else:
            jt = bundle.judgment_trace
            if not jt.unicode_trace_ids:
                violations.append("judgment_trace has no unicode_trace_ids")
            if not jt.token_ids:
                violations.append("judgment_trace has no token_ids")
            if jt.final_decision == "suspend" and not jt.warnings:
                violations.append("judgment_trace: final_decision=suspend but no warnings explaining reason")
            if jt.certainty_policy == "near_certainty":
                if not jt.evidence_status or jt.evidence_status != "present":
                    violations.append(
                        "judgment_trace: near_certainty requires evidence_status='present'"
                    )

        # 7. Unknown chars must be tracked (not dropped)
        for u in bundle.unicode_units:
            if u.trace_status == "unknown_but_tracked" and not u.trace_id:
                violations.append(f"Unknown char '{u.char}' at index {u.char_index} has no trace_id")

        # 8. JSON serializable
        try:
            bundle_dict = bundle.to_dict()
            json.dumps(bundle_dict, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            violations.append(f"TraceBundle is not JSON serializable: {exc}")

        # Compute traceability_score
        # Base: fraction of traced unicode
        if total_u == 0:
            score = 1.0
        else:
            score = traced_u / total_u

        # Penalize violations (soft, capped at -0.01 each)
        penalty = len(violations) * 0.01
        score = max(0.0, score - penalty)

        passed = (
            total_u == traced_u
            and orphan_tokens == 0
            and orphan_edges == 0
            and orphan_vectors == 0
            and bundle.judgment_trace is not None
            and score >= 0.99
            and not any("not JSON serializable" in v for v in violations)
        )

        return TraceValidationReport(
            passed=passed,
            total_unicode=total_u,
            traced_unicode=traced_u,
            orphan_tokens=orphan_tokens,
            orphan_nodes=orphan_nodes,
            orphan_edges=orphan_edges,
            orphan_vectors=orphan_vectors,
            violations=violations,
            traceability_score=score,
        )
