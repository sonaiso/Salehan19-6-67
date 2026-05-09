"""V1 versioned API routes — /v1/* prefix.

Phase 6.1: All routes are mounted under /v1/.
Legacy unversioned routes remain as aliases (backward-compatible).

New in Phase 6.1:
  GET  /v1/health
  GET  /v1/version
  POST /v1/classify
  POST /v1/curriculum/evaluate
  POST /v1/curriculum/quality-lock
  POST /v1/industrial/test
  POST /v1/pre-api/qualification
  POST /v1/reasoning/evaluate
  GET  /v1/pilot/readiness         ← new
"""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from mcd.api.errors import (
    EngineExecutionError,
    InvalidInputError,
    SchemaSerializationError,
    UnsupportedProfileError,
)
from mcd.api.schemas import (
    APIResponse,
    ClassifyRequest,
    ProfileRequest,
    ReasoningEvaluateRequest,
)
from mcd.api.serializers import safe_serialize
from mcd.api.version import API_VERSION, LAYERS, SERVICE_NAME

v1_router = APIRouter(prefix="/v1")

# ---------------------------------------------------------------------------
# Supported curriculum / industrial profiles
# ---------------------------------------------------------------------------
_CURRICULUM_PROFILES = {
    "full_curriculum",
    "full_curriculum_extended",
    "industrial_curriculum",
    "basic_reality",
    "relational_reasoning",
    "evidence_certainty",
    "mixed_reasoning",
    "adversarial",
}
_INDUSTRIAL_PROFILES = {"quick", "full"}

# Production blockers (always present in this phase)
_PRODUCTION_BLOCKERS = [
    "No authentication implemented",
    "No rate limiting implemented",
    "No persistent logging",
    "No external source adapters (MockSourceAPI only)",
    "No production deployment configuration",
    "No load testing under real traffic",
    "No security audit completed",
    "API versioning via URL path added in Phase 6.1 but not validated in production",
]


# ---------------------------------------------------------------------------
# GET /v1/health
# ---------------------------------------------------------------------------


@v1_router.get("/health", tags=["v1", "health"])
def v1_health() -> dict:
    """Liveness check — always returns ok."""
    return {"status": "ok", "service": SERVICE_NAME, "version": "v1"}


# ---------------------------------------------------------------------------
# GET /v1/version
# ---------------------------------------------------------------------------


@v1_router.get("/version", tags=["v1", "meta"])
def v1_version() -> dict:
    """Return API version and active layers."""
    return {
        "version": API_VERSION,
        "api_version": "v1",
        "service": SERVICE_NAME,
        "layers": LAYERS,
    }


# ---------------------------------------------------------------------------
# POST /v1/classify
# ---------------------------------------------------------------------------


@v1_router.post("/classify", response_model=APIResponse, tags=["v1", "classification"])
def v1_classify(req: ClassifyRequest) -> dict:
    """Run FPCL classification on Arabic text."""
    start = time.monotonic()
    if not req.text.strip():
        raise InvalidInputError("text must not be blank")

    try:
        from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
        fpc = FractalPromptClassifier()
        frame = fpc.classify(req.text, include_debug=req.include_debug)
        raw = frame.to_dict()
    except Exception as exc:
        raise EngineExecutionError("FractalPromptClassifier", str(exc)) from exc

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=list(frame.warnings),
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /v1/curriculum/evaluate
# ---------------------------------------------------------------------------


@v1_router.post("/curriculum/evaluate", response_model=APIResponse, tags=["v1", "curriculum"])
def v1_curriculum_evaluate(req: ProfileRequest) -> dict:
    """Run curriculum evaluator on the given profile."""
    start = time.monotonic()
    profile_name = req.profile or "full_curriculum"
    if profile_name not in _CURRICULUM_PROFILES:
        raise UnsupportedProfileError(profile_name)

    try:
        from mcd.curriculum.curriculum_dataset import CurriculumDataset
        from mcd.curriculum.curriculum_evaluator import CurriculumEvaluator
        from mcd.curriculum.learning_profiles import get_profile

        profile = get_profile(profile_name)
        units = CurriculumDataset().load_levels(profile.levels)
        eval_report = CurriculumEvaluator().evaluate(units)
        raw = eval_report.to_dict()
    except UnsupportedProfileError:
        raise
    except Exception as exc:
        raise EngineExecutionError("CurriculumEvaluator", str(exc)) from exc

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=[],
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /v1/curriculum/quality-lock
# ---------------------------------------------------------------------------


