"""JSON serializers for FPCL data models."""
from __future__ import annotations

import json
from typing import Any

from mcd.classification.prompt_frame import PromptFrame


def prompt_frame_to_dict(frame: PromptFrame) -> dict[str, Any]:
    """Convert a PromptFrame to a serializable dictionary."""
    return frame.to_dict()


def prompt_frame_to_json(
    frame: PromptFrame,
    ensure_ascii: bool = False,
    indent: int = 2,
) -> str:
    """Convert a PromptFrame to a JSON string."""
    return json.dumps(prompt_frame_to_dict(frame), ensure_ascii=ensure_ascii, indent=indent)
