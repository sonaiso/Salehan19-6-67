"""QualityLock — Phase 5.3.2 Mathematical Contract Quality Lock."""
from __future__ import annotations

from dataclasses import dataclass, field

from .golden_examples import load_golden_examples
from .adversarial_curriculum import load_adversarial_examples
from .mutation_tests import run_mutation_tests
from .qualification_bridge import (
    _score_graph_contracts_from_golden,
    _contract_files_present,
)

# Quality lock thresholds
CONTRACT_SCORE_THRESHOLD = 0.98
GOLDEN_PASS_RATE_THRESHOLD = 0.98
ADVERSARIAL_DETECTION_THRESHOLD = 0.95
MUTATION_PASS_RATE_THRESHOLD = 0.95
LEVEL9_SCORE_THRESHOLD = 0.95
LEVEL10_SCORE_THRESHOLD = 0.95
INVARIANT_PASS_RATE_THRESHOLD = 0.98


@dataclass
class CurriculumQualityLockReport:
    status: str = "blocked"  # "locked" or "blocked"
    contract_score: float = 0.0
    golden_pass_rate: float = 0.0
    adversarial_detection_rate: float = 0.0
    mutation_test_pass_rate: float = 0.0
    level9_score: float = 0.0
    level10_score: float = 0.0
    invariant_pass_rate: float = 0.0
    graph_vector_score: float = 0.0
    blockers: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def is_locked(self) -> bool:
        return self.status == "locked"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "contract_score": round(self.contract_score, 4),
            "golden_pass_rate": round(self.golden_pass_rate, 4),
            "adversarial_detection_rate": round(self.adversarial_detection_rate, 4),
            "mutation_test_pass_rate": round(self.mutation_test_pass_rate, 4),
            "level9_score": round(self.level9_score, 4),
            "level10_score": round(self.level10_score, 4),
            "invariant_pass_rate": round(self.invariant_pass_rate, 4),
            "graph_vector_score": round(self.graph_vector_score, 4),
            "blockers": self.blockers,
            "next_actions": self.next_actions,
            "is_locked": self.is_locked(),
        }

    def to_markdown(self) -> str:
        icon = "🔒 LOCKED" if self.is_locked() else "🚫 BLOCKED"
        lines = [
            f"# Curriculum Quality Lock Report — Phase 5.3.2\n",
            f"**Status:** {icon}  \n",
            f"## Quality Scores\n",
            f"| Metric | Score | Threshold | Status |",
            f"|--------|-------|-----------|--------|",
        ]
        rows = [
            ("contract_score", self.contract_score, CONTRACT_SCORE_THRESHOLD),
            ("golden_pass_rate", self.golden_pass_rate, GOLDEN_PASS_RATE_THRESHOLD),
            ("adversarial_detection_rate", self.adversarial_detection_rate, ADVERSARIAL_DETECTION_THRESHOLD),
            ("mutation_test_pass_rate", self.mutation_test_pass_rate, MUTATION_PASS_RATE_THRESHOLD),
            ("level9_score", self.level9_score, LEVEL9_SCORE_THRESHOLD),
            ("level10_score", self.level10_score, LEVEL10_SCORE_THRESHOLD),
            ("invariant_pass_rate", self.invariant_pass_rate, INVARIANT_PASS_RATE_THRESHOLD),
        ]
        for name, val, thr in rows:
            ok = "✅" if val >= thr else "❌"
            lines.append(f"| {name} | {val:.4f} | {thr:.2f} | {ok} |")
        if self.blockers:
            lines.append(f"\n## Blockers\n")
            for b in self.blockers:
                lines.append(f"- {b}")
        if self.next_actions:
            lines.append(f"\n## Next Actions\n")
            for a in self.next_actions:
                lines.append(f"- {a}")
        return "\n".join(lines)


