import json
from pathlib import Path


def _load_worktree() -> dict:
    path = Path(__file__).resolve().parents[1] / "spec" / "worktree" / "nabhani_mind_worktree.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _node_by_id(worktree: dict, node_id: str) -> dict:
    for node in worktree["nodes"]:
        if node["id"] == node_id:
            return node
    raise AssertionError(f"missing node: {node_id}")


def test_fit_brain_is_not_root_mind() -> None:
    worktree = _load_worktree()
    fit_brain = _node_by_id(worktree, "fit_brain_condition")

    assert fit_brain["type"] == "biological_condition"
    assert fit_brain["parent"] == "nabhani_cognitive_kernel"
    assert fit_brain["id"] != "mind_geometry"
    assert fit_brain["beta"] == "condition_only"


def test_epistemic_zero_genesis_exists() -> None:
    worktree = _load_worktree()
    zero_genesis = _node_by_id(worktree, "epistemic_zero_genesis")

    assert zero_genesis["type"] == "cognitive_activation"
    assert zero_genesis["dependencies"] == ["fit_brain_condition"]
    assert zero_genesis["progress_status"] == "HYPOTHESIS"


def test_mind_geometry_depends_on_epistemic_zero_genesis() -> None:
    worktree = _load_worktree()
    mind_geometry = _node_by_id(worktree, "mind_geometry")

    assert "epistemic_zero_genesis" in mind_geometry["dependencies"]


def test_initial_zero_distinct_from_final_zero() -> None:
    worktree = _load_worktree()
    distinction = worktree["zero_distinction"]
    initial_zero = _node_by_id(worktree, distinction["initial"])
    final_zero = _node_by_id(worktree, distinction["final"])

    assert distinction["initial"] != distinction["final"]
    assert initial_zero["type"] == "cognitive_activation"
    assert initial_zero["judgment"] == "HYPOTHESIS"
    assert initial_zero["judgment"] != "ZERO"
    assert final_zero["judgment"] == "ZERO"
    assert distinction["final_zero_requires"] == "blocking_failure"


def test_brain_condition_is_not_industrial_or_judgment_node() -> None:
    worktree = _load_worktree()
    fit_brain = _node_by_id(worktree, "fit_brain_condition")

    assert fit_brain["type"] not in {"industrial_application", "final_judgment"}
    assert fit_brain["judgment"] == "HYPOTHESIS"
