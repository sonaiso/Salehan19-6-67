"""Production Readiness Scorecard — 10-dimension assessment."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ReadinessDimension:
    name: str
    score: int          # 1-5
    rationale: str
    blockers: list[str]
    next_actions: list[str]


@dataclass
class ProductionReadinessReport:
    dimensions: list[ReadinessDimension]
    average_score: float
    maturity_level: str  # concept | research_prototype | working_prototype | pilot_ready | production_ready
    top_blockers: list[str]
    next_30_days_actions: list[str]
    next_90_days_actions: list[str]

    @classmethod
    def build_default(cls) -> "ProductionReadinessReport":
        """Build a realistic default scorecard based on current project state."""
        dimensions = [
            ReadinessDimension(
                name="Architecture Maturity",
                score=3,
                rationale="Four fully implemented layers (MCD, NERL, FPCL, GLCFL) with clean separation. CLI exists. No REST API yet.",
                blockers=["No REST API", "No async support"],
                next_actions=["Design REST API schema", "Add FastAPI or Flask endpoint"],
            ),
            ReadinessDimension(
                name="Test Maturity",
                score=4,
                rationale="600+ deterministic tests across all layers. Strong unit test coverage for core classification logic.",
                blockers=["No load/stress tests", "No end-to-end integration tests"],
                next_actions=["Add integration tests", "Add benchmark latency tests"],
            ),
            ReadinessDimension(
                name="CLI Usability",
                score=3,
                rationale="decode, nabhani, classify, ground commands work. JSON output supported. No shell completion or man pages.",
                blockers=["No shell completion", "No --help localization"],
                next_actions=["Add shell completion", "Add Arabic help strings"],
            ),
            ReadinessDimension(
                name="API Readiness",
                score=1,
                rationale="No HTTP/REST API exists. Only CLI and Python library interface.",
                blockers=["No REST API", "No authentication", "No rate limiting"],
                next_actions=["Implement FastAPI REST API", "Add authentication layer"],
            ),
            ReadinessDimension(
                name="Documentation",
                score=3,
                rationale="README exists. Docs folder has architecture docs. No API reference or deployment guide.",
                blockers=["No API reference", "No deployment guide"],
                next_actions=["Generate API docs", "Write deployment guide"],
            ),
            ReadinessDimension(
                name="Observability",
                score=1,
                rationale="No logging framework configured. No metrics, tracing, or monitoring. print() used in some places.",
                blockers=["No logging", "No metrics", "No error tracking"],
                next_actions=["Add structured logging", "Add Prometheus metrics endpoint"],
            ),
            ReadinessDimension(
                name="Evaluation Dataset",
                score=2,
                rationale="Initial benchmark dataset of 10 examples built. No human annotations or calibrated gold labels yet.",
                blockers=["Small dataset", "No human validation", "No calibration study"],
                next_actions=["Expand to 100+ examples", "Run human annotation study"],
            ),
            ReadinessDimension(
                name="Mathematical Formalization",
                score=3,
                rationale="Epistemic axioms defined. Certainty scoring, domain separation, evidence grading implemented. No formal proof.",
                blockers=["No formal proof of correctness", "No uncertainty quantification"],
                next_actions=["Document formal axioms", "Add uncertainty bounds"],
            ),
            ReadinessDimension(
                name="LLM Integration Safety",
                score=2,
                rationale="Adapters exist. No LLM calls in deterministic classifiers. No guardrails or output validation for LLM results.",
                blockers=["No LLM output validation", "No injection protection"],
                next_actions=["Add LLM output schema validation", "Add injection guard"],
            ),
            ReadinessDimension(
                name="Commercial Focus",
                score=2,
                rationale="Strong promise for Arabic knowledge management and epistemic AI. No product roadmap or commercial packaging.",
                blockers=["No product packaging", "No SLA definition"],
                next_actions=["Define target use cases", "Build demo application"],
            ),
        ]

        avg = sum(d.score for d in dimensions) / len(dimensions)

        if avg >= 4.5:
            maturity = "production_ready"
        elif avg >= 3.5:
            maturity = "pilot_ready"
        elif avg >= 2.5:
            maturity = "working_prototype"
        elif avg >= 1.5:
            maturity = "research_prototype"
        else:
            maturity = "concept"

        top_blockers = [
            "No REST API — prevents external system integration",
            "No observability — cannot monitor production behavior",
            "No evaluation dataset calibration — cannot measure accuracy",
            "No LLM output guardrails — safety risk in production",
        ]

        next_30 = [
            "Implement FastAPI REST endpoint for classify and decode",
            "Add structured logging with Python logging module",
            "Expand benchmark dataset to 50 examples",
            "Add integration tests for CLI + FPCL + NERL pipeline",
        ]

        next_90 = [
            "Complete REST API with authentication",
            "Build Arabic demo application",
            "Run human annotation study on 100+ examples",
            "Add Prometheus metrics and Grafana dashboard",
            "Formal documentation of epistemic axioms",
            "Commercial pilot with Arabic education or knowledge system",
        ]

        return cls(
            dimensions=dimensions,
            average_score=round(avg, 2),
            maturity_level=maturity,
            top_blockers=top_blockers,
            next_30_days_actions=next_30,
            next_90_days_actions=next_90,
        )
