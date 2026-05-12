"""Serializers for the CFK module."""
from __future__ import annotations

import json
from mcd.cfk.cfk_pipeline import CognitiveFractalResult
from mcd.cfk.cfk_schema import CognitiveFractalUnit, KernelProjection
from mcd.cfk.proof_object import ProofObject
from mcd.core.public_judgment import collapse_to_public_judgment


def _normalize_public_judgments(obj):
    if isinstance(obj, dict):
        normalized = {}
        for k, v in obj.items():
            if k in {"judgment", "kernel_judgment", "final_judgment", "proof_status"} and isinstance(v, str):
                normalized[k] = collapse_to_public_judgment(v)
            else:
                normalized[k] = _normalize_public_judgments(v)
        return normalized
    if isinstance(obj, list):
        return [_normalize_public_judgments(v) for v in obj]
    return obj


def cfk_result_to_json(result: CognitiveFractalResult) -> str:
    return json.dumps(_normalize_public_judgments(result.to_dict()), ensure_ascii=False, indent=2)


def proof_to_json(proof: ProofObject) -> str:
    return json.dumps(_normalize_public_judgments(proof.to_dict()), ensure_ascii=False, indent=2)


def unit_to_json(unit: CognitiveFractalUnit) -> str:
    return json.dumps(_normalize_public_judgments(unit.to_dict()), ensure_ascii=False, indent=2)


def projection_to_json(proj: KernelProjection) -> str:
    return json.dumps(_normalize_public_judgments(proj.to_dict()), ensure_ascii=False, indent=2)
