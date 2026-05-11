from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.code_claim import CodeClaim
from mcd.coding_copilot.coding_judgment import build_coding_judgment
from mcd.coding_copilot.coding_residual import CodingResidual
from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace
from mcd.coding_copilot.coding_status import CodingStatus
from mcd.coding_copilot.issue_understanding import IssueUnderstanding
from mcd.coding_copilot.patch_artifact import PatchArtifact
from mcd.coding_copilot.patch_plan import PatchPlan
from mcd.coding_copilot.repo_context import RepoContextMap
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence


def _base_parts(task_type: str = "bugfix"):
    issue = IssueUnderstanding("I-1", "fix bug", task_type=task_type)
    context = RepoContextMap("S-1", relevant_files=["src/a.py"], relevant_tests=["tests/test_a.py"])
    claim = CodeClaim("C-1", "fixes_bug", ["src/a.py"], "fix")
    plan = PatchPlan("P-1", [claim], steps=["edit"], expected_tests=["tests/test_a.py"], rollback_plan="revert")
    patch = PatchArtifact("A-1", ["src/a.py"], 2, 1, linked_claims={"src/a.py": ["C-1"]})
    trace = CodingReverseTrace(
        trace_id="T-1",
        issue_id="I-1",
        repo_snapshot_id="S-1",
        claim_ids=["C-1"],
        patch_id="A-1",
        evidence_ids=["test::pytest tests/test_a.py -q", "static::ruff", "architecture::governance"],
        test_commands=["pytest tests/test_a.py -q"],
        changed_files=["src/a.py"],
        commit_sha="abc",
        pr_number="123",
    )
    return issue, context, [claim], plan, patch, trace


def test_issue_unknown_blocks_certificate():
    issue, context, claims, plan, patch, trace = _base_parts(task_type="unknown")
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.HYPOTHESIS.value


def test_patch_without_claim_zero():
    issue, context, _claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=[],
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.ZERO.value


def test_missing_tests_hypothesis():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=None,
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.HYPOTHESIS.value


def test_failing_tests_zero():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", False, ["assert x"]),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.ZERO.value


def test_architecture_violation_zero():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], ["violation"], False),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.ZERO.value


def test_static_pass_alone_not_certificate():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=None,
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment != CodingStatus.CERTIFICATE.value


def test_certificate_requires_tests_architecture_and_reverse_trace():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[],
    )
    assert result.final_judgment == CodingStatus.CERTIFICATE.value


def test_copilot_summary_is_not_proof():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[CodingResidual("summary_as_proof", "fatal", "summary used as proof")],
    )
    assert result.final_judgment == CodingStatus.ZERO.value


def test_ci_pending_hypothesis():
    issue, context, claims, plan, patch, trace = _base_parts()
    result = build_coding_judgment(
        issue=issue,
        repo_context=context,
        claims=claims,
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=[CodingResidual("ci_pending", "blocking", "checks pending")],
    )
    assert result.final_judgment == CodingStatus.HYPOTHESIS.value
