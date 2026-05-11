# AFJG Coding Copilot Auditor

Coding Copilot Auditor is the first industrial dogfood product in this repository.

## Purpose

Audit pull requests under AFJG coding-governance contracts.

## Inputs

- issue intent
- patch artifacts
- repository tests/checks evidence
- architecture and policy signals

## Outputs

- governed coding judgment
- PR reverse trace
- blocked transitions and residual reporting

## Non-Negotiable Rule

```text
MERGED != CERTIFICATE
3/4 checks != CERTIFICATE
```

## Current State

Implemented and tested under `src/mcd/coding_copilot` and related test suites.