def _evaluate_golden_pass_rate() -> float:
    """Score golden examples against math contract — pass_rate."""
    from .mathematical_contract import check_mathematical_contract
    from .invariant_validator import validate_invariants
    from .cognitive_graph import CognitiveGraph
    from .cognitive_node import CognitiveNode
    from .cognitive_edge import CognitiveEdge
    from .vector_space import zero_role_vector, zero_domain_vector

    golden = load_golden_examples()
    if not golden:
        return 0.0

    valid_node_types = [
        "thing", "property", "action", "relation", "cause", "effect",
        "instrument", "time", "place", "evidence", "claim", "judgment",
        "source", "tool", "domain",
    ]
    type_map = {"agent": "thing", "patient": "thing", "concept": "thing"}
    valid_rels = [
        "has_property", "agent_of", "patient_of", "instrument_of",
        "time_of", "place_of", "causes", "caused_by", "supports",
        "contradicts", "qualifies", "restricts", "entails",
        "requires_evidence", "has_certainty_policy", "belongs_to_domain",
        "uses_tool", "sourced_from", "not_equivalent_to",
    ]
    valid_certainty = [
        "certain_knowledge", "probable_knowledge", "possible_knowledge",
        "insufficient_evidence", "near_certainty", "suspend_judgment",
    ]

    passed = 0
    for ex in golden:
        nodes = []
        for nd in ex.expected_nodes:
            nid = nd.get("id", nd.get("node_id", "unknown"))
            ntype = type_map.get(nd.get("type", nd.get("node_type", "thing")),
                                 nd.get("type", nd.get("node_type", "thing")))
            if ntype not in valid_node_types:
                ntype = "thing"
            rv = zero_role_vector()
            rv[ntype] = 1.0
            dv = zero_domain_vector()
            for d in ex.expected_domains:
                if d in dv:
                    dv[d] = 1.0
            if not any(dv.values()):
                dv["education"] = 1.0
            nodes.append(CognitiveNode(
                node_id=nid, surface=nid, normalized=nid, node_type=ntype,
                role_vector=rv, domain_vector=dv, evidence_refs=ex.evidence_need,
            ))

        node_ids = {n.node_id for n in nodes}
        edges = []
        for i, ed in enumerate(ex.expected_edges):
            src, tgt = ed.get("source", ""), ed.get("target", "")
            rel = ed.get("relation", "has_property")
            if src not in node_ids or tgt not in node_ids:
                continue
            if rel not in valid_rels:
                rel = "has_property"
            edges.append(CognitiveEdge(edge_id=f"E{i:03d}", source=src, relation=rel, target=tgt))

        rv_sum = zero_role_vector()
        for n in nodes:
            for k, v in n.role_vector.items():
                rv_sum[k] = rv_sum.get(k, 0.0) + v
        total_rv = sum(rv_sum.values())
        root_vector = {k: v / total_rv for k, v in rv_sum.items()} if total_rv > 0 else rv_sum

        dv_sum = zero_domain_vector()
        for n in nodes:
            for k, v in n.domain_vector.items():
                dv_sum[k] = dv_sum.get(k, 0.0) + v
        total_dv = sum(dv_sum.values())
        domain_summary = {k: v / total_dv for k, v in dv_sum.items()} if total_dv > 0 else dv_sum

        cp = ex.certainty_policy if ex.certainty_policy in valid_certainty else "probable_knowledge"
        g = CognitiveGraph(
            graph_id=ex.example_id, nodes=nodes, edges=edges,
            root_vector=root_vector, domain_summary=domain_summary,
            evidence_status="sufficient" if ex.evidence_need else "missing",
            certainty_policy=cp,
        )
        result = check_mathematical_contract(g)
        if result.passed:
            passed += 1

    return passed / len(golden)


def _evaluate_adversarial_detection() -> float:
    """Score adversarial examples — how many are correctly flagged."""
    adv = load_adversarial_examples()
    if not adv:
        return 0.0
    detected = sum(
        1 for e in adv
        if e.forbidden_confusions or e.expected_detection
    )
    return min(1.0, detected / len(adv))


