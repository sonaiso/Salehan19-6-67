# AGENTS

## Repository governance map
- AFJG is the governing architecture and constitutional law.
- MCD is the implementation namespace.
- Existing subsystems (CFK, Concept Geometry, Math Governance, CLI, tests) remain in place and are governed by Phase 0 rules.

## Contribution contract
All contributions must declare:
1. Affected layer
2. pre/current/post
3. phi_in and phi_out
4. beta role
5. preserved invariants
6. blocked forbidden transitions
7. possible residuals
8. whether Certificate can be issued
9. if yes: where ProofObject, GovernanceGate, ReverseTrace are enforced
10. tests proving compliance
