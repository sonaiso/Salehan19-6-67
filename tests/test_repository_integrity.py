from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import Path


def _iter_python_files(*roots: str):
    for root in roots:
        for path in Path(root).rglob("*.py"):
            if "__pycache__" not in path.parts:
                yield path


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _all_function_names(path: Path) -> set[str]:
    names: set[str] = set()
    tree = _parse(path)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def test_no_duplicate_top_level_definitions():
    for path in _iter_python_files("src", "tests", "research/formal/lean/scripts"):
        tree = _parse(path)
        top_level_names = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        duplicates = sorted(name for name, count in Counter(top_level_names).items() if count > 1)
        assert not duplicates, f"{path} has duplicate top-level symbols: {duplicates}"


def test_no_duplicate_test_functions():
    for path in Path("tests").glob("test_*.py"):
        tree = _parse(path)
        test_names = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        ]
        duplicates = sorted(name for name, count in Counter(test_names).items() if count > 1)
        assert not duplicates, f"{path} has duplicate test names: {duplicates}"


def test_formal_obligations_mapping_consistency():
    obligations_payload = json.loads(Path("research/formal/theorem_obligations.json").read_text(encoding="utf-8"))
    mapping_payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))

    obligation_ids = [item["id"] for item in obligations_payload["obligations"]]
    mapping_ids = [item["obligation"] for item in mapping_payload["mapping"]]

    assert len(obligation_ids) == len(set(obligation_ids))
    assert len(mapping_ids) == len(set(mapping_ids))
    assert set(obligation_ids) == set(mapping_ids)


def test_formal_mapping_entries_reference_real_files_tests_and_theorems():
    payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))

    for item in payload["mapping"]:
        python_file = Path(item["python_file"])
        test_file = Path(item["test_file"])
        lean_file = Path(item["lean_file"])

        assert python_file.exists(), f"missing python file: {python_file}"
        assert test_file.exists(), f"missing test file: {test_file}"
        assert lean_file.exists(), f"missing lean file: {lean_file}"

        for contract in item["runtime_contracts"]:
            test_path, _, test_name = contract.partition("::")
            runtime_test_file = Path(test_path)
            assert runtime_test_file.exists(), f"runtime contract path missing: {test_path}"
            assert test_name, f"runtime contract missing test function: {contract}"
            assert test_name in _all_function_names(runtime_test_file), (
                f"mapped test function not found: {contract}"
            )

        searchable_lean_files = [lean_file]
        for artifact in item.get("formal_artifacts", []):
            artifact_path = Path(artifact)
            if artifact_path.suffix == ".lean" and artifact_path.exists():
                searchable_lean_files.append(artifact_path)
        lean_text = "\n".join(path.read_text(encoding="utf-8") for path in searchable_lean_files)
        for theorem_name in item.get("theorem_contracts", []):
            token_pattern = rf"\b(?:theorem|def)\s+{re.escape(theorem_name)}\b"
            assert re.search(token_pattern, lean_text), (
                f"missing theorem/def '{theorem_name}' in mapped Lean artifacts for {item['obligation']}"
            )
