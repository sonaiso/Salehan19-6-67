# Curriculum Quality Lock — Phase 5.3.2

## 1. Why PR #28 Was Not Sufficient

PR #28 (Phase 5.3.1) introduced the correct **architectural shape**:
- `CognitiveNode`, `CognitiveEdge`, `CognitiveGraph`
- `VectorRegistry`, `MathematicalContract`, `InvariantValidator`
- Golden examples, adversarial curriculum, 1251 training examples

However, code review (Copilot) revealed that several contracts were declared but not enforced:

| Issue | Symptom |
|-------|---------|
| `curriculum-contract-check` built nodes without `role_vector`/`domain_vector` | Graph violated its own contract |
| `domain_vector` documented as mandatory but coded as `warning` only | Nodes could exist without domain identity |
| `cause_has_effect` invariant added warnings but never set `passed_check=False` | Blocking invariant silently failed |
| `tool/API not evidence` ignored `trust_policy` metadata | Trust mechanism bypassed |
| Level 9/10 evaluator only checked `evidence_need` | Graph and vector composition went unmeasured |

These meant that `qualified_for_api_phase` could be reported based on validators that **never failed** when they should.

---

## 2. What Is a Quality Lock?

A **quality lock** is the proof that a mathematical contract is **governing**, not merely **present**.

A contract exists when code defines the rules.
A contract **governs** when:

1. A valid example satisfies all rules.
2. A mutated (corrupted) example fails the rules.
3. The score is derived from actual checks, not defaults.

Phase 5.3.2 adds `curriculum-quality-lock` which verifies both directions — pass and fail.

---

## 3. Why Mutation Tests?

Mutation tests answer the question:

> "Does the validator actually catch failures, or does it just validate successful examples?"

A mutation test:
1. Takes a valid golden example
2. Applies a targeted corruption (mutation)
3. Verifies that validators **reject** the corrupted version

**10 mutation types are tested:**

| Mutation | What it breaks |
|----------|---------------|
| `remove_role_vector` | Node identity lost |
| `remove_domain_vector` | Domain membership lost |
| `remove_edge_target` | Graph closure violated |
| `remove_edge_source` | Graph closure violated |
| `remove_effect_for_cause` | Cause–effect invariant broken |
| `set_near_certainty_without_evidence` | Certainty policy violated |
| `mark_api_as_evidence_without_trust` | Tool evidence rule broken |
| `remove_domain_from_level9` | Domain reasoning missing |
| `remove_graph_from_level10` | Composition missing |
| `replace_structured_frame_with_label_only` | Input→label shortcut |

If all 10 mutations are caught, `mutation_test_pass_rate = 1.0`.

---

## 4. How Do We Know the Mathematical Contract Is Governing?

The contract governs when:

```
✅ check_mathematical_contract(valid_graph).passed == True
✅ check_mathematical_contract(mutated_graph).passed == False  (for each mutation)
✅ validate_invariants(graph_with_cause_without_effect).passed == False
✅ validate_invariants(tool_without_trust).passed == False
✅ score derives from actual check results (no hardcoded 0.95)
```

The `curriculum-quality-lock` command verifies all these in a single run.

---

## 5. Dataset Size vs. Dataset Trust

A large dataset is not the same as a trusted dataset.

| Dimension | What it measures |
|-----------|-----------------|
| Size (1251 examples) | Coverage — how many patterns are included |
| Golden pass rate (≥ 0.98) | Correctness — valid examples satisfy the contract |
| Adversarial detection rate (≥ 0.95) | Robustness — invalid patterns are identified |
| Mutation pass rate (≥ 0.95) | Governance — corruptions are caught |

A dataset of 10,000 examples that are never validated by a governing contract provides **false confidence**. A dataset of 100 examples where every mutation is caught provides **real assurance**.

---

## 6. How Quality Lock Affects Pre-API Qualification

The `QualificationBridge` now enforces a strict gate:

```python
def is_qualified(self) -> bool:
    return (
        self._quality_lock_gates_pass()  # <-- NEW: must pass first
        and self.dataset_score_estimate >= DATASET_THRESHOLD
        and ...
    )
```

**Quality lock gates (all must pass):**

| Gate | Threshold |
|------|-----------|
| `contract_quality_lock_passed` | `True` |
| `golden_examples_pass_rate` | ≥ 0.98 |
| `adversarial_failure_detection` | ≥ 0.95 |
| `level9_domain_contract_score` | ≥ 0.95 |
| `level10_graph_vector_contract_score` | ≥ 0.95 |
| `mutation_tests_passed` | `True` |

Only when all gates pass does the system proceed to evaluate the numeric scores.

---

## 7. Why No API Before `locked`?

The API is a public commitment. Once deployed:

- Users trust the output
- Errors are amplified by traffic
- Rollbacks are expensive

The quality lock ensures:

```
API phase begins only when:
curriculum-quality-lock status = "locked"
pre-api-qualification status = "qualified_for_api_phase"
```

If the contract is not governing, the API output is built on unmeasured foundations. The quality lock closes this gap before any API work begins.

---

## CLI Commands (Phase 5.3.2)

```bash
# Run quality lock (verifies contract governance)
python -m mcd.cli curriculum-quality-lock --output markdown
python -m mcd.cli curriculum-quality-lock --output json

# Run mutation tests (verifies validators catch corruptions)
python -m mcd.cli curriculum-mutation-test --output json

# Run contract check on curriculum graph
python -m mcd.cli curriculum-contract-check --output json

# Run full qualification (now requires quality lock)
python -m mcd.cli curriculum-qualification --output markdown

# Run pre-API qualification (only valid after quality lock passes)
python -m mcd.cli pre-api-qualification --tests-pass true --readiness-report-exists true --output markdown
```

---

## Quality Lock Report Interpretation

| Status | Meaning |
|--------|---------|
| `locked` | All gates pass — contract is governing |
| `blocked` | One or more gates fail — cannot proceed to API |

The report includes `blockers` (which gates failed) and `next_actions` (how to resolve them).

---

## Thresholds

| Metric | Threshold |
|--------|-----------|
| `contract_score` | ≥ 0.98 |
| `golden_pass_rate` | ≥ 0.98 |
| `adversarial_detection_rate` | ≥ 0.95 |
| `mutation_test_pass_rate` | ≥ 0.95 |
| `level9_score` | ≥ 0.95 |
| `level10_score` | ≥ 0.95 |
| `invariant_pass_rate` | ≥ 0.98 |
