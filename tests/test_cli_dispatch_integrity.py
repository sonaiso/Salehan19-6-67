from __future__ import annotations

import ast
from pathlib import Path


def _is_command_expr(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "args"
        and node.attr == "command"
    ) or (isinstance(node, ast.Name) and node.id == "cmd")


def _collect_cli_commands(tree: ast.AST) -> tuple[list[str], set[str]]:
    registered: list[str] = []
    dispatched: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_parser":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                registered.append(node.args[0].value)

        if not isinstance(node, ast.Compare):
            continue

        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            left, right = node.left, node.comparators[0]
            if _is_command_expr(left) and isinstance(right, ast.Constant) and isinstance(right.value, str):
                dispatched.add(right.value)
            if _is_command_expr(right) and isinstance(left, ast.Constant) and isinstance(left.value, str):
                dispatched.add(left.value)

        if len(node.ops) == 1 and isinstance(node.ops[0], ast.In) and _is_command_expr(node.left):
            comparator = node.comparators[0]
            if isinstance(comparator, (ast.Tuple, ast.List, ast.Set)):
                for elt in comparator.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        dispatched.add(elt.value)

    return registered, dispatched


def test_cli_registered_commands_are_unique_and_dispatched():
    cli_path = Path("src/mcd/cli.py")
    tree = ast.parse(cli_path.read_text(encoding="utf-8"), filename=str(cli_path))
    registered, dispatched = _collect_cli_commands(tree)

    registered_set = set(registered)
    duplicate_registrations = sorted({name for name in registered if registered.count(name) > 1})

    assert not duplicate_registrations, f"duplicate command registrations: {duplicate_registrations}"
    assert not (registered_set - dispatched), f"missing dispatch branches: {sorted(registered_set - dispatched)}"
