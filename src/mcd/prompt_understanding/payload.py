"""Minimal governed Arabic prompt-understanding payload layer."""
from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO
from mcd.core.residual_taxonomy import has_blocking_residuals

PROMPT_UNDERSTANDING_SCHEMA_VERSION = "1.0.0"
PROMPT_UNDERSTANDING_CONTRACT_VERSION = "1.0.0"
_SUPPORTED_SCHEMA_VERSIONS = frozenset({PROMPT_UNDERSTANDING_SCHEMA_VERSION})
_SUPPORTED_RANKS = frozenset({JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE})
_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")

_TASK_CUE_MAP: tuple[tuple[str, str, str], ...] = (
    ("اكتب برومبت", "prompt_generation", "prompt_authoring"),
    ("ما الخطوة التالية", "next_step", "next_step_request"),
    ("اشرح", "explanation", "explain_request"),
    ("حلل", "analysis", "analysis_request"),
    ("راجع", "review", "review_request"),
    ("اكمل", "continuation", "continuation_request"),
)

_PROMPT_KEYS = frozenset(
    {
        "prompt_understanding_schema_version",
        "prompt_understanding_contract_version",
        "raw_prompt",
        "normalized_prompt",
        "understanding_rank",
        "inferred_intent",
        "task_type",
        "residuals",
    }
)


