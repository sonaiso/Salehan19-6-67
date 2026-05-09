"""Tests for Phase 5.3.2 — Mathematical Contract Quality Lock & Verification."""
from __future__ import annotations

import pytest

from mcd.curriculum.cognitive_graph import CognitiveGraph
from mcd.curriculum.cognitive_node import CognitiveNode
from mcd.curriculum.cognitive_edge import CognitiveEdge
from mcd.curriculum.mathematical_contract import check_mathematical_contract
from mcd.curriculum.invariant_validator import validate_invariants
from mcd.curriculum.vector_space import zero_role_vector, zero_domain_vector


# ── helpers ──────────────────────────────────────────────────────────────────

def _node(nid: str, ntype: str = "thing", rv: dict | None = None, dv: dict | None = None,
          ev: list | None = None) -> CognitiveNode:
    role_vector = rv if rv is not None else {**zero_role_vector(), ntype: 1.0}
    domain_vector = dv if dv is not None else {**zero_domain_vector(), "education": 1.0}
    return CognitiveNode(
        node_id=nid, surface=nid, normalized=nid, node_type=ntype,
        role_vector=role_vector, domain_vector=domain_vector,
        evidence_refs=ev if ev is not None else [],
    )


def _graph(nodes=None, edges=None, certainty="probable_knowledge",
           evidence_status="sufficient") -> CognitiveGraph:
    return CognitiveGraph(
        graph_id="test",
        nodes=nodes or [],
        edges=edges or [],
        evidence_status=evidence_status,
        certainty_policy=certainty,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Issue 1: curriculum-contract-check CLI builds valid vectors
# ══════════════════════════════════════════════════════════════════════════════

def test_curriculum_contract_check_cli_builds_valid_vectors():
    """CLI must build nodes with valid role_vector and domain_vector."""
    import subprocess, sys, json, os
    from pathlib import Path
    repo_root = str(Path(__file__).parent.parent)
    env = {**os.environ, "PYTHONPATH": "src"}
    result = subprocess.run(
        [sys.executable, "-m", "mcd.cli", "curriculum-contract-check", "--output", "json"],
        capture_output=True, text=True, env=env,
        cwd=repo_root,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert "passed" in data
    assert "violations" in data


def test_curriculum_contract_check_passes_on_valid_curriculum_graph():
    """A graph with proper role_vector and domain_vector must pass contract."""
    nodes = [_node("n1"), _node("n2")]
    g = _graph(nodes=nodes)
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


def test_curriculum_contract_check_fails_on_missing_vectors():
    """A node without role_vector must cause contract violation."""
    n = CognitiveNode(
        node_id="n1", surface="n1", normalized="n1", node_type="thing",
        role_vector={},  # missing
        domain_vector={**zero_domain_vector(), "education": 1.0},
    )
    g = _graph(nodes=[n])
    result = check_mathematical_contract(g)
    assert not result.passed


# ══════════════════════════════════════════════════════════════════════════════
# Issue 2: domain_vector mandatory — must be violation not warning
# ══════════════════════════════════════════════════════════════════════════════

def test_missing_domain_vector_is_violation():
    """Missing domain_vector must appear in violations, not just warnings."""
    n = CognitiveNode(
        node_id="n1", surface="n1", normalized="n1", node_type="thing",
        role_vector={**zero_role_vector(), "thing": 1.0},
        domain_vector={},  # missing
    )
    g = _graph(nodes=[n])
    result = check_mathematical_contract(g)
    assert not result.passed
    assert any("domain_vector" in v for v in result.violations), \
        f"Expected domain_vector violation. Got violations: {result.violations}"


def test_missing_role_vector_is_violation():
    """Missing role_vector must be a contract violation."""
    n = CognitiveNode(
        node_id="n1", surface="n1", normalized="n1", node_type="thing",
        role_vector={},  # missing
        domain_vector={**zero_domain_vector(), "education": 1.0},
    )
    g = _graph(nodes=[n])
    result = check_mathematical_contract(g)
    assert not result.passed
    assert any("role_vector" in v for v in result.violations)


def test_node_requires_role_and_domain_vectors():
    """Both role_vector and domain_vector are mandatory for each node."""
    n_no_rv = CognitiveNode(
        node_id="n1", surface="n1", normalized="n1", node_type="thing",
        role_vector={}, domain_vector={**zero_domain_vector(), "education": 1.0},
    )
    n_no_dv = CognitiveNode(
        node_id="n2", surface="n2", normalized="n2", node_type="thing",
        role_vector={**zero_role_vector(), "thing": 1.0}, domain_vector={},
    )
    g_no_rv = _graph(nodes=[n_no_rv])
    g_no_dv = _graph(nodes=[n_no_dv])
    assert not check_mathematical_contract(g_no_rv).passed
    assert not check_mathematical_contract(g_no_dv).passed


def test_domain_vector_warning_replaced_by_violation():
    """domain_vector absence must NOT appear only in warnings — must be violation."""
    n = CognitiveNode(
        node_id="n1", surface="n1", normalized="n1", node_type="thing",
        role_vector={**zero_role_vector(), "thing": 1.0},
        domain_vector={},
    )
    g = _graph(nodes=[n])
    result = check_mathematical_contract(g)
    # Must be in violations (not just warnings)
    dv_in_violations = any("domain_vector" in v for v in result.violations)
    assert dv_in_violations, "domain_vector absence must be a VIOLATION, not just a warning"


# ══════════════════════════════════════════════════════════════════════════════
# Issue 3: cause_has_effect invariant must fail (blocking)
# ══════════════════════════════════════════════════════════════════════════════

def test_cause_without_effect_fails_blocking_invariant():
    """A cause node with no effect target must cause a contract violation."""
    cause_n = _node("cause1", "cause")
    thing_n = _node("thing1", "thing")  # not an effect type
    edge = CognitiveEdge(
        edge_id="e1", source="cause1", relation="causes", target="thing1",
    )
    g = _graph(nodes=[cause_n, thing_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert not result.passed, "cause without typed effect must fail contract"
    assert any("cause" in v.lower() or "effect" in v.lower() for v in result.violations)


def test_unrelated_caused_by_does_not_satisfy_cause():
    """A caused_by edge pointing elsewhere must NOT satisfy the causes requirement."""
    cause_n = _node("cause1", "cause")
    thing_n = _node("thing1", "thing")
    other_n = _node("other1", "thing")
    # cause1 causes thing1, but caused_by goes from other1 (unrelated)
    cause_edge = CognitiveEdge(edge_id="e1", source="cause1", relation="causes", target="thing1")
    unrelated_edge = CognitiveEdge(edge_id="e2", source="other1", relation="caused_by", target="cause1")
    g = _graph(nodes=[cause_n, thing_n, other_n], edges=[cause_edge, unrelated_edge])
    result = check_mathematical_contract(g)
    # thing1 is not an effect-type node AND has no caused_by edge FROM thing1
    assert not result.passed


def test_cause_with_tied_effect_passes():
    """A cause edge to an effect-typed node must pass the contract."""
    cause_n = _node("cause1", "cause")
    effect_n = _node("effect1", "effect")
    edge = CognitiveEdge(edge_id="e1", source="cause1", relation="causes", target="effect1")
    g = _graph(nodes=[cause_n, effect_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


def test_cause_with_caused_by_edge_from_target_passes():
    """A cause edge where target has caused_by edge from itself must pass."""
    cause_n = _node("cause1", "cause")
    target_n = _node("target1", "thing")  # not effect type
    effect_n = _node("effect1", "effect")
    cause_edge = CognitiveEdge(edge_id="e1", source="cause1", relation="causes", target="target1")
    caused_by_edge = CognitiveEdge(edge_id="e2", source="target1", relation="caused_by", target="effect1")
    g = _graph(nodes=[cause_n, target_n, effect_n], edges=[cause_edge, caused_by_edge])
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


def test_cause_without_effect_fails_invariant_as_blocking():
    """The invariant validator must mark cause_has_effect as blocking violation."""
    cause_n = _node("cause1", "cause")
    thing_n = _node("thing1", "thing")
    edge = CognitiveEdge(edge_id="e1", source="cause1", relation="causes", target="thing1")
    g = _graph(nodes=[cause_n, thing_n], edges=[edge])
    inv_result = validate_invariants(g)
    # Must produce a violation (not just a warning) with blocking severity
    cause_violations = [v for v in inv_result.violations if "cause" in v.description.lower()]
    assert cause_violations or not inv_result.passed, \
        "cause_has_effect must produce a blocking violation"


# ══════════════════════════════════════════════════════════════════════════════
# Issue 4: tool/API not evidence — trust_policy check
# ══════════════════════════════════════════════════════════════════════════════

def test_tool_support_without_evidence_or_trust_policy_fails():
    """Tool node supporting without evidence_refs or trust_policy must fail."""
    tool_n = _node("api1", "tool")
    claim_n = _node("claim1", "claim")
    edge = CognitiveEdge(
        edge_id="e1", source="api1", relation="supports", target="claim1",
        evidence_refs=[],  # no evidence
        metadata={},  # no trust_policy
    )
    g = _graph(nodes=[tool_n, claim_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert not result.passed
    assert any("tool" in v.lower() or "trust" in v.lower() for v in result.violations)


def test_tool_support_with_trust_policy_passes():
    """Tool node with trust_policy=trusted must pass the contract."""
    tool_n = _node("api1", "tool")
    claim_n = _node("claim1", "claim")
    edge = CognitiveEdge(
        edge_id="e1", source="api1", relation="supports", target="claim1",
        evidence_refs=[],
        metadata={"trust_policy": {"trusted": True, "source_trust_score": 0.9}},
    )
    g = _graph(nodes=[tool_n, claim_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


def test_api_is_not_authority_by_itself():
    """Source node used as sourced_from without trust_policy must fail."""
    source_n = _node("src1", "source")
    claim_n = _node("claim1", "claim")
    edge = CognitiveEdge(
        edge_id="e1", source="src1", relation="sourced_from", target="claim1",
        evidence_refs=[],
        metadata={},
    )
    g = _graph(nodes=[source_n, claim_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert not result.passed


def test_source_requires_trust_policy_before_evidence_acceptance():
    """Source node with evidence_refs (but no trust_policy) should pass — evidence is valid."""
    source_n = _node("src1", "source", ev=["ref_001"])
    claim_n = _node("claim1", "claim")
    edge = CognitiveEdge(
        edge_id="e1", source="src1", relation="supports", target="claim1",
        evidence_refs=["ref_001"],  # has evidence
        metadata={},
    )
    g = _graph(nodes=[source_n, claim_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


def test_tool_support_with_trust_score_passes():
    """Tool with source_trust_score >= 0.7 must pass."""
    tool_n = _node("tool1", "tool")
    claim_n = _node("claim1", "claim")
    edge = CognitiveEdge(
        edge_id="e1", source="tool1", relation="supports", target="claim1",
        evidence_refs=[],
        metadata={"trust_policy": {"source_trust_score": 0.85}},
    )
    g = _graph(nodes=[tool_n, claim_n], edges=[edge])
    result = check_mathematical_contract(g)
    assert result.passed, f"violations: {result.violations}"


# ══════════════════════════════════════════════════════════════════════════════
# Issue 5: Level 9/10 evaluator measures actual domains/graph/vectors
# ══════════════════════════════════════════════════════════════════════════════

def test_level9_requires_domain_vector():
    """Level 9 unit without metadata.domains must score 0."""
    from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
    from mcd.curriculum.cognitive_unit import CognitiveUnit
    from mcd.curriculum.reality_frame import RealityFrame
    evaluator = CurriculumEvaluator()
    unit = CognitiveUnit(
        unit_id="test-L09-no-domain",
        input_text="test",
        level=9,
        target_layer="domain_reasoning",
        expected_frame=RealityFrame(evidence_need=["domain_classification"]),
        certainty_policy="probable_knowledge",
        metadata={},  # no domains
    )
    score = evaluator._score_unit(unit)
    assert score == 0.0, f"Expected 0 for unit without domains, got {score}"


def test_level9_requires_domain_summary_or_domain_edges():
    """Level 9 unit with metadata.domains must score > 0.0."""
    from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
    from mcd.curriculum.cognitive_unit import CognitiveUnit
    from mcd.curriculum.reality_frame import RealityFrame
    evaluator = CurriculumEvaluator()
    unit = CognitiveUnit(
        unit_id="test-L09-with-domain",
        input_text="test",
        level=9,
        target_layer="domain_reasoning",
        expected_frame=RealityFrame(evidence_need=["domain_classification"]),
        certainty_policy="probable_knowledge",
        metadata={"domains": ["science", "method"]},
    )
    score = evaluator._score_unit(unit)
    assert score > 0.0, "Level 9 unit with domains should score > 0"


def test_level10_requires_nodes_edges_vectors():
    """Level 10 unit with nodes, edges, and vector_hint must score higher than bare unit."""
    from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
    from mcd.curriculum.cognitive_unit import CognitiveUnit
    from mcd.curriculum.reality_frame import RealityFrame, RelationTriple
    evaluator = CurriculumEvaluator()
    full_unit = CognitiveUnit(
        unit_id="test-L10-full",
        input_text="test",
        level=10,
        target_layer="graph_vector_composition",
        expected_frame=RealityFrame(
            things=["العالم", "الحقيقة"],
            relations=[RelationTriple("العالم", "agent_of", "يكتشف", None)],
            evidence_need=["graph_construction", "vector_composition"],
        ),
        certainty_policy="strong_knowledge",
        metadata={"vector_hint": {"role": "agent_action", "domain": "science"}},
    )
    bare_unit = CognitiveUnit(
        unit_id="test-L10-bare",
        input_text="test",
        level=10,
        target_layer="graph_vector_composition",
        expected_frame=RealityFrame(evidence_need=[]),
        certainty_policy="probable_knowledge",
        metadata={},
    )
    full_score = evaluator._score_unit(full_unit)
    bare_score = evaluator._score_unit(bare_unit)
    assert full_score > bare_score, f"Full unit ({full_score}) should score higher than bare ({bare_score})"


def test_level10_missing_graph_scores_zero():
    """Level 10 unit with no nodes and no vector_hint must score 0."""
    from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
    from mcd.curriculum.cognitive_unit import CognitiveUnit
    from mcd.curriculum.reality_frame import RealityFrame
    evaluator = CurriculumEvaluator()
    unit = CognitiveUnit(
        unit_id="test-L10-empty",
        input_text="test",
        level=10,
        target_layer="graph_vector_composition",
        expected_frame=RealityFrame(),
        certainty_policy="probable_knowledge",
        metadata={},  # no vector_hint, no nodes
    )
    score = evaluator._score_unit(unit)
    assert score == 0.0, f"Expected 0 for unit without graph/vectors, got {score}"


def test_level10_valid_graph_scores_high():
    """Level 10 unit with full graph structure must score >= 0.7."""
    from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
    from mcd.curriculum.cognitive_unit import CognitiveUnit
    from mcd.curriculum.reality_frame import RealityFrame, RelationTriple
    evaluator = CurriculumEvaluator()
    unit = CognitiveUnit(
        unit_id="test-L10-high",
        input_text="test",
        level=10,
        target_layer="graph_vector_composition",
        expected_frame=RealityFrame(
            things=["العالم", "الحقيقة", "التجربة"],
            relations=[
                RelationTriple("العالم", "agent_of", "يكتشف", None),
                RelationTriple("التجربة", "instrument_of", "يكتشف", None),
            ],
            evidence_need=["graph_construction", "vector_composition"],
        ),
        certainty_policy="strong_knowledge",
        metadata={"vector_hint": {"role": "agent_action", "domain": "science", "certainty": "strong"}},
        tags=["graph_vector_composition", "science"],
    )
    score = evaluator._score_unit(unit)
    assert score >= 0.7, f"Expected >= 0.7, got {score}"


# ══════════════════════════════════════════════════════════════════════════════
# Mutation tests
# ══════════════════════════════════════════════════════════════════════════════

def test_mutation_remove_vectors_fails():
    """remove_role_vector and remove_domain_vector mutations must be detected."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    rv_result = next(r for r in report.results if r.mutation_name == "remove_role_vector")
    dv_result = next(r for r in report.results if r.mutation_name == "remove_domain_vector")
    assert rv_result.passed, f"remove_role_vector not detected: {rv_result.explanation}"
    assert dv_result.passed, f"remove_domain_vector not detected: {dv_result.explanation}"


def test_mutation_input_label_only_fails():
    """replace_structured_frame_with_label_only mutation must be detected."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    result = next(r for r in report.results if r.mutation_name == "replace_structured_frame_with_label_only")
    assert result.passed, f"label_only mutation not detected: {result.explanation}"


def test_mutation_api_as_evidence_fails():
    """mark_api_as_evidence_without_trust mutation must be detected."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    result = next(r for r in report.results if r.mutation_name == "mark_api_as_evidence_without_trust")
    assert result.passed, f"api_evidence mutation not detected: {result.explanation}"


def test_mutation_near_certainty_without_evidence_fails():
    """set_near_certainty_without_evidence mutation must be detected."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    result = next(r for r in report.results if r.mutation_name == "set_near_certainty_without_evidence")
    assert result.passed, f"near_certainty mutation not detected: {result.explanation}"


def test_mutation_remove_effect_for_cause_fails():
    """remove_effect_for_cause mutation must be detected."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    result = next(r for r in report.results if r.mutation_name == "remove_effect_for_cause")
    assert result.passed, f"cause_without_effect mutation not detected: {result.explanation}"


def test_mutation_report_has_all_types():
    """Mutation report must cover all 10 mutation types."""
    from mcd.curriculum.mutation_tests import run_mutation_tests, MUTATION_TYPES
    report = run_mutation_tests()
    names = {r.mutation_name for r in report.results}
    for mut in MUTATION_TYPES:
        assert mut in names, f"Missing mutation type: {mut}"


def test_mutation_pass_rate_above_threshold():
    """Overall mutation pass rate must be >= 0.95."""
    from mcd.curriculum.mutation_tests import run_mutation_tests
    report = run_mutation_tests()
    assert report.pass_rate >= 0.95, f"Mutation pass rate {report.pass_rate} < 0.95"


# ══════════════════════════════════════════════════════════════════════════════
# Quality Lock
# ══════════════════════════════════════════════════════════════════════════════

def test_quality_lock_returns_report():
    """run_quality_lock must return a CurriculumQualityLockReport."""
    from mcd.curriculum.quality_lock import run_quality_lock, CurriculumQualityLockReport
    report = run_quality_lock()
    assert isinstance(report, CurriculumQualityLockReport)


def test_quality_lock_status_is_locked_or_blocked():
    """Quality lock status must be 'locked' or 'blocked'."""
    from mcd.curriculum.quality_lock import run_quality_lock
    report = run_quality_lock()
    assert report.status in ("locked", "blocked")


def test_quality_lock_to_dict_has_keys():
    """Quality lock report dict must have all required keys."""
    from mcd.curriculum.quality_lock import run_quality_lock
    d = run_quality_lock().to_dict()
    for k in ("status", "contract_score", "golden_pass_rate", "adversarial_detection_rate",
              "mutation_test_pass_rate", "level9_score", "level10_score",
              "invariant_pass_rate", "blockers", "next_actions", "is_locked"):
        assert k in d, f"Missing key: {k}"


def test_quality_lock_to_markdown_contains_status():
    """Quality lock markdown must contain status."""
    from mcd.curriculum.quality_lock import run_quality_lock
    md = run_quality_lock().to_markdown()
    assert "LOCKED" in md or "BLOCKED" in md


def test_quality_lock_mutation_rate_is_1():
    """All 10 mutation types must be caught, giving 1.0 mutation pass rate."""
    from mcd.curriculum.quality_lock import run_quality_lock
    report = run_quality_lock()
    assert report.mutation_test_pass_rate == 1.0, \
        f"Expected mutation_test_pass_rate=1.0, got {report.mutation_test_pass_rate}"


def test_quality_lock_golden_pass_rate_is_high():
    """Golden examples must pass the contract at a high rate."""
    from mcd.curriculum.quality_lock import run_quality_lock
    report = run_quality_lock()
    assert report.golden_pass_rate >= 0.98


def test_quality_lock_scores_between_0_and_1():
    """All quality lock scores must be in [0, 1]."""
    from mcd.curriculum.quality_lock import run_quality_lock
    r = run_quality_lock()
    for attr in ("contract_score", "golden_pass_rate", "adversarial_detection_rate",
                 "mutation_test_pass_rate", "level9_score", "level10_score",
                 "invariant_pass_rate", "graph_vector_score"):
        val = getattr(r, attr)
        assert 0.0 <= val <= 1.0, f"{attr}={val} out of [0,1]"


# ══════════════════════════════════════════════════════════════════════════════
# Qualification Bridge — quality lock gates
# ══════════════════════════════════════════════════════════════════════════════

def test_qualification_blocked_if_contract_quality_lock_false():
    """Qualification must be blocked when contract_quality_lock_passed is False."""
    from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics
    m = CurriculumQualificationMetrics(
        contract_quality_lock_passed=False,
        golden_examples_pass_rate=1.0,
        adversarial_failure_detection=1.0,
        level9_domain_contract_score=1.0,
        level10_graph_vector_contract_score=1.0,
        mutation_tests_passed=True,
        dataset_score_estimate=5.0,
        calibration_score_estimate=5.0,
        industrial_testing_score_estimate=5.0,
        source_trust_score_estimate=5.0,
        graph_contract_score=1.0,
        vector_contract_score=1.0,
        invariant_pass_rate=1.0,
        adversarial_pass_rate=1.0,
    )
    assert not m.is_qualified(), "Must not qualify with contract_quality_lock_passed=False"


def test_qualification_blocked_if_level10_score_low():
    """Qualification must be blocked when level10_graph_vector_contract_score is low."""
    from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics
    m = CurriculumQualificationMetrics(
        contract_quality_lock_passed=True,
        golden_examples_pass_rate=1.0,
        adversarial_failure_detection=1.0,
        level9_domain_contract_score=1.0,
        level10_graph_vector_contract_score=0.5,  # too low
        mutation_tests_passed=True,
        dataset_score_estimate=5.0,
        calibration_score_estimate=5.0,
        industrial_testing_score_estimate=5.0,
        source_trust_score_estimate=5.0,
        graph_contract_score=1.0,
        vector_contract_score=1.0,
        invariant_pass_rate=1.0,
        adversarial_pass_rate=1.0,
    )
    assert not m.is_qualified(), "Must not qualify with low level10 score"


def test_qualification_blocked_if_mutation_tests_fail():
    """Qualification must be blocked when mutation_tests_passed is False."""
    from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics
    m = CurriculumQualificationMetrics(
        contract_quality_lock_passed=True,
        golden_examples_pass_rate=1.0,
        adversarial_failure_detection=1.0,
        level9_domain_contract_score=1.0,
        level10_graph_vector_contract_score=1.0,
        mutation_tests_passed=False,  # failing
        dataset_score_estimate=5.0,
        calibration_score_estimate=5.0,
        industrial_testing_score_estimate=5.0,
        source_trust_score_estimate=5.0,
        graph_contract_score=1.0,
        vector_contract_score=1.0,
        invariant_pass_rate=1.0,
        adversarial_pass_rate=1.0,
    )
    assert not m.is_qualified(), "Must not qualify with mutation_tests_passed=False"


def test_qualification_passes_when_all_quality_gates_pass():
    """All quality gates passing must be a prerequisite for qualification."""
    from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics
    m = CurriculumQualificationMetrics(
        contract_quality_lock_passed=True,
        golden_examples_pass_rate=1.0,
        adversarial_failure_detection=1.0,
        level9_domain_contract_score=1.0,
        level10_graph_vector_contract_score=1.0,
        mutation_tests_passed=True,
        dataset_score_estimate=5.0,
        calibration_score_estimate=5.0,
        industrial_testing_score_estimate=5.0,
        source_trust_score_estimate=5.0,
        graph_contract_score=1.0,
        vector_contract_score=1.0,
        invariant_pass_rate=1.0,
        adversarial_pass_rate=1.0,
    )
    assert m.is_qualified(), "Must qualify when all gates pass"


def test_qualification_metrics_to_dict_has_quality_lock_fields():
    """to_dict must include all Phase 5.3.2 quality lock fields."""
    from mcd.curriculum.qualification_bridge import CurriculumQualificationMetrics
    m = CurriculumQualificationMetrics()
    d = m.to_dict()
    for key in (
        "contract_quality_lock_passed",
        "golden_examples_pass_rate",
        "adversarial_failure_detection",
        "level9_domain_contract_score",
        "level10_graph_vector_contract_score",
        "mutation_tests_passed",
    ):
        assert key in d, f"Missing key: {key}"


# ══════════════════════════════════════════════════════════════════════════════
# CLI integration tests for new commands
# ══════════════════════════════════════════════════════════════════════════════

def _run_cli(cmd: list[str]):
    import subprocess, sys, os
    from pathlib import Path
    repo_root = str(Path(__file__).parent.parent)
    env = {**os.environ, "PYTHONPATH": "src"}
    return subprocess.run(
        [sys.executable, "-m", "mcd.cli"] + cmd,
        capture_output=True, text=True, env=env,
        cwd=repo_root,
    )


def test_curriculum_quality_lock_cli_exits_0():
    result = _run_cli(["curriculum-quality-lock", "--output", "json"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_quality_lock_cli_json_output():
    import json
    result = _run_cli(["curriculum-quality-lock", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "status" in data
    assert data["status"] in ("locked", "blocked")


def test_curriculum_quality_lock_cli_markdown_output():
    result = _run_cli(["curriculum-quality-lock", "--output", "markdown"])
    assert result.returncode == 0
    assert "LOCKED" in result.stdout or "BLOCKED" in result.stdout


def test_curriculum_mutation_test_cli_exits_0():
    result = _run_cli(["curriculum-mutation-test", "--output", "json"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_mutation_test_cli_json_output():
    import json
    result = _run_cli(["curriculum-mutation-test", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "total" in data
    assert "passed" in data
    assert "pass_rate" in data
    assert data["total"] == 10


def test_curriculum_contract_check_cli_exits_0():
    result = _run_cli(["curriculum-contract-check", "--output", "json"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_curriculum_contract_check_cli_passes():
    """curriculum-contract-check must pass on a properly built curriculum graph."""
    import json
    result = _run_cli(["curriculum-contract-check", "--output", "json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["passed"] is True, f"violations: {data.get('violations')}"
