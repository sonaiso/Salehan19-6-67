# Product Roadmap

## Product 1 — Bayani Verifier API

- **Purpose:** Verify Arabic texts, claims, and model answers under AFJG governance.
- **Input:** Arabic text, claim bundles, model-answer artifacts.
- **Output:** ZERO/HYPOTHESIS/CERTIFICATE + evidence trace + reverse trace + residuals.
- **Current status:** **partial**

## Product 2 — AFJG Coding Copilot Auditor

- **Purpose:** Audit pull requests with governed coding judgment.
- **Input:** Issue context, patch artifacts, tests, checks, and repository evidence.
- **Output:** Governed coding judgment + reverse trace + policy violations.
- **Current status:** **implemented**

## Product 3 — Governed LLM Gateway

- **Purpose:** Gate LLM outputs with AFJG verification before acceptance.
- **Input:** Model prompts, answers, and context evidence.
- **Output:** Governed acceptance/rejection decision with trace.
- **Current status:** **spec-only**

## Product 4 — Judgment-Trace Training Dataset

- **Purpose:** Build supervised datasets from governed judgment traces.
- **Input:** Historical traces, residual logs, and governance decisions.
- **Output:** Structured training/evaluation datasets.
- **Current status:** **future**

## Product 5 — Domain-Specific AFJG Model

- **Purpose:** Train a specialized model constrained by AFJG governance contracts.
- **Input:** Curated governed datasets and domain ontologies.
- **Output:** Domain model optimized for governed verification tasks.
- **Current status:** **future**
