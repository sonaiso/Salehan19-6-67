"""Serializers — serialize GroundedReasoningFrame to JSON-compatible dict."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from mcd.grounding.grounded_frame import GroundedReasoningFrame


def _serialize(obj: Any) -> Any:
    """Recursively serialize dataclasses, Enums, and standard types."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def grounded_frame_to_dict(frame: GroundedReasoningFrame) -> dict:
    """Convert a GroundedReasoningFrame to a JSON-compatible dictionary."""
    return _serialize(frame)


def grounded_frame_to_json(frame: GroundedReasoningFrame, indent: int = 2) -> str:
    """Convert a GroundedReasoningFrame to a JSON string."""
    return json.dumps(grounded_frame_to_dict(frame), ensure_ascii=False, indent=indent)
