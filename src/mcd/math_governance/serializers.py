from __future__ import annotations

import json
from typing import Any


def to_json(data: Any, *, indent: int = 2) -> str:
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    return json.dumps(data, ensure_ascii=False, indent=indent)
