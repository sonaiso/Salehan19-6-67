"""All MCD REST API route handlers.

Endpoints implemented:
  GET  /health               — liveness probe
  GET  /version              — version info + layers
  POST /classify             — FPCL prompt classification
  POST /curriculum/evaluate  — curriculum evaluation on profile
  POST /curriculum/quality-lock  — quality lock status
  POST /industrial/test      — industrial test profile
  POST /pre-api/qualification — pre-API qualification gate
  POST /reasoning/evaluate   — full reasoning evaluation

Constraints (Phase 6):
  - No LLM calls
  - No external network calls
  - No GraphRAG
  - Responses always include request_id + execution_time_ms
  - Errors are JSON-structured (no stack traces)
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

router = APIRouter()

# ---------------------------------------------------------------------------
# Supported curriculum / industrial profiles
# ---------------------------------------------------------------------------
_CURRICULUM_PROFILES = {
    "full_curriculum",
    "quick",
    "full_curriculum_extended",
    "industrial_curriculum",
}
_INDUSTRIAL_PROFILES = {"quick", "full"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(data: dict, warnings: list[str] | None = None, start: float | None = None) -> dict:
    """Build a standard APIResponse dict."""
    elapsed = (time.monotonic() - (start or time.monotonic())) * 1000
    return APIResponse(
        request_id=str(uuid.uuid4()),
        status="ok",
        data=data,
        warnings=warnings or [],
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


@router.get("/version", tags=["meta"])
def get_version() -> dict:
    """Return API version and active layers."""
    return {"version": API_VERSION, "service": SERVICE_NAME, "layers": LAYERS}


# ---------------------------------------------------------------------------
# POST /classify
# ---------------------------------------------------------------------------


@router.post("/classify", response_model=APIResponse, tags=["classification"])
def classify(req: ClassifyRequest) -> dict:
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
        status="ok",
        data=data,
        warnings=list(frame.warnings),
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /curriculum/evaluate
# ---------------------------------------------------------------------------


@router.post("/curriculum/evaluate", response_model=APIResponse, tags=["curriculum"])
def curriculum_evaluate(req: ProfileRequest) -> dict:
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
        status="ok",
        data=data,
        warnings=[],
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /curriculum/quality-lock
# ---------------------------------------------------------------------------


@router.post("/curriculum/quality-lock", response_model=APIResponse, tags=["curriculum"])
def curriculum_quality_lock() -> dict:
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
        status="ok",
        data=data,
        warnings=warnings,
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /industrial/test
# ---------------------------------------------------------------------------


@router.post("/industrial/test", response_model=APIResponse, tags=["industrial"])
def industrial_test(req: ProfileRequest) -> dict:
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
        status="ok",
        data=data,
        warnings=[],
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /pre-api/qualification
# ---------------------------------------------------------------------------


@router.post("/pre-api/qualification", response_model=APIResponse, tags=["qualification"])
def pre_api_qualification() -> dict:
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
        status="ok",
        data=data,
        warnings=warnings,
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /reasoning/evaluate
# ---------------------------------------------------------------------------


@router.post("/reasoning/evaluate", response_model=APIResponse, tags=["reasoning"])
def reasoning_evaluate(req: ReasoningEvaluateRequest) -> dict:
    """Full reasoning evaluation: classification + evidence need + certainty policy + warnings."""
    start = time.monotonic()
    if not req.text.strip():
        raise InvalidInputError("text must not be blank")

    # Run FPCL classification
    try:
        from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
        fpc = FractalPromptClassifier()
        frame = fpc.classify(req.text, include_debug=req.include_debug)
    except Exception as exc:
        raise EngineExecutionError("FractalPromptClassifier", str(exc)) from exc

    # Build structured reasoning result
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
        status="ok",
        data=data,
        warnings=list(frame.warnings),
        errors=[],
        execution_time_ms=round(elapsed, 3),
    ).model_dump()
