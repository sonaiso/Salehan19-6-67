# Cognitive Graph–Vector Contract

## Overview

Phase 5.3.1 introduces a **mathematical contract** that every `CognitiveGraph` must satisfy before output is trusted. The contract formalises the 12 cognitive invariants.

Phase 5.3.2 strengthens the contract by making it **governing**: every rule that is declared must also be enforced — violations must cause `passed=False`, not just warnings.

## Contract Rules

| # | Rule | Enforcement | Module |
|---|------|-------------|--------|
| 1 | Graph must have nodes (no input→label shortcut) | violation | `mathematical_contract` |
| 2 | Every node must carry a `role_vector` **and** `domain_vector` | **violation (mandatory)** | `mathematical_contract` |
| 3 | Vectors must match registered dimensions | violation | `vector_validator` |
| 4 | Every edge must be closed (endpoints in graph) | violation | `mathematical_contract` |
| 5 | Cause nodes must have effect targets (same source/target) | **violation (blocking)** | `mathematical_contract` |
| 6 | Near-certainty requires evidence_refs | violation | `mathematical_contract` |
| 7 | Ambiguous input cannot carry `near_certainty` policy | violation | `mathematical_contract` |
| 8 | Harm ≠ Haram (distinct domains, no entail edge) | violation | `mathematical_contract` |
| 9 | Tool/API cannot be standalone evidence without `trust_policy` | **violation (with trust_policy check)** | `mathematical_contract` |
| 10 | Metaphors are not literal facts | violation | `cognitive_graph` invariants |
| 11 | Source edges require trust policy metadata | violation | `mathematical_contract` |
| 12 | Graph invariants must hold per `cognitive_invariants.json` | violation | `invariant_validator` |

## domain_vector: Mandatory (Phase 5.3.2)

**`domain_vector` is mandatory for every node.** Absence is a contract violation, not a warning.

```python
# BEFORE (Phase 5.3.1 — incorrect):
if not node.domain_vector:
    warnings.append(...)  # silently allowed

# AFTER (Phase 5.3.2 — correct):
if not node.domain_vector:
    violations.append(...)  # contract violation → passed=False
```

Rationale: the methodology depends on domain membership. A node without a domain vector has no domain identity and cannot participate in domain reasoning.

## cause_has_effect: Blocking Invariant (Phase 5.3.2)

A `causes` edge must point to a node that is either:
- typed as `effect`, OR
- has a `caused_by` edge originating **from** that same target

An unrelated `caused_by` edge elsewhere in the graph does NOT satisfy this invariant.

```python
# Violation: cause1 → thing1 (thing1 is not effect-typed, has no caused_by from it)
CognitiveEdge(source="cause1", relation="causes", target="thing1")  # FAILS

# Pass: cause1 → effect1 (effect-typed)
CognitiveEdge(source="cause1", relation="causes", target="effect1")  # PASSES

# Pass: cause1 → target1 (target1 has caused_by edge)
CognitiveEdge(source="cause1", relation="causes", target="target1")  # PASSES if:
CognitiveEdge(source="target1", relation="caused_by", target="effect1")
```

## tool/API Evidence: Trust Policy Required (Phase 5.3.2)

When a `tool` or `source` node is used in an evidence relation (`supports`, `sourced_from`, `requires_evidence`), at least ONE of the following must be present:

1. `edge.evidence_refs` is non-empty, OR
2. `edge.metadata["trust_policy"]["trusted"] == True`, OR
3. `edge.metadata["trust_policy"]["source_trust_score"] >= 0.7`

```python
# Violation: tool supports without any trust basis
CognitiveEdge(source="api1", relation="supports", target="claim1",
              evidence_refs=[], metadata={})  # FAILS

# Pass: tool supports with trust policy
CognitiveEdge(source="api1", relation="supports", target="claim1",
              metadata={"trust_policy": {"trusted": True}})  # PASSES

# Pass: tool supports with evidence
CognitiveEdge(source="api1", relation="supports", target="claim1",
              evidence_refs=["ref_001"])  # PASSES
```

## Level 9 — Domain Reasoning Requirements

Level 9 units must have:
- `metadata["domains"]` — non-empty list of domain names
- `evidence_need` containing at least one domain-related term (e.g., `"domain_classification"`)

A Level 9 unit without `metadata["domains"]` scores **0.0** in the evaluator.

## Level 10 — Graph/Vector Composition Requirements

Level 10 units must have:
- `metadata["vector_hint"]` — role/domain/certainty vector hints
- `expected_frame.things` — actual node list (not empty)
- `expected_frame.relations` — actual edges
- `evidence_need` containing `"graph_construction"` or `"vector_composition"`

A Level 10 unit without nodes or vector_hint scores **0.0** in the evaluator.

## Vector Dimensions

```
role_vector    → ROLE_DIMENSIONS    (see vector_space.py)
                 ["thing", "property", "action", "relation", "cause", "effect",
                  "instrument", "time", "place", "evidence", "claim", "judgment",
                  "source", "tool"]

domain_vector  → DOMAIN_DIMENSIONS  (see vector_space.py)
                 ["universe", "human", "life", "science", "culture", "civilization",
                  "technology", "language", "method", "industrial", "education",
                  "enterprise", "safety", "product"]
```

Note: `"domain"` is a valid **node_type** but NOT a role_vector dimension. Use `"thing"` or another valid dimension for domain-typed nodes in the role vector.

## Usage

```python
from mcd.curriculum import check_mathematical_contract, CognitiveGraph

result = check_mathematical_contract(graph)
if not result.passed:
    for v in result.violations:
        print("VIOLATION:", v)
```

## CLI

```bash
# Check contract on curriculum graph
python -m mcd.cli curriculum-contract-check --output json

# Run quality lock (Phase 5.3.2)
python -m mcd.cli curriculum-quality-lock --output markdown

# Run mutation tests (Phase 5.3.2)
python -m mcd.cli curriculum-mutation-test --output json
```

