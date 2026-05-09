# GPT-5.5 Simulation Benchmark

## Purpose

This document defines the methodology for comparing the MCD/NERL/FPCL/GLCFL system against GPT-5.5 (and similar large language models). The goal is **not** to determine who writes better text. The goal is to measure whether this project adds a **controllable epistemic layer** above LLMs.

**Key distinction:** GPT-5.5 is a language model. This project is an epistemic discipline layer that can run **on top of** any LLM.

---

## What We Are Measuring

We are NOT measuring:
- Language generation quality
- Fluency or readability
- General knowledge accuracy

We ARE measuring:
- Whether prompts are correctly classified by domain (epistemic/shari/value/technical/practical)
- Whether certainty is assigned correctly (not too high, not too low)
- Whether judgment is suspended when evidence is insufficient
- Whether shari and epistemic domains are kept separate (harm ≠ haram)
- Whether output is structured and machine-readable

---

## 10 Comparison Dimensions

| # | Dimension | What it Measures |
|---|-----------|-----------------|
| 1 | `prompt_understanding_structure` | Is the prompt parsed into explicit components? |
| 2 | `evidence_discipline` | Does the system require evidence before asserting? |
| 3 | `certainty_discipline` | Is certainty assigned correctly (not always high)? |
| 4 | `domain_separation` | Are shari/epistemic/value domains clearly separated? |
| 5 | `arabic_epistemic_semantics` | Are Arabic epistemic terms handled correctly? |
| 6 | `structured_output` | Is output always JSON-serializable and machine-readable? |
| 7 | `hallucination_resistance` | Is false certainty avoided when evidence is lacking? |
| 8 | `tool_layer_compatibility` | Can output be used as structured input to downstream tools? |
| 9 | `latency` | Is processing fast enough for real-time use? |
| 10 | `developer_controllability` | Can rules be modified without retraining? |

---

## Expected Behavior of Each System

| Dimension | GPT-5.5 | MCD/NERL/FPCL |
|-----------|---------|----------------|
| Prompt Understanding Structure | Implicit — model decides internally | Explicit — PromptFrame JSON with judgment_types, evidence_needs, etc. |
| Evidence Discipline | Variable — may assert without evidence | Enforced — evidence_needs always populated |
| Certainty Discipline | Variable — often overconfident | Enforced — certainty_policy chosen from calibrated set |
| Domain Separation | Implicit — blends shari and epistemic | Explicit — judgment_types separates shari from epistemic |
| Arabic Epistemic Semantics | General — trained on generic Arabic | Nabhani-grounded — domain judge applies Islamic epistemic logic |
| Structured Output | Possible — requires prompt engineering | Always — JSON output by default |
| Hallucination Resistance | Model-dependent | Deterministic — suspends when certainty < threshold |
| Tool Layer Compatibility | Low — output is text | High — output is typed dict |
| Latency | API round-trip (100ms–2s) | Local, deterministic (target: <200ms) |
| Developer Controllability | API parameters only | Full rule control — modify classifiers without retraining |

---

## Benchmark Methodology

### Step 1: Select Examples

Use the 10 benchmark examples from `src/mcd/evaluation/benchmark_dataset.py`. These represent the key epistemic distinctions the system must handle:

- BM-01: Empirical physical claim (النار تحرق)
- BM-02: Deeply ambiguous single word (علم)
- BM-03: Linguistic definition request (ما معنى علم؟)
- BM-04: Harm question — epistemic (هل الكذب ضار؟)
- BM-05: Shari judgment — haram (هل الكذب حرام؟)
- BM-06: Technical construction question (كيف نبني API؟)
- BM-07: Complex system design
- BM-08: Analogy without illah
- BM-09: Civilization vs. civility distinction
- BM-10: Social epistemic claim

### Step 2: Run Through MCD Pipeline

```bash
python -m mcd.cli benchmark-simulation --output json
```

This runs all 10 examples through FPCL and scores them against expected behavior.

### Step 3: Collect GPT-5.5 Outputs (Future Work)

For each example, collect GPT-5.5's raw output. Fill the `gpt55_output` field in `BaselineExample` (see `gpt55_baseline_schema.py`). Do **not** make API calls automatically — this must be done manually or via a separate human evaluation script.

### Step 4: Score Both Systems

For each dimension, assign a score (0.0–1.0) to both systems. Compute:
- `delta = mcd_score - gpt55_score`
- `winner_by_dimension` — which system performs better per dimension

### Step 5: Report Results

The comparison is honest: some dimensions favor GPT-5.5 (e.g., fluency), others favor MCD (e.g., structured output, certainty discipline).

---

## Important Notes

1. **No API calls are made automatically.** The `gpt55_baseline_schema.py` only defines the schema for future comparison. No credentials are required.

2. **This is not a competition.** MCD is designed to wrap LLMs, not replace them. A production system might use both together.

3. **The shari/epistemic separation test (BM-05) is the most important.** GPT-5.5 tends to conflate "is X haram?" with "is X harmful?" — which is an epistemic error. MCD must correctly identify BM-05 as requiring shari evidence and suspend judgment.

4. **Results should be interpreted by humans.** Automated scoring is approximate. Human evaluation on the 10 examples is required for accurate comparison.

---

## Schema Reference

```python
from mcd.evaluation.gpt55_baseline_schema import (
    build_comparison_schema,
    empty_dimension_scores,
    COMPARISON_DIMENSIONS,
)

examples = build_comparison_schema()
scores = empty_dimension_scores()  # {dim: None for all dimensions}
```

Fill `gpt55_output` in each `BaselineExample` and add scores manually after evaluation.
