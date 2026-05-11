from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.coding_copilot_kernel import CodingCopilotKernel
from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence


def test_kernel_methods_end_to_end():
    kernel = CodingCopilotKernel()
    issue = kernel.understand_issue("fix bug in parser", issue_id="I-1")
    context = kernel.build_repo_context(
        repo_snapshot_id="S-1",
        relevant_files=["src/a.py"],
        relevant_tests=["tests/test_a.py"],
        architecture_rules=["no_silent_level_skip"],
    )
    claim = kernel.create_code_claim(
        claim_id="C-1",
        claim_type="fixes_bug",
        affected_files=["src/a.py"],
        expected_effect="fix parser",
    )
    plan = kernel.create_patch_plan(
        plan_id="P-1",
        claims=[claim],
        steps=["edit parser"],
        expected_tests=["tests/test_a.py"],
        rollback_plan="revert",
        task_type=issue.task_type,
    )
    patch, residuals = kernel.evaluate_patch(
        patch_id="A-1",
        changed_files=["src/a.py"],
        additions=3,
        deletions=1,
        touched_layers=["parser"],
        declared_reason="fix null branch",
        linked_claims={"src/a.py": ["C-1"]},
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
    )
    trace = CodingReverseTrace(
        trace_id="T-1",
        issue_id=issue.issue_id,
        repo_snapshot_id=context.repo_snapshot_id,
        claim_ids=["C-1"],
        patch_id="A-1",
        evidence_ids=["test::pytest tests/test_a.py -q", "static::ruff", "architecture::governance"],
        test_commands=["pytest tests/test_a.py -q"],
        changed_files=["src/a.py"],
        commit_sha="abc",
        pr_number="100",
    )
    judgment = kernel.decide(
        issue=issue,
        repo_context=context,
        claims=[claim],
        patch_plan=plan,
        patch_artifact=patch,
        test_evidence=TestEvidence("pytest tests/test_a.py -q", True, []),
        static_evidence=StaticEvidence("ruff", True, []),
        architecture_evidence=ArchitectureEvidence(["r1"], [], True),
        reverse_trace=trace,
        residuals=residuals,
    )
    report = kernel.produce_report(judgment)
    assert report["final_judgment"] in {"zero", "hypothesis", "certificate"}