def build_prompt_understanding_payload(prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = dict(context or {})
    raw_prompt = str(prompt or "")
    normalized_prompt = _normalize_prompt(raw_prompt)
    segmentation = _segment_prompt(raw_prompt)
    linguistic_units = [item["text"] for item in segmentation if item["text"]]
    trace_anchors = _trace_anchors(raw_prompt)
    task_type, inferred_intent = _infer_task_and_intent(normalized_prompt)
    discourse_force = _infer_discourse_force(normalized_prompt, task_type=task_type)
    domain = str(ctx.get("domain", "general")).strip() or "general"
    constraints = list(ctx.get("constraints", [])) if isinstance(ctx.get("constraints"), list) else []
    activated_modules = ["prompt_understanding_heuristics"]
    if bool(ctx.get("enable_usul_inference", False)):
        activated_modules.append("usul_inference")

    payload: dict[str, Any] = {
        "prompt_understanding_schema_version": PROMPT_UNDERSTANDING_SCHEMA_VERSION,
        "prompt_understanding_contract_version": PROMPT_UNDERSTANDING_CONTRACT_VERSION,
        "raw_prompt": raw_prompt,
        "normalized_prompt": normalized_prompt,
        "language": "Arabic" if _is_mostly_arabic(raw_prompt) else "mixed_or_non_arabic",
        "vocalization_status": _vocalization_status(raw_prompt),
        "segmentation_trace": segmentation,
        "linguistic_units": linguistic_units,
        "semantic_nodes": [{"node": token, "kind": "lexical"} for token in linguistic_units],
        "nisbah_graph": [],
        "ifadah_units": [normalized_prompt] if normalized_prompt else [],
        "discourse_force": discourse_force,
        "inferred_intent": inferred_intent,
        "task_type": task_type,
        "domain": domain,
        "constraints": constraints,
        "activated_modules": activated_modules,
        "answer_plan": _answer_plan(task_type=task_type, intent=inferred_intent),
        "reverse_trace": {"anchors": trace_anchors},
        "residuals": [],
        "understanding_rank": JUDGMENT_HYPOTHESIS,
    }
    return enforce_prompt_understanding_contract(payload)


def validate_prompt_understanding_payload(payload: dict[str, Any]) -> list[str]:
    residuals: list[str] = _normalize_residuals(payload.get("residuals"))
    schema_version = str(payload.get("prompt_understanding_schema_version", "")).strip()
    if not schema_version:
        residuals.append("missing_prompt_understanding_schema_version")
    elif schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
        residuals.append("unsupported_prompt_understanding_schema_version")

    if not _field_text(payload.get("raw_prompt")):
        residuals.append("prompt_missing_raw_text")
    if not _field_text(payload.get("normalized_prompt")):
        residuals.append("prompt_understanding_payload_invalid")

    if not _has_trace_anchors(payload):
        residuals.append("prompt_missing_trace_anchors")
    if not _field_text(payload.get("inferred_intent")):
        residuals.append("prompt_intent_ambiguous")
    if not _field_text(payload.get("task_type")):
        residuals.append("prompt_task_type_missing")

    if _field_text(payload.get("domain")).lower() in {"", "general", "unknown"}:
        residuals.append("prompt_domain_ambiguous")
    return list(dict.fromkeys(residuals))


def enforce_prompt_understanding_contract(payload: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(payload)
    out.setdefault("prompt_understanding_schema_version", PROMPT_UNDERSTANDING_SCHEMA_VERSION)
    out.setdefault("prompt_understanding_contract_version", PROMPT_UNDERSTANDING_CONTRACT_VERSION)
    out["residuals"] = validate_prompt_understanding_payload(out)
    out["understanding_rank"] = _enforce_rank(out)
    return out


def serialize_prompt_understanding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_prompt_understanding_payload(payload):
        return deepcopy(payload)
    enforced = enforce_prompt_understanding_contract(payload)
    return json.loads(json.dumps(enforced, ensure_ascii=False, sort_keys=True))


def deserialize_prompt_understanding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_prompt_understanding_payload(payload):
        return deepcopy(payload)
    input_rank = _normalize_rank(payload.get("understanding_rank"))
    enforced = enforce_prompt_understanding_contract(payload)
    output_rank = _normalize_rank(enforced.get("understanding_rank"))
    if input_rank in {JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS} and output_rank == JUDGMENT_CERTIFICATE:
        enforced["understanding_rank"] = input_rank
    return enforced


def _normalize_prompt(raw_prompt: str) -> str:
    return " ".join(str(raw_prompt).split()).strip()


def _segment_prompt(raw_prompt: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for match in re.finditer(r"\S+", raw_prompt):
        segments.append({"text": match.group(0), "start": match.start(), "end": match.end()})
    return segments


def _trace_anchors(raw_prompt: str) -> list[dict[str, Any]]:
    if not raw_prompt.strip():
        return []
    return [{"start": 0, "end": len(raw_prompt), "text": raw_prompt, "label": "raw_prompt"}]


def _is_mostly_arabic(text: str) -> bool:
    stripped = re.sub(r"\s+", "", text or "")
    if not stripped:
        return True
    arabic_count = len(_ARABIC_RE.findall(stripped))
    return (arabic_count / max(len(stripped), 1)) >= 0.6


def _vocalization_status(text: str) -> str:
    if not text.strip():
        return "empty"
    letters = len(_ARABIC_RE.findall(text))
    if letters == 0:
        return "non_arabic"
    marks = len(_DIACRITICS_RE.findall(text))
    if marks == 0:
        return "unvocalized"
    if marks >= max(1, letters // 2):
        return "fully_vocalized"
    return "partially_vocalized"


def _infer_task_and_intent(prompt: str) -> tuple[str | None, str | None]:
    normalized = prompt.strip()
    if not normalized:
        return None, None
    for cue, task_type, intent in _TASK_CUE_MAP:
        if cue in normalized:
            return task_type, intent
    if normalized.endswith("؟") or normalized.startswith(("ما ", "ماذا ", "هل ")):
        return "question_answering", "question_request"
    return None, None


def _infer_discourse_force(prompt: str, *, task_type: str | None) -> str:
    if not prompt:
        return "unknown"
    if task_type == "continuation":
        return "continuation"
    if prompt.endswith("؟") or prompt.startswith(("ما ", "ماذا ", "هل ")):
        return "question"
    if task_type:
        return "request"
    return "unknown"


def _answer_plan(*, task_type: str | None, intent: str | None) -> list[str]:
    if not task_type:
        return []
    return [
        f"identify_intent:{intent or 'unknown'}",
        f"classify_task:{task_type}",
        "compose_governed_answer",
    ]


def _normalize_residuals(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [code for item in raw if (code := str(item).strip())]


def _normalize_rank(raw_rank: Any) -> str:
    rank = str(raw_rank or "").strip().lower()
    if rank in _SUPPORTED_RANKS:
        return rank
    return JUDGMENT_ZERO


def _enforce_rank(payload: dict[str, Any]) -> str:
    current = _normalize_rank(payload.get("understanding_rank"))
    residuals = _normalize_residuals(payload.get("residuals"))
    if has_blocking_residuals(residuals):
        return JUDGMENT_ZERO if "prompt_missing_raw_text" in residuals else JUDGMENT_HYPOTHESIS
    if "prompt_intent_ambiguous" in residuals or "prompt_domain_ambiguous" in residuals:
        return JUDGMENT_HYPOTHESIS
    if not _certificate_gates_pass(payload):
        return JUDGMENT_HYPOTHESIS
    if current in {JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE}:
        return JUDGMENT_CERTIFICATE
    return JUDGMENT_HYPOTHESIS


def _certificate_gates_pass(payload: dict[str, Any]) -> bool:
    if not _field_text(payload.get("raw_prompt")):
        return False
    if not _field_text(payload.get("normalized_prompt")):
        return False
    if not _has_trace_anchors(payload):
        return False
    if not _field_text(payload.get("inferred_intent")):
        return False
    if not _field_text(payload.get("task_type")):
        return False
    if has_blocking_residuals(_normalize_residuals(payload.get("residuals"))):
        return False
    schema_version = str(payload.get("prompt_understanding_schema_version", "")).strip()
    return schema_version in _SUPPORTED_SCHEMA_VERSIONS


def _has_trace_anchors(payload: dict[str, Any]) -> bool:
    reverse_trace = payload.get("reverse_trace")
    if not isinstance(reverse_trace, dict):
        return False
    anchors = reverse_trace.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        return False
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        start = anchor.get("start")
        end = anchor.get("end")
        text = str(anchor.get("text", "")).strip()
        if isinstance(start, int) and isinstance(end, int) and end > start and text:
            return True
    return False


def _is_prompt_understanding_payload(payload: dict[str, Any]) -> bool:
    return bool(set(payload.keys()) & _PROMPT_KEYS)


def _field_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
