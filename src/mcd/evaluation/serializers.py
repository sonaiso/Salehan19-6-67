"""Serializers — JSON serialization for EIRL dataclasses."""
from __future__ import annotations
import json
from dataclasses import asdict

from mcd.evaluation.repository_audit import RepositoryAuditResult
from mcd.evaluation.architecture_audit import ArchitectureAuditResult
from mcd.evaluation.test_audit import TestAuditResult
from mcd.evaluation.cli_audit import CLIAuditResult
from mcd.evaluation.code_quality_audit import CodeQualityAuditResult
from mcd.evaluation.production_readiness import ProductionReadinessReport
from mcd.evaluation.evaluation_runner import EvaluationReport


def _to_json(obj) -> str:
    return json.dumps(asdict(obj), ensure_ascii=False, indent=2)


def repo_audit_to_json(result: RepositoryAuditResult) -> str:
    return _to_json(result)


def arch_audit_to_json(result: ArchitectureAuditResult) -> str:
    return _to_json(result)


def test_audit_to_json(result: TestAuditResult) -> str:
    return _to_json(result)


def cli_audit_to_json(result: CLIAuditResult) -> str:
    return _to_json(result)


def code_quality_to_json(result: CodeQualityAuditResult) -> str:
    return _to_json(result)


def readiness_to_json(report: ProductionReadinessReport) -> str:
    return _to_json(report)


def eval_report_to_json(report: EvaluationReport) -> str:
    return _to_json(report)
