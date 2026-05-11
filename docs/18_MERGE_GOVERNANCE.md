# 18 — Merge Governance and PR Certification Gate

## Core governance clarifications

- `MERGED` is repository state, not epistemic judgment.
- CI checks are evidence inputs, not judgment outputs.
- Pending checks force `HYPOTHESIS`.
- A PR can be useful and merged but still not epistemically certified.
- Branch protection is required to enforce AFJG rules at GitHub level.
- Repository code can audit violations, but GitHub settings must prevent them.

## Hard merge governance rules

A PR cannot be epistemically merge-allowed when any of the following holds:

- pending checks (`merge_with_pending_checks`)
- failed checks (`failing_checks`)
- missing check evidence (`missing_check_evidence`)
- missing branch protection (`branch_protection_not_configured`)
- missing required checks configuration (`merge_without_required_checks`)
- missing PR certification (`merge_without_pr_certification`)

`CERTIFICATE` is allowed only when all merge gates pass, including reverse trace completion.

## Required GitHub repository settings

1. Require pull request before merging
2. Require status checks to pass before merging
3. Require all required checks to complete
4. Require branches to be up to date before merging
5. Require conversation resolution
6. Do not allow bypass unless explicitly documented
7. Disable auto-merge unless all AFJG gates pass

## Main ruleset evidence (2026-05-11)

Observed governance snapshot:

```text
Ruleset: Active
Target: main
Required status check: AFJG PR Certification
Bypass list: empty
```

This confirms `main` is protected with `AFJG PR Certification` as a required check.

Current residual to close before final repository-level certification:

- execute a tiny docs PR and verify Merge stays blocked until `AFJG PR Certification` succeeds
- ensure `Require branches to be up to date before merging` is enabled in the ruleset
- confirm these controls remain enabled: Require pull request, Require status checks, Block force pushes, Restrict deletions
- prefer enabling conversation resolution before merge if available in the pull request settings

## Operational checklist

- [x] Branch protection enabled on main
- [x] Required checks configured
- [x] PR certification check required
- [ ] Branches required to be up to date before merge
- [ ] Pending checks block merge (validated by test PR)
- [ ] Review conversations resolved before merge

## Enforcement note

`AFJG PR Certification` workflow provides repository-local evidence testing.  
Full merge blocking requires branch protection/ruleset configuration in GitHub settings and marking this workflow as required.