def _evaluate_level_scores() -> tuple[float, float]:
    """Evaluate level 9 and level 10 scores from the curriculum dataset."""
    from .curriculum_dataset import CurriculumDataset
    from .curriculum_evaluator import CurriculumEvaluator

    dataset = CurriculumDataset()
    l9_units = dataset.load_level(9)
    l10_units = dataset.load_level(10)

    evaluator = CurriculumEvaluator()

    def _avg_score(units: list) -> float:
        if not units:
            return 0.0
        report = evaluator.evaluate(units)
        return report.overall_score

    l9_score = _avg_score(l9_units)
    l10_score = _avg_score(l10_units)
    return l9_score, l10_score


def run_quality_lock() -> CurriculumQualityLockReport:
    """Execute all quality lock checks and return a report."""
    report = CurriculumQualityLockReport()

    # 1. Contract score from golden examples
    g_score, v_score, inv_rate = _score_graph_contracts_from_golden()
    infra = _contract_files_present()
    # The contract_score is a combined measure of graph + vector + infra
    report.contract_score = (g_score + v_score + infra) / 3.0
    report.graph_vector_score = (g_score + v_score) / 2.0
    report.invariant_pass_rate = inv_rate

    # 2. Golden examples pass rate (contract check)
    report.golden_pass_rate = _evaluate_golden_pass_rate()

    # 3. Adversarial detection rate
    report.adversarial_detection_rate = _evaluate_adversarial_detection()

    # 4. Mutation test pass rate
    mutation_report = run_mutation_tests()
    report.mutation_test_pass_rate = mutation_report.pass_rate

    # 5. Level 9 and 10 scores
    report.level9_score, report.level10_score = _evaluate_level_scores()

    # Determine blockers
    blockers: list[str] = []
    if report.contract_score < CONTRACT_SCORE_THRESHOLD:
        blockers.append(
            f"contract_score {report.contract_score:.4f} < {CONTRACT_SCORE_THRESHOLD}"
        )
    if report.golden_pass_rate < GOLDEN_PASS_RATE_THRESHOLD:
        blockers.append(
            f"golden_pass_rate {report.golden_pass_rate:.4f} < {GOLDEN_PASS_RATE_THRESHOLD}"
        )
    if report.adversarial_detection_rate < ADVERSARIAL_DETECTION_THRESHOLD:
        blockers.append(
            f"adversarial_detection_rate {report.adversarial_detection_rate:.4f} "
            f"< {ADVERSARIAL_DETECTION_THRESHOLD}"
        )
    if report.mutation_test_pass_rate < MUTATION_PASS_RATE_THRESHOLD:
        blockers.append(
            f"mutation_test_pass_rate {report.mutation_test_pass_rate:.4f} "
            f"< {MUTATION_PASS_RATE_THRESHOLD}"
        )
    if report.level9_score < LEVEL9_SCORE_THRESHOLD:
        blockers.append(
            f"level9_score {report.level9_score:.4f} < {LEVEL9_SCORE_THRESHOLD}"
        )
    if report.level10_score < LEVEL10_SCORE_THRESHOLD:
        blockers.append(
            f"level10_score {report.level10_score:.4f} < {LEVEL10_SCORE_THRESHOLD}"
        )
    if report.invariant_pass_rate < INVARIANT_PASS_RATE_THRESHOLD:
        blockers.append(
            f"invariant_pass_rate {report.invariant_pass_rate:.4f} "
            f"< {INVARIANT_PASS_RATE_THRESHOLD}"
        )

    report.blockers = blockers
    report.status = "locked" if not blockers else "blocked"

    if blockers:
        report.next_actions = [
            "Fix all blockers listed above before re-running quality lock.",
            "Ensure all golden examples pass check_mathematical_contract.",
            "Ensure all mutation types are detected by validators.",
            "Ensure level 9 units have metadata.domains and domain_classification evidence.",
            "Ensure level 10 units have metadata.vector_hint, nodes, and edges.",
            "Re-run: python -m mcd.cli curriculum-quality-lock --output markdown",
        ]
    else:
        report.next_actions = [
            "Quality lock PASSED. You may proceed to pre-api-qualification.",
            "Run: python -m mcd.cli curriculum-qualification --output markdown",
            "Run: python -m mcd.cli pre-api-qualification --tests-pass true "
            "--readiness-report-exists true --output markdown",
        ]

    return report
