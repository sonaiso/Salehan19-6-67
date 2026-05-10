# data/mabni/ — Arabic Mabni Logical-Pragmatic Layer Data

This directory contains data files for Phase 7.4 of the MCD project.

## Files

| File | Description | Format |
|------|-------------|--------|
| `mabni_registry_ar.json` | Master registry of all Mabni operators | JSON |
| `ma_usage_examples_ar.jsonl` | Usage examples for ما | JSONL |
| `man_usage_examples_ar.jsonl` | Usage examples for من | JSONL |
| `in_usage_examples_ar.jsonl` | Usage examples for إن/إنّ/إنما | JSONL |
| `la_usage_examples_ar.jsonl` | Usage examples for لا | JSONL |
| `preposition_senses_ar.jsonl` | Preposition sense examples | JSONL |
| `conditional_examples_ar.jsonl` | Conditional structure examples | JSONL |
| `counterfactual_examples_ar.jsonl` | Counterfactual structure examples | JSONL |
| `attached_pronoun_examples_ar.jsonl` | Attached pronoun examples | JSONL |
| `answer_particle_examples_ar.jsonl` | Answer particle examples | JSONL |
| `exception_restriction_examples_ar.jsonl` | Exception structure examples | JSONL |
| `qasr_examples_ar.jsonl` | Qasr (restriction) examples | JSONL |
| `emphasis_vs_evidence_examples_ar.jsonl` | Emphasis vs evidence contrast | JSONL |
| `mabni_golden_examples_ar.jsonl` | Golden test examples | JSONL |
| `mabni_adversarial_examples_ar.jsonl` | Adversarial/challenging examples | JSONL |

## Key Invariants

- `creates_evidence` is ALWAYS `false` for all Mabni operators
- Emphasis increases discourse force only, NOT evidential weight
- Conditionals NEVER assert the protasis occurred
- Questions (istifham) are NOT assertions
