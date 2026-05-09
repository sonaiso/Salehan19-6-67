"""Serialization helpers — ensure all API data is JSON-safe.

Rules:
- No Enum leakage: convert every enum value to str.
- No dataclass leakage: convert dataclasses via to_dict() or dataclasses.asdict().
- All keys and values must be JSON-primitive or nested dict/list.
"""
from __future__ import annotations

import dataclasses
import enum
import json
from typing import Any


def _coerce(obj: Any) -> Any:
    """Recursively make ``obj`` JSON-safe."""
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, enum.Enum):
        return str(obj.value)
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        # Keys may be str-enum instances — normalize them to plain strings
        return {_key(k): _coerce(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_coerce(v) for v in obj]
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        # Use to_dict() if available, else fall back to dataclasses.asdict()
        if hasattr(obj, "to_dict"):
            return _coerce(obj.to_dict())
        return _coerce(dataclasses.asdict(obj))
    # Try __dict__ as last resort
    if hasattr(obj, "__dict__"):
        return _coerce(obj.__dict__)
    return str(obj)


def _key(k: Any) -> str:
    """Normalize a dict key to a plain string.

    For str-enum instances like ``RootDomain.HUMAN`` (which have value "human"),
    return the enum VALUE instead of the Python 3.11+ repr "RootDomain.HUMAN".
    """
    if isinstance(k, enum.Enum):
        return str(k.value)
    return str(k)


def safe_serialize(data: Any) -> dict:
    """Return a JSON-safe dict for use in APIResponse.data."""
    coerced = _coerce(data)
    if isinstance(coerced, dict):
        return coerced
    return {"result": coerced}


def to_json_string(data: Any) -> str:
    """Serialize data to a compact JSON string (for debug use)."""
    return json.dumps(_coerce(data), ensure_ascii=False, indent=2)
