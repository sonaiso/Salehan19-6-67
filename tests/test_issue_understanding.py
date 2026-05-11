from mcd.coding_copilot.issue_understanding import IssueUnderstanding


def test_unknown_issue_emits_ambiguity_residual():
    issue = IssueUnderstanding(issue_id="I-1", raw_text="???", task_type="unknown")
    issue.ensure_consistency()
    assert any(r.residual_type == "ambiguous_issue_scope" for r in issue.ambiguity_residuals)
