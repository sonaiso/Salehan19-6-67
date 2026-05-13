# Pilot Risk Register

Status: Controlled pilot risk register (**not production risk closure**).

| Risk ID | Risk | Impact | Likelihood | Current Control | Residual Risk | Required Before Production |
|---|---|---|---|---|---|---|
| PR-01 | Security hardening incomplete | High | Medium | Pilot-only scope, no production claim | Medium | External security audit, threat model, hardening checklist |
| PR-02 | Auth/AuthZ policy not fully enforced for enterprise contexts | High | Medium | Controlled access assumptions | Medium | Real IAM policy, key rotation, authorization model |
| PR-03 | Storage/retention policy not finalized | Medium | Medium | Event log integrity contract | Medium | Retention, archival, deletion and legal compliance policy |
| PR-04 | Replay theorem not fully formalized in Lean | Medium | Medium | Runtime replay integrity contract + tests | Medium | Machine-checked replay formalization |
| PR-05 | Runtime↔formal equivalence is bounded baseline only | Medium | Medium | Truth-table equivalence + test guard | Medium | Broader refinement proof coverage |
| PR-06 | Comparative benchmarks not complete vs external systems | Medium | Medium | Internal readiness and benchmark artifacts | Medium | Comparative benchmark suite and external review |
| PR-07 | Monitoring dashboard package not finalized | Medium | Medium | Persistent traces and governance metrics exist | Medium | Production observability dashboards and SLO tracking |
| PR-08 | Release governance package still pilot-grade | Medium | Low | External audit package + reproducible validation script | Low-Medium | Versioned production release policy and audit report |

## Pilot Risk Decision

- Go for: controlled scientific-industrial pilot
- No-go for: production certification

## Governance Rule

No risk entry may be silently erased. Any unresolved risk must remain explicit in release artifacts.

