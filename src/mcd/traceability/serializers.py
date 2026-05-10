"""Serializers for TraceBundle and sub-components."""
from __future__ import annotations

import json
from mcd.traceability.trace_builder import TraceBundle


def trace_bundle_to_dict(bundle: TraceBundle) -> dict:
    return bundle.to_dict()


def trace_bundle_to_json(bundle: TraceBundle, indent: int = 2) -> str:
    return json.dumps(trace_bundle_to_dict(bundle), ensure_ascii=False, indent=indent)
