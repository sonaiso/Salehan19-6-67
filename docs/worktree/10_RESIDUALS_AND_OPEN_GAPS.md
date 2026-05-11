# 10 — Residuals and Open Gaps

## Residual ledger

### 1) root_runtime_contract_incomplete
- **severity:** high
- **why it matters:** the canonical root worktree map now exists in docs/spec/schema/tests, but branch growth can still drift unless those structures are enforced through executable runtime and governance paths
- **what fixes it:** bind the root-first worktree index/spec/schema/tests into runtime contracts, governance validation, and reverse-traceable enforcement
- **proposed next PR:** Phase 2.1 — Formalize Mind Geometry Runtime Contracts

### 2) mind_geometry_not_runtime_complete
- **severity:** high
- **why it matters:** mind-level distinctions are not fully executable in runtime contracts
- **what fixes it:** add runtime contracts for distinction/identity/concept transitions
- **proposed next PR:** Phase 2.1 — Mind Geometry Runtime Contracts

### 3) language_geometry_fragmented
- **severity:** medium
- **why it matters:** language nodes are spread across docs and runtime without one executable bridge
- **what fixes it:** unify language reveal contracts and testable transitions
- **proposed next PR:** Phase 2.2 — Language Reveals Mind Runtime Bridge

### 4) signifier_signified_not_fully_bound
- **severity:** high
- **why it matters:** mapping gaps risk linguistic analysis being misread as evidence
- **what fixes it:** add explicit signifier-signified relation validators
- **proposed next PR:** Phase 2.2 — Signifier/Signified Runtime Bridge

### 5) concept_judgment_evidence_bridge_partial
- **severity:** high
- **why it matters:** concept output does not fully enforce downstream evidence gates
- **what fixes it:** complete concept -> judgment -> evidence executable chain
- **proposed next PR:** Phase 2.3 — Concept to Evidence Bridge

### 6) bayani_runtime_mixed_with_spec
- **severity:** medium
- **why it matters:** runtime and specification concerns can blur operational confidence
- **what fixes it:** clearer runtime/spec boundaries and validation paths
- **proposed next PR:** Phase 2.3 — Runtime/Spec Boundary Hardening

### 7) coding_copilot_branch_ahead_of_mind_root
- **severity:** medium
- **why it matters:** industrial branch maturity can hide unfinished root architecture
- **what fixes it:** complete root worktree progression before adding new industrial scope
- **proposed next PR:** Phase 2.1 — Root Completion Alignment

### 8) training_trace_not_yet_built
- **severity:** medium
- **why it matters:** future training loops require governed trace datasets
- **what fixes it:** implement training-trace extraction from governed nodes
- **proposed next PR:** Phase 2.4 — TrainingTrace from Worktree Nodes

### 9) industrial_gateway_deferred
- **severity:** low
- **why it matters:** productionized gateway path remains roadmap-level only
- **what fixes it:** define industrial gateway scope and guarded rollout criteria
- **proposed next PR:** Future industrial gateway planning PR

### 10) ruleset_enforcement_needs_live_pr_test
- **severity:** high
- **why it matters:** configuration snapshot alone is HYPOTHESIS until merge-lock behavior is observed
- **what fixes it:** tiny docs PR proving merge stays blocked until required check succeeds
- **proposed next PR:** Governance evidence PR with ProofObject/GovernanceGate/ReverseTrace
