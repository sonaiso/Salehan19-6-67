from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace


def test_reverse_trace_completeness():
    trace = CodingReverseTrace(
        trace_id="T-1",
        issue_id="I-1",
        repo_snapshot_id="S-1",
        claim_ids=["C-1"],
        patch_id="P-1",
        evidence_ids=["test::pytest -q"],
        test_commands=["pytest -q"],
        changed_files=["src/a.py"],
        commit_sha="abc",
        pr_number="12",
    )
    trace.assess_completeness()
    assert trace.complete is True
    assert trace.gaps == []
