"""Serializers for residual learning types — JSON roundtrip safe."""
from __future__ import annotations

import json

from .proposal_schema import GPTProposal
from .residual_schema import CognitiveResidual
from .learning_action import LearningAction
from .residual_report import ResidualReport
from .residual_calibration import ResidualCalibrationReport
from .residual_test_generator import TestSpec


def proposal_to_json(proposal: GPTProposal) -> str:
    return json.dumps(proposal.to_dict(), ensure_ascii=False, indent=2)


def residual_to_json(residual: CognitiveResidual) -> str:
    return json.dumps(residual.to_dict(), ensure_ascii=False, indent=2)


def action_to_json(action: LearningAction) -> str:
    return json.dumps(action.to_dict(), ensure_ascii=False, indent=2)


def report_to_json(report: ResidualReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def calibration_report_to_json(report: ResidualCalibrationReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def test_spec_to_json(spec: TestSpec) -> str:
    return json.dumps(spec.to_dict(), ensure_ascii=False, indent=2)


def residuals_to_jsonl(residuals: list[CognitiveResidual]) -> str:
    return "\n".join(json.dumps(r.to_dict(), ensure_ascii=False) for r in residuals)


def actions_to_jsonl(actions: list[LearningAction]) -> str:
    return "\n".join(json.dumps(a.to_dict(), ensure_ascii=False) for a in actions)


def test_specs_to_jsonl(specs: list[TestSpec]) -> str:
    return "\n".join(json.dumps(s.to_dict(), ensure_ascii=False) for s in specs)
