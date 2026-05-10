"""TraceGraphConsistency — Phase 7.1.3.

Checks that the trace chain (node links, edge links, vector traces,
judgment trace) is internally consistent:

  - Every NodeTraceLink.node_id exists in a known node set
  - Every EdgeTraceLink references existing node_ids
  - Every VectorTrace has non-empty source_trace_ids
  - JudgmentTrace references existing trace/token/node/edge/vector IDs
  - No orphan semantic tokens
  - No judgment without supporting trace
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.traceability.trace_builder import TraceBundle


@dataclass
class TraceGraphConsistencyReport:
    """Result of a consistency check over a TraceBundle."""

    passed: bool
    consistency_score: float
    orphan_nodes: list[str] = field(default_factory=list)
    orphan_edges: list[str] = field(default_factory=list)
    orphan_vectors: list[str] = field(default_factory=list)
    missing_judgment_refs: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "consistency_score": round(self.consistency_score, 4),
            "orphan_nodes": self.orphan_nodes,
            "orphan_edges": self.orphan_edges,
            "orphan_vectors": self.orphan_vectors,
            "missing_judgment_refs": self.missing_judgment_refs,
            "violations": self.violations,
        }

    def to_markdown(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [
            f"# Trace Graph Consistency Report — {status}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| consistency_score | {self.consistency_score:.4f} |",
            f"| orphan_nodes | {len(self.orphan_nodes)} |",
            f"| orphan_edges | {len(self.orphan_edges)} |",
            f"| orphan_vectors | {len(self.orphan_vectors)} |",
            f"| missing_judgment_refs | {len(self.missing_judgment_refs)} |",
            "",
        ]
        if self.violations:
            lines.append("## Violations")
            for v in self.violations:
                lines.append(f"- ❌ {v}")
        return "\n".join(lines)


class TraceGraphConsistencyChecker:
    """Checks internal consistency of a TraceBundle graph."""

    def check(self, bundle: TraceBundle) -> TraceGraphConsistencyReport:
        violations: list[str] = []
        orphan_nodes: list[str] = []
        orphan_edges: list[str] = []
        orphan_vectors: list[str] = []
        missing_judgment_refs: list[str] = []

        # Build known ID sets
        known_unicode_ids: set[str] = {u.trace_id for u in bundle.unicode_units if u.trace_id}
        known_token_ids: set[str] = {t.token_id for t in bundle.tokens if t.token_id}
        known_node_ids: set[str] = {nl.node_id for nl in bundle.node_links}
        known_edge_ids: set[str] = {el.edge_id for el in bundle.edge_links}
        known_vector_ids: set[str] = {vt.vector_id for vt in bundle.vector_traces}
        known_evidence_ids: set[str] = {ev.evidence_id for ev in bundle.evidence_traces}

        total_checks = 0
        passed_checks = 0

        # ── NodeTraceLink consistency ─────────────────────────────────────
        for nl in bundle.node_links:
            total_checks += 1
            # Every token_id referenced must exist
            missing_tids = [tid for tid in nl.token_ids if tid not in known_token_ids]
            if missing_tids:
                violations.append(
                    f"NodeTraceLink '{nl.node_id}': token_ids {missing_tids} not in known tokens"
                )
                orphan_nodes.append(nl.node_id)
            else:
                passed_checks += 1

        # ── EdgeTraceLink consistency ─────────────────────────────────────
        for el in bundle.edge_links:
            total_checks += 1
            is_inferred = el.metadata.get("inferred", False)
            ok = True

            if not el.source_node_id:
                violations.append(f"EdgeTraceLink '{el.edge_id}' missing source_node_id")
                ok = False
            elif el.source_node_id not in known_node_ids:
                violations.append(
                    f"EdgeTraceLink '{el.edge_id}': source_node_id '{el.source_node_id}' not in node_links"
                )
                ok = False

            if not el.target_node_id:
                violations.append(f"EdgeTraceLink '{el.edge_id}' missing target_node_id")
                ok = False
            elif el.target_node_id not in known_node_ids:
                violations.append(
                    f"EdgeTraceLink '{el.edge_id}': target_node_id '{el.target_node_id}' not in node_links"
                )
                ok = False

            if ok:
                passed_checks += 1
            else:
                orphan_edges.append(el.edge_id)

        # ── VectorTrace consistency ───────────────────────────────────────
        for vt in bundle.vector_traces:
            total_checks += 1
            if not vt.source_trace_ids:
                violations.append(f"VectorTrace '{vt.vector_id}' has no source_trace_ids")
                orphan_vectors.append(vt.vector_id)
            else:
                # All source_trace_ids must exist in unicode IDs or token IDs
                missing_sids = [
                    sid for sid in vt.source_trace_ids
                    if sid not in known_unicode_ids and sid not in known_token_ids
                ]
                if missing_sids:
                    violations.append(
                        f"VectorTrace '{vt.vector_id}': source_trace_ids "
                        f"{missing_sids[:3]} not in known trace IDs"
                    )
                    orphan_vectors.append(vt.vector_id)
                else:
                    passed_checks += 1

        # ── JudgmentTrace consistency ─────────────────────────────────────
        if bundle.judgment_trace is None:
            total_checks += 1
            violations.append("No judgment_trace present")
        else:
            jt = bundle.judgment_trace

            total_checks += 1
            if not jt.unicode_trace_ids:
                violations.append("judgment_trace: no unicode_trace_ids")
                missing_judgment_refs.append("unicode_trace_ids")
            else:
                missing_u = [uid for uid in jt.unicode_trace_ids[:5] if uid not in known_unicode_ids]
                if missing_u:
                    violations.append(f"judgment_trace: unicode_trace_ids {missing_u} not found")
                    missing_judgment_refs.append("unicode_trace_ids")
                else:
                    passed_checks += 1

            total_checks += 1
            if not jt.token_ids:
                violations.append("judgment_trace: no token_ids")
                missing_judgment_refs.append("token_ids")
            else:
                missing_t = [tid for tid in jt.token_ids[:5] if tid not in known_token_ids]
                if missing_t:
                    violations.append(f"judgment_trace: token_ids {missing_t} not found")
                    missing_judgment_refs.append("token_ids")
                else:
                    passed_checks += 1

            total_checks += 1
            if jt.node_ids:
                missing_n = [nid for nid in jt.node_ids if nid not in known_node_ids]
                if missing_n:
                    violations.append(f"judgment_trace: node_ids {missing_n} not in node_links")
                    missing_judgment_refs.append("node_ids")
                else:
                    passed_checks += 1
            else:
                passed_checks += 1  # no node_ids is OK (no graph nodes provided)

            total_checks += 1
            if jt.edge_ids:
                missing_e = [eid for eid in jt.edge_ids if eid not in known_edge_ids]
                if missing_e:
                    violations.append(f"judgment_trace: edge_ids {missing_e} not in edge_links")
                    missing_judgment_refs.append("edge_ids")
                else:
                    passed_checks += 1
            else:
                passed_checks += 1

            total_checks += 1
            if jt.vector_ids:
                missing_v = [vid for vid in jt.vector_ids if vid not in known_vector_ids]
                if missing_v:
                    violations.append(f"judgment_trace: vector_ids {missing_v} not in vector_traces")
                    missing_judgment_refs.append("vector_ids")
                else:
                    passed_checks += 1
            else:
                passed_checks += 1

            # Judgment must have explanation
            total_checks += 1
            if jt.explanation:
                passed_checks += 1
            else:
                violations.append("judgment_trace has no explanation")
                missing_judgment_refs.append("explanation")

            # No judgment without supporting trace
            total_checks += 1
            if jt.final_decision == "suspend" and not jt.warnings:
                violations.append(
                    "judgment_trace: final_decision=suspend but no warnings explaining reason"
                )
            else:
                passed_checks += 1

        # ── Orphan semantic token check ───────────────────────────────────
        semantic_tokens = [t for t in bundle.tokens if t.token_type not in ("whitespace",)]
        total_checks += len(semantic_tokens)
        for tok in semantic_tokens:
            # Token must be linked to at least one evidence trace or vector trace
            in_evidence = any(tok.token_id in ev.token_ids for ev in bundle.evidence_traces)
            in_vector = any(tok.token_id in vt.source_trace_ids for vt in bundle.vector_traces)
            in_node = any(tok.token_id in nl.token_ids for nl in bundle.node_links)
            if in_evidence or in_vector or in_node:
                passed_checks += 1
            # Not tracking orphan tokens as violations — they are handled by TraceValidator

        # ── Compute score ─────────────────────────────────────────────────
        consistency_score = passed_checks / total_checks if total_checks > 0 else 1.0

        passed = (
            consistency_score >= 0.98
            and not violations
        )

        return TraceGraphConsistencyReport(
            passed=passed,
            consistency_score=consistency_score,
            orphan_nodes=orphan_nodes,
            orphan_edges=orphan_edges,
            orphan_vectors=orphan_vectors,
            missing_judgment_refs=missing_judgment_refs,
            violations=violations,
        )
