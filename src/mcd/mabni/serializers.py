"""Serializers for Mabni analysis results."""
from __future__ import annotations

import json
from typing import Any


def to_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """Serialize data to JSON string."""
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)


def from_json(json_str: str) -> Any:
    """Deserialize JSON string to Python object."""
    return json.loads(json_str)


def to_jsonl(records: list[Any]) -> str:
    """Serialize a list of records to JSONL (one JSON per line)."""
    lines: list[str] = []
    for record in records:
        if hasattr(record, "to_dict"):
            record = record.to_dict()
        lines.append(json.dumps(record, ensure_ascii=False))
    return "\n".join(lines)


def flatten_result(result: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten a nested dict for tabular output."""
    flat: dict[str, Any] = {}
    for key, value in result.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_result(value, prefix=full_key))
        elif isinstance(value, list):
            flat[full_key] = json.dumps(value, ensure_ascii=False)
        else:
            flat[full_key] = value
    return flat


def result_to_tsv(result: dict[str, Any]) -> str:
    """Convert a flattened result to TSV format."""
    flat = flatten_result(result)
    header = "\t".join(flat.keys())
    row = "\t".join(str(v) for v in flat.values())
    return f"{header}\n{row}"
