"""Serializers for the CFK module."""
from __future__ import annotations

import json
from mcd.cfk.cfk_pipeline import CognitiveFractalResult
from mcd.cfk.cfk_schema import CognitiveFractalUnit, KernelProjection
from mcd.cfk.proof_object import ProofObject


def cfk_result_to_json(result: CognitiveFractalResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)


def proof_to_json(proof: ProofObject) -> str:
    return json.dumps(proof.to_dict(), ensure_ascii=False, indent=2)


def unit_to_json(unit: CognitiveFractalUnit) -> str:
    return json.dumps(unit.to_dict(), ensure_ascii=False, indent=2)


def projection_to_json(proj: KernelProjection) -> str:
    return json.dumps(proj.to_dict(), ensure_ascii=False, indent=2)
