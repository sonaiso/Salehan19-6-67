import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec/worktree/nabhani_mind_worktree.json"
SCHEMA_PATH = ROOT / "spec/worktree/progress_status.schema.json"

REQUIRED_DOCS = [
    ROOT / "docs/worktree/00_WORKTREE_INDEX.md",
    ROOT / "docs/worktree/01_NABHANI_COGNITIVE_KERNEL.md",
    ROOT / "docs/worktree/02_MIND_VALIDITY_STANDARD.md",
    ROOT / "docs/worktree/03_ARCHITECTURE_OF_ARCHITECTURES.md",
    ROOT / "docs/worktree/04_LANGUAGE_REVEALS_MIND.md",
    ROOT / "docs/worktree/05_SIGNIFIER_SIGNIFIED_GEOMETRY.md",
    ROOT / "docs/worktree/06_CONCEPT_JUDGMENT_EVIDENCE.md",
    ROOT / "docs/worktree/07_PROGRAMMING_EXECUTION_TREE.md",
    ROOT / "docs/worktree/08_INDUSTRIAL_BRANCHES.md",
    ROOT / "docs/worktree/09_PROGRESS_STATUS_MATRIX.md",
    ROOT / "docs/worktree/10_RESIDUALS_AND_OPEN_GAPS.md",
]


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _nodes_by_id(spec: dict) -> dict:
    return {node["node_id"]: node for node in spec["nodes"]}


def test_worktree_json_validates_against_schema():
    schema = _load_json(SCHEMA_PATH)
    spec = _load_json(SPEC_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(spec, schema)


def test_root_node_is_nabhani_cognitive_kernel():
    spec = _load_json(SPEC_PATH)
    assert spec["root_node"] == "nabhani_cognitive_kernel"


def test_coding_copilot_depends_on_programming_geometry():
    spec = _load_json(SPEC_PATH)
    nodes = _nodes_by_id(spec)
    assert "programming_geometry" in nodes["coding_copilot_auditor"]["dependencies"]


def test_programming_geometry_depends_on_judgment_geometry():
    spec = _load_json(SPEC_PATH)
    nodes = _nodes_by_id(spec)
    assert "judgment_geometry" in nodes["programming_geometry"]["dependencies"]


def test_judgment_geometry_depends_on_mind_geometry():
    spec = _load_json(SPEC_PATH)
    nodes = _nodes_by_id(spec)
    assert "mind_geometry" in nodes["judgment_geometry"]["dependencies"]


def test_language_geometry_depends_on_mind_geometry():
    spec = _load_json(SPEC_PATH)
    nodes = _nodes_by_id(spec)
    assert "mind_geometry" in nodes["language_geometry"]["dependencies"]


def test_no_industrial_branch_is_marked_as_root():
    spec = _load_json(SPEC_PATH)
    for node in spec["nodes"]:
        if node["type"] == "industrial":
            assert node["node_id"] != spec["root_node"]


def test_every_hypothesis_node_has_residuals():
    spec = _load_json(SPEC_PATH)
    for node in spec["nodes"]:
        if node["progress_status"] == "HYPOTHESIS":
            assert node["residuals"], f"HYPOTHESIS node {node['node_id']} must include residuals"


def test_every_node_has_next_actions():
    spec = _load_json(SPEC_PATH)
    for node in spec["nodes"]:
        assert node["next_actions"], f"Node {node['node_id']} must include next_actions"


def test_required_worktree_docs_exist():
    for path in REQUIRED_DOCS:
        assert path.exists(), f"Missing required worktree doc: {path}"
