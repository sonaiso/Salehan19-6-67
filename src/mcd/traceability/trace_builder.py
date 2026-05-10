"""TraceBuilder — deterministic builder for the full trace chain."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.traceability.unicode_trace import UnicodeTraceUnit, build_unicode_trace_unit
from mcd.traceability.grapheme_trace import GraphemeTrace, build_grapheme_traces
from mcd.traceability.token_trace import TokenTrace, build_token_traces
from mcd.traceability.node_trace import NodeTraceLink
from mcd.traceability.edge_trace import EdgeTraceLink
from mcd.traceability.vector_trace import VectorTrace
from mcd.traceability.evidence_trace import EvidenceTrace
from mcd.traceability.certainty_trace import CertaintyTrace
from mcd.traceability.judgment_trace import JudgmentTrace

# Keywords used to detect missing evidence
_MISSING_EVIDENCE_SIGNALS = {
    'بلا', 'بدون', 'مصدر', 'دليل', 'بلا مصدر', 'بلا دليل',
    'بدون مصدر', 'بدون دليل', 'لا دليل', 'لا مصدر',
}
_UNIVERSAL_QUANTIFIERS = {'كل', 'جميع', 'دائما', 'دائمًا', 'أبدا', 'أبدًا'}
_INJECTION_SIGNALS = {'تجاهل', 'تجاهل تعليمات', 'ignore', 'forget instructions'}
_NEGATION_SIGNALS = {'لا', 'لن', 'لم', 'ليس', 'ليست', 'ليسوا', 'لا يوجد', 'غير', 'بلا', 'بدون'}


@dataclass
class TraceBundle:
    """Complete trace bundle for one input text."""
    text: str
    unicode_units: list[UnicodeTraceUnit] = field(default_factory=list)
    graphemes: list[GraphemeTrace] = field(default_factory=list)
    tokens: list[TokenTrace] = field(default_factory=list)
    node_links: list[NodeTraceLink] = field(default_factory=list)
    edge_links: list[EdgeTraceLink] = field(default_factory=list)
    vector_traces: list[VectorTrace] = field(default_factory=list)
    evidence_traces: list[EvidenceTrace] = field(default_factory=list)
    certainty_trace: CertaintyTrace | None = None
    judgment_trace: JudgmentTrace | None = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "unicode_units": [u.to_dict() for u in self.unicode_units],
            "graphemes": [g.to_dict() for g in self.graphemes],
            "tokens": [t.to_dict() for t in self.tokens],
            "node_links": [n.to_dict() for n in self.node_links],
            "edge_links": [e.to_dict() for e in self.edge_links],
            "vector_traces": [v.to_dict() for v in self.vector_traces],
            "evidence_traces": [e.to_dict() for e in self.evidence_traces],
            "certainty_trace": self.certainty_trace.to_dict() if self.certainty_trace else None,
            "judgment_trace": self.judgment_trace.to_dict() if self.judgment_trace else None,
        }


class TraceBuilder:
    """Deterministic builder that constructs the full Unicode-to-Cognition trace chain."""

    def build_unicode_trace(self, text: str) -> list[UnicodeTraceUnit]:
        """Build UnicodeTraceUnit for every character in text. Never drops unknown chars."""
        return [build_unicode_trace_unit(ch, i) for i, ch in enumerate(text)]

    def build_grapheme_trace(self, unicode_units: list[UnicodeTraceUnit]) -> list[GraphemeTrace]:
        return build_grapheme_traces(unicode_units)

    def build_token_trace(
        self,
        text: str,
        unicode_units: list[UnicodeTraceUnit],
        graphemes: list[GraphemeTrace],
    ) -> list[TokenTrace]:
        return build_token_traces(text, unicode_units, graphemes)

    def link_nodes_to_tokens(
        self,
        nodes: list[dict],
        tokens: list[TokenTrace],
    ) -> list[NodeTraceLink]:
        """
        Link CognitiveNode dicts to tokens by surface matching.
        nodes: list of dicts with at least 'node_id', 'surface', 'role_vector', 'domain_vector'.
        """
        links: list[NodeTraceLink] = []
        # Build surface->token map for lookup
        surface_to_tokens: dict[str, list[TokenTrace]] = {}
        for tok in tokens:
            key = tok.normalized.strip()
            if key:
                surface_to_tokens.setdefault(key, []).append(tok)

        for node in nodes:
            node_id = node.get("node_id", f"N-{uuid.uuid4().hex[:8]}")
            surface = node.get("normalized", node.get("surface", ""))
            matched_tokens = surface_to_tokens.get(surface, [])
            # Also try partial match
            if not matched_tokens:
                for tok in tokens:
                    if surface and (surface in tok.surface or tok.normalized in surface):
                        matched_tokens.append(tok)
            token_ids = [t.token_id for t in matched_tokens]
            unicode_ids = []
            for t in matched_tokens:
                unicode_ids.extend(t.unicode_trace_ids)

            links.append(NodeTraceLink(
                node_id=node_id,
                token_ids=token_ids,
                unicode_trace_ids=unicode_ids,
                role_vector_contribution=dict(node.get("role_vector", {})),
                domain_vector_contribution=dict(node.get("domain_vector", {})),
                explanation=f"Node '{surface}' linked via surface matching to {len(token_ids)} token(s).",
                metadata={"generated_node": not bool(token_ids), "reason": "no_surface_match" if not token_ids else ""},
            ))
        return links

    def link_edges_to_tokens(
        self,
        edges: list[dict],
        node_links: list[NodeTraceLink],
    ) -> list[EdgeTraceLink]:
        """Link CognitiveEdge dicts to token/unicode trace via node links."""
        node_link_map: dict[str, NodeTraceLink] = {nl.node_id: nl for nl in node_links}
        result: list[EdgeTraceLink] = []

        for edge in edges:
            edge_id = edge.get("edge_id", f"E-{uuid.uuid4().hex[:8]}")
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            relation = edge.get("relation", "unknown")
            certainty = float(edge.get("certainty", 0.5))

            src_link = node_link_map.get(src)
            tgt_link = node_link_map.get(tgt)

            u_ids: list[str] = []
            t_ids: list[str] = []
            if src_link:
                u_ids.extend(src_link.unicode_trace_ids)
                t_ids.extend(src_link.token_ids)
            if tgt_link:
                u_ids.extend(tgt_link.unicode_trace_ids)
                t_ids.extend(tgt_link.token_ids)

            inferred = not (src_link and tgt_link and src_link.token_ids and tgt_link.token_ids)
            meta: dict = {}
            if inferred:
                meta["inferred"] = True
                meta["inference_reason"] = "one_or_both_nodes_not_surface_matched"

            result.append(EdgeTraceLink(
                edge_id=edge_id,
                source_node_id=src,
                target_node_id=tgt,
                relation=relation,
                supporting_unicode_trace_ids=list(set(u_ids)),
                supporting_token_ids=list(set(t_ids)),
                confidence=certainty,
                explanation=f"Edge '{src}' --{relation}--> '{tgt}'",
                metadata=meta,
            ))
        return result

    def build_vector_traces(
        self,
        tokens: list[TokenTrace],
        unicode_units: list[UnicodeTraceUnit],
    ) -> list[VectorTrace]:
        """Build VectorTrace objects from token role vectors."""
        traces: list[VectorTrace] = []
        if not tokens:
            return traces

        # Feature vector trace (aggregate of all unicode feature vectors)
        all_u_ids = [u.trace_id for u in unicode_units]
        # Compute average feature for numeric dims
        numeric_keys = [
            "root_candidate_score", "affix_candidate_score",
            "weak_letter_score", "connects_right", "connects_left",
        ]
        agg_fv: dict[str, float] = {}
        n = len(unicode_units)
        if n > 0:
            for key in numeric_keys:
                vals = [float(u.feature_vector.get(key, 0.0)) for u in unicode_units]
                agg_fv[key] = min(1.0, sum(vals) / n)

        traces.append(VectorTrace(
            vector_id=f"V-feature-{uuid.uuid4().hex[:8]}",
            vector_type="feature",
            source_trace_ids=all_u_ids,
            vector=agg_fv,
            contribution_weights={u.trace_id: 1.0 / n for u in unicode_units} if n > 0 else {},
            normalization_applied=True,
            explanation="Aggregate feature vector over all Unicode units.",
        ))

        # Role vector trace (aggregate of token role vectors)
        non_ws_tokens = [t for t in tokens if t.token_type not in ("whitespace",)]
        if non_ws_tokens:
            all_t_ids = [t.token_id for t in non_ws_tokens]
            merged_rv: dict[str, float] = {}
            for tok in non_ws_tokens:
                for k, v in tok.role_vector.items():
                    merged_rv[k] = max(merged_rv.get(k, 0.0), v)
            # Normalize to [0,1]
            max_val = max(merged_rv.values()) if merged_rv else 1.0
            if max_val > 0:
                merged_rv = {k: v / max_val for k, v in merged_rv.items()}
            traces.append(VectorTrace(
                vector_id=f"V-role-{uuid.uuid4().hex[:8]}",
                vector_type="role",
                source_trace_ids=all_t_ids,
                vector=merged_rv,
                contribution_weights={t.token_id: 1.0 / len(non_ws_tokens) for t in non_ws_tokens},
                normalization_applied=True,
                explanation="Merged role vector from all non-whitespace tokens.",
            ))

        return traces

    def build_evidence_trace(
        self,
        tokens: list[TokenTrace],
        unicode_units: list[UnicodeTraceUnit],
    ) -> EvidenceTrace:
        """Detect evidence status from tokens."""
        surfaces = {t.normalized.strip() for t in tokens}
        missing = any(s in _MISSING_EVIDENCE_SIGNALS for s in surfaces)
        # Also check multi-word signals
        text_joined = " ".join(t.normalized for t in tokens)
        for sig in _MISSING_EVIDENCE_SIGNALS:
            if sig in text_joined:
                missing = True
                break

        injection = any(s in _INJECTION_SIGNALS for s in surfaces)
        for sig in _INJECTION_SIGNALS:
            if sig in text_joined:
                injection = True
                break

        if injection:
            status = "fake"
            desc = "Prompt injection signal detected."
            etype = "injection"
        elif missing:
            status = "missing"
            desc = "Missing evidence signal detected (بلا مصدر / بدون دليل)."
            etype = "source_required"
        else:
            status = "present"
            desc = "No missing evidence signals detected."
            etype = "contextual"

        u_ids = [u.trace_id for u in unicode_units]
        t_ids = [t.token_id for t in tokens]
        return EvidenceTrace(
            evidence_id=f"EV-{uuid.uuid4().hex[:8]}",
            status=status,
            source_trace_ids=u_ids,
            token_ids=t_ids,
            description=desc,
            evidence_type=etype,
        )

    def build_certainty_trace(
        self,
        evidence: EvidenceTrace,
        tokens: list[TokenTrace],
    ) -> CertaintyTrace:
        """Derive certainty policy from evidence trace."""
        surfaces = {t.normalized.strip() for t in tokens}
        text_joined = " ".join(t.normalized for t in tokens)

        has_universal = any(s in _UNIVERSAL_QUANTIFIERS for s in surfaces)
        for q in _UNIVERSAL_QUANTIFIERS:
            if q in text_joined:
                has_universal = True
                break

        if evidence.status in ("fake", "missing"):
            policy = "suspend"
            score = 0.1
            reason = f"Evidence status is '{evidence.status}'. Judgment suspended."
        elif has_universal and evidence.status != "present":
            policy = "suspend"
            score = 0.2
            reason = "Universal quantifier with missing evidence → suspend."
        elif evidence.status == "partial":
            policy = "probable_knowledge"
            score = 0.5
            reason = "Partial evidence → probable knowledge."
        else:
            policy = "strong_knowledge"
            score = 0.75
            reason = "Evidence present → strong knowledge."

        return CertaintyTrace(
            certainty_id=f"C-{uuid.uuid4().hex[:8]}",
            policy=policy,
            score=score,
            source_evidence_ids=[evidence.evidence_id],
            source_token_ids=[t.token_id for t in tokens],
            reason=reason,
        )

    def build_judgment_trace(
        self,
        text: str,
        unicode_units: list[UnicodeTraceUnit],
        tokens: list[TokenTrace],
        node_links: list[NodeTraceLink],
        edge_links: list[EdgeTraceLink],
        vector_traces: list[VectorTrace],
        evidence: EvidenceTrace,
        certainty: CertaintyTrace,
    ) -> JudgmentTrace:
        """Build the final JudgmentTrace with complete chain."""
        u_ids = [u.trace_id for u in unicode_units]
        t_ids = [t.token_id for t in tokens]
        n_ids = [nl.node_id for nl in node_links]
        e_ids = [el.edge_id for el in edge_links]
        v_ids = [vt.vector_id for vt in vector_traces]

        warnings: list[str] = []
        if certainty.policy == "near_certainty" and evidence.status != "present":
            warnings.append("near_certainty requires evidence trace but evidence is not 'present'")
        if certainty.policy == "suspend":
            warnings.append(f"Judgment suspended: {certainty.reason}")

        if certainty.policy == "suspend":
            decision = "suspend"
        elif evidence.status == "missing":
            decision = "request_evidence"
        elif evidence.status == "fake":
            decision = "reject"
        else:
            decision = "answer"

        return JudgmentTrace(
            judgment_id=f"J-{uuid.uuid4().hex[:8]}",
            input_text=text,
            unicode_trace_ids=u_ids,
            token_ids=t_ids,
            node_ids=n_ids,
            edge_ids=e_ids,
            vector_ids=v_ids,
            evidence_status=evidence.status,
            certainty_policy=certainty.policy,
            final_decision=decision,
            warnings=warnings,
            explanation=(
                f"Decision '{decision}' based on evidence_status='{evidence.status}', "
                f"certainty_policy='{certainty.policy}'. {certainty.reason}"
            ),
        )

    def build(
        self,
        text: str,
        nodes: list[dict] | None = None,
        edges: list[dict] | None = None,
    ) -> TraceBundle:
        """Build the complete TraceBundle for a given text (and optional nodes/edges)."""
        nodes = nodes or []
        edges = edges or []

        unicode_units = self.build_unicode_trace(text)
        graphemes = self.build_grapheme_trace(unicode_units)
        tokens = self.build_token_trace(text, unicode_units, graphemes)
        node_links = self.link_nodes_to_tokens(nodes, tokens)
        edge_links = self.link_edges_to_tokens(edges, node_links)
        vector_traces = self.build_vector_traces(tokens, unicode_units)
        evidence = self.build_evidence_trace(tokens, unicode_units)
        certainty = self.build_certainty_trace(evidence, tokens)
        judgment = self.build_judgment_trace(
            text, unicode_units, tokens, node_links, edge_links,
            vector_traces, evidence, certainty,
        )

        return TraceBundle(
            text=text,
            unicode_units=unicode_units,
            graphemes=graphemes,
            tokens=tokens,
            node_links=node_links,
            edge_links=edge_links,
            vector_traces=vector_traces,
            evidence_traces=[evidence],
            certainty_trace=certainty,
            judgment_trace=judgment,
        )
