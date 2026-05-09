# Cognitive Graph–Vector Contract

## Overview

Phase 5.3.1 introduces a **mathematical contract** that every `CognitiveGraph` must satisfy before output is trusted. The contract formalises the 12 cognitive invariants.

## Contract Rules

| # | Rule | Module |
|---|------|--------|
| 1 | Graph must have nodes (no input→label shortcut) | `mathematical_contract` |
| 2 | Every node must carry a `role_vector` and `domain_vector` | `mathematical_contract` |
| 3 | Vectors must match registered dimensions | `vector_validator` |
| 4 | Every edge must be closed (endpoints in graph) | `mathematical_contract` |
| 5 | Cause nodes must have effect targets | `mathematical_contract` |
| 6 | Near-certainty requires evidence_refs | `mathematical_contract` |
| 7 | Ambiguous input cannot carry `near_certainty` policy | `mathematical_contract` |
| 8 | Harm ≠ Haram (distinct domains, no entail edge) | `mathematical_contract` |
| 9 | Tool/API cannot support without trust policy | `mathematical_contract` |
| 10 | Metaphors are not literal facts | `cognitive_graph` invariants |
| 11 | Source edges require trust policy metadata | `mathematical_contract` |
| 12 | Graph invariants must hold per `cognitive_invariants.json` | `invariant_validator` |

## Vector Dimensions

```
role_vector    → ROLE_DIMENSIONS    (see vector_space.py)
domain_vector  → DOMAIN_DIMENSIONS  (see vector_space.py)
```

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
python -m mcd curriculum-contract-check --profile full_curriculum
```
