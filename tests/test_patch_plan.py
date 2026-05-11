from mcd.coding_copilot.code_claim import CodeClaim
from mcd.coding_copilot.patch_plan import PatchPlan


def test_missing_tests_hypothesis_inputs_emit_residual():
    claim = CodeClaim("C-1", "fixes_bug", ["src/a.py"], "fix bug")
    plan = PatchPlan(plan_id="P-1", claims=[claim], steps=["edit"], expected_tests=[], rollback_plan="revert")
    plan.ensure_consistency(task_type="bugfix")
    assert any(r.residual_type == "missing_expected_tests" for r in plan.residuals)