@v1_router.post("/curriculum/quality-lock", response_model=APIResponse, tags=["v1", "curriculum"])
def v1_curriculum_quality_lock() -> dict:
    """Return the current curriculum quality lock status."""
    start = time.monotonic()
    try:
        from mcd.curriculum.quality_lock import run_quality_lock
        report = run_quality_lock()
        raw = report.to_dict()
    except Exception as exc:
        raise EngineExecutionError("QualityLock", str(exc)) from exc

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    warnings: list[str] = []
    if not report.is_locked():
        warnings = [f"Quality lock blocked: {b}" for b in report.blockers]

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=warnings,
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /v1/industrial/test
# ---------------------------------------------------------------------------


@v1_router.post("/industrial/test", response_model=APIResponse, tags=["v1", "industrial"])
def v1_industrial_test(req: ProfileRequest) -> dict:
    """Run the industrial test suite on the given profile."""
    start = time.monotonic()
    profile_name = req.profile or "quick"
    if profile_name not in _INDUSTRIAL_PROFILES:
        raise UnsupportedProfileError(profile_name)

    try:
        from mcd.industrial.industrial_test_runner import IndustrialTestRunner
        from mcd.industrial.industrial_test_case import get_default_test_cases
        from mcd.industrial.serializers import industrial_result_to_dict

        cases = get_default_test_cases()
        if profile_name == "quick":
            cases = cases[:10]

        runner = IndustrialTestRunner()
        results = runner.run_all(cases)
        summary = runner.summary(results)

        raw = {
            "profile": profile_name,
            "summary": summary,
            "results": [industrial_result_to_dict(r) for r in results],
        }
    except UnsupportedProfileError:
        raise
    except Exception as exc:
        raise EngineExecutionError("IndustrialTestRunner", str(exc)) from exc

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=[],
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /v1/pre-api/qualification
# ---------------------------------------------------------------------------


@v1_router.post("/pre-api/qualification", response_model=APIResponse, tags=["v1", "qualification"])
def v1_pre_api_qualification() -> dict:
    """Return the pre-API qualification gate result."""
    start = time.monotonic()
    try:
        from mcd.industrial.pre_api_qualification import PreAPIQualificationGate
        gate = PreAPIQualificationGate()
        report = gate.evaluate(tests_pass=True)
        raw = report.to_dict()
    except Exception as exc:
        raise EngineExecutionError("PreAPIQualificationGate", str(exc)) from exc

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    warnings: list[str] = []
    if report.status == "blocked_before_api":
        warnings = list(report.blockers)

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=warnings,
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /v1/reasoning/evaluate
# ---------------------------------------------------------------------------


@v1_router.post("/reasoning/evaluate", response_model=APIResponse, tags=["v1", "reasoning"])
def v1_reasoning_evaluate(req: ReasoningEvaluateRequest) -> dict:
    """Full reasoning evaluation: classification + evidence need + certainty policy + warnings."""
    start = time.monotonic()
    if not req.text.strip():
        raise InvalidInputError("text must not be blank")

    try:
        from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
        fpc = FractalPromptClassifier()
        frame = fpc.classify(req.text, include_debug=req.include_debug)
    except Exception as exc:
        raise EngineExecutionError("FractalPromptClassifier", str(exc)) from exc

    raw = {
        "classification": {
            "intent": frame.intent,
            "judgment_types": frame.judgment_types,
            "routing_engine": frame.routing_engine,
            "sub_engines": list(frame.sub_engines),
        },
        "evidence_need": frame.evidence_needs,
        "certainty_policy": frame.certainty_policy,
        "certainty_reason": frame.certainty_reason,
        "warnings": list(frame.warnings),
    }
    if req.include_debug:
        raw["reasoning_frame"] = frame.to_dict()

    try:
        data = safe_serialize(raw)
    except Exception as exc:
        raise SchemaSerializationError(str(exc)) from exc

    elapsed = (time.monotonic() - start) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="success",
        data=data,
        warnings=list(frame.warnings),
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# GET /v1/pilot/readiness  (new in Phase 6.1)
# ---------------------------------------------------------------------------


@v1_router.get("/pilot/readiness", tags=["v1", "pilot"])
def v1_pilot_readiness() -> dict:
    """Return pilot readiness status.

    Important:
    - production_ready is ALWAYS false in Phase 6.1.
    - tests_verified is false unless CI confirms it (cannot be hardcoded true).
    """
    # Determine quality lock status
    quality_lock_status = "unknown"
    try:
        from mcd.curriculum.quality_lock import run_quality_lock
        ql = run_quality_lock()
        quality_lock_status = "locked" if ql.is_locked() else "not_locked"
    except Exception:
        quality_lock_status = "error"

    return {
        "status": "conditional_candidate",
        "production_ready": False,
        "blockers_before_production": _PRODUCTION_BLOCKERS,
        "api_implemented": True,
        "quality_lock": quality_lock_status,
        "tests_verified": False,
        "warnings": [
            "tests_pass must be verified by CI — cannot be hardcoded true",
            "Production requires auth, rate limiting, persistent logging, and security audit",
        ],
    }
