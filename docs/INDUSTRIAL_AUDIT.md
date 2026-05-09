# Industrial Audit — EIRL (Evaluation & Industrial Readiness Layer)

## What is EIRL?

The **Evaluation & Industrial Readiness Layer (EIRL)** is the fifth layer of the MCD (Minimal Cognitive Decoder) project. Its purpose is to measure, report, and track the industrial readiness of the entire system — from repository structure to production deployment readiness.

EIRL does **not** add new features to the epistemic reasoning pipeline. Instead, it provides:

- **Repository Audits** — inspect the structure of `src/mcd/`, `tests/`, `docs/`
- **Architecture Audits** — check layer separation, modularity, dependency risks
- **Test Audits** — measure test suite distribution across all layers
- **CLI Audits** — detect which CLI commands exist and whether they smoke-test clean
- **Code Quality Audits** — detect long files, long functions, print() in src, TODOs
- **Production Readiness Scorecard** — 10-dimension scored assessment
- **KPI Dashboard** — 20 measurable industrial performance indicators
- **Benchmark Dataset** — 10 curated Arabic examples for evaluating the classifier
- **Report Builder** — generates structured Markdown audit reports
- **Evaluation Runner** — scores benchmark examples against FPCL classifier output

---

## How to Run

### Full Project Audit (Markdown)

```bash
python -m mcd.cli evaluate-project --output markdown
```

### Full Project Audit (JSON)

```bash
python -m mcd.cli evaluate-project --output json
```

### Benchmark Simulation

Runs all 10 benchmark examples through the FPCL classifier and scores them:

```bash
python -m mcd.cli benchmark-simulation --output json
python -m mcd.cli benchmark-simulation --output markdown
```

### Readiness Score

Returns the 10-dimension production readiness scorecard:

```bash
python -m mcd.cli readiness-score --output json
python -m mcd.cli readiness-score --output markdown
```

---

## Maturity Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| `concept` | avg < 1.5/5 | Idea only, no implementation |
| `research_prototype` | 1.5–2.4/5 | Experimental, not reliable |
| `working_prototype` | 2.5–3.4/5 | Works, not production-safe |
| `pilot_ready` | 3.5–4.4/5 | Can be used in controlled pilots |
| `production_ready` | 4.5+/5 | Deployable at scale |

The current project is at **working_prototype** level (average score: ~2.4/5).

---

## Architecture Audit Scoring

The architecture audit measures 5 dimensions (0.0–1.0 each):

| Dimension | What it Measures |
|-----------|-----------------|
| Layer Separation | Each package has `__init__.py` |
| Modularity | Each layer has >2 Python modules |
| Dependency Risk | Core does not import from higher layers |
| Deterministic Core | No LLM calls in classification layer |
| Integration | CLI exists and connects multiple layers |

**Score thresholds:**
- `>= 0.80` → strong
- `0.60–0.79` → acceptable prototype
- `0.40–0.59` → research prototype
- `< 0.40` → weak

---

## KPI Categories

The 20 KPIs are organized into 4 categories:

### A. Epistemic Quality (EQ-01 to EQ-06)
Measures how well the system applies epistemic discipline: grounding rate, evidence attachment, certainty calibration, suspension correctness, domain separation, and harm-vs-haram separation.

### B. Prompt Classification (PC-01 to PC-04)
Measures accuracy of the FPCL layer: root domain accuracy, judgment type accuracy, evidence need accuracy, certainty policy accuracy.

### C. Reasoning Quality (RQ-01 to RQ-04)
Measures reasoning integrity: false certainty rate (hallucination proxy), fake evidence detection, conflict suspension, manat applicability accuracy.

### D. Industrial (IN-01 to IN-06)
Measures engineering readiness: test pass rate, CLI success rate, average latency, error rate, JSON schema stability, regression failure rate.

---

## Running Tests for EIRL

```bash
PYTHONPATH=src python -m pytest tests/test_evaluation_*.py tests/test_cli_evaluate_project.py tests/test_cli_benchmark_simulation.py tests/test_cli_readiness_score.py -v
```
