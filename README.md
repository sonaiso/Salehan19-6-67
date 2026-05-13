# Bayani / AFJG Knowledge Verification System

Bayani / AFJG is a governed knowledge-verification and coding-judgment system.

It transforms claims, Arabic texts, model answers, and coding pull requests into governed final judgments:

- ZERO
- HYPOTHESIS
- CERTIFICATE

The repository began as a machine-readable specification and now contains partial runtime implementation under `src/mcd` plus verification tests.

## What it is not

- Not a general LLM
- Not a GPT replacement
- Not raw next-token prediction

## Core Thesis

LLMs propose; AFJG governs judgment.

The system separates:

- linguistic analysis from proof
- model output from evidence
- merged state from certification
- test passing from epistemic certainty
- hypothesis from certificate

## Architecture

| Name | Meaning | Role |
| --- | --- | --- |
| AFJG | Architectonic Fractal Judgment Geometry | Governing constitutional law |
| Bayani | Arabic knowledge verification layer | Arabic epistemic verification |
| MCD | Implementation namespace | Runtime modules, CLI, and tests |
| Mustadil | Reasoner/verifier persona | Governed inference actor |
| GLCFL | Grounded Lexical Cognitive Frame Layer | Lexical grounding layer |
| Coding Copilot Auditor | Industrial test product | Governed coding PR audit |

AFJG is the law. Bayani is the Arabic verifier. MCD is the implementation namespace. Coding Copilot Auditor is the industrial dogfood application.

## Current Implemented Tracks

1. Bayani Verifier
2. Mustadil Pipeline
3. Grounded Lexical Cognitive Frame Layer (GLCFL)
4. Epistemic Decoder
5. AFJG Coding Copilot Auditor

## Final Judgments

```text
ZERO        = fatal violation or invalid proof path
HYPOTHESIS  = plausible structure with incomplete evidence (including internal suspension)
CERTIFICATE = evidence + governance + reverse trace completed
```

No fourth public final judgment is allowed.

## Merge Governance Rule

```text
MERGED != CERTIFICATE
3/4 checks != CERTIFICATE
```

## Quick Commands

```bash
python tests/verify_bayani_repository.py
python -m pytest tests/test_coding_pr_audit.py -v
python -m pytest tests/test_coding_checks_governance.py -v
python -m pytest tests/test_coding_real_pr_fixtures.py -v
```

## Documentation Map

- [Project Overview](docs/00_PROJECT_OVERVIEW.md)
- [Architecture Map](docs/01_ARCHITECTURE_MAP.md)
- [Product Roadmap](docs/02_PRODUCT_ROADMAP.md)
- [Judgment Model](docs/03_JUDGMENT_MODEL.md)
- [Merge Governance](docs/04_MERGE_GOVERNANCE.md)
- [Bayani Verifier API](docs/05_BAYANI_VERIFIER_API.md)
- [Coding Copilot Auditor](docs/06_CODING_COPILOT_AUDITOR.md)
- [Epistemic Decoder](docs/07_EPISTEMIC_DECODER.md)
- [GLCFL](docs/08_GLCFL.md)
- [Mustadil Pipeline](docs/09_MUSTADIL_PIPELINE.md)
- [Developer Guide](docs/10_DEVELOPER_GUIDE.md)
- [Testing and CI](docs/11_TESTING_AND_CI.md)
- [Historical README Archive](docs/12_ARCHIVE_README_HISTORY.md)
- [Worktree Progress](docs/worktree/00_WORKTREE_INDEX.md)

## Current Status

- **CERTIFICATE:** The repository has a strong governed architecture and a testable PR-audit kernel.
- **HYPOTHESIS:** It can become an industrial verification product when CI and branch governance are fully enforced.
- **ZERO:** The claim that this repository is already a general GPT-level model is false.

## Official Positioning (Qualification Phase)

Current external positioning is pilot-qualified:

- A governed epistemic and meaning-ascent platform with:
  - machine-checkable core proof fragments,
  - ranked certificate gating,
  - typed residual preservation,
  - persistent audit replay,
  - adversarial validation,
  - empirical readiness scoring.

Current posture is **not production-certified** and **not full-theory proof completion**.
