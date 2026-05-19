"""AST-level guard: ``mcd.afu`` must not import any theory layer.

PR 1 documented this rule in :mod:`mcd.afu.__init__`. PR 2 raises it to
an enforceable test: every module under ``src/mcd/afu/**`` is parsed,
its top-level imports are extracted, and any import from a non-allowed
``mcd.*`` sub-package is rejected.

Allow-list (intentionally narrow):

* ``mcd.afu`` itself (relative imports are fine).
* ``mcd.core`` — kernel primitives (residual taxonomy, epistemic rank).

Adding to the allow-list requires an explicit change to this test;
that is the design.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

AFU_ROOT = Path(__file__).resolve().parents[2] / "src" / "mcd" / "afu"

ALLOWED_MCD_PREFIXES = (
    "mcd.afu",
    "mcd.core",
)


def _iter_afu_modules() -> list[Path]:
    return sorted(p for p in AFU_ROOT.rglob("*.py") if "__pycache__" not in p.parts)


def _import_targets(tree: ast.AST) -> list[str]:
    """Return fully-qualified module names that this AST imports from ``mcd.*``."""
    targets: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name.startswith("mcd."):
                    targets.append(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # node.level > 0 means a relative import; resolved within mcd.afu.
            if node.level > 0:
                continue
            if module.startswith("mcd."):
                targets.append(module)
            elif module == "mcd":
                targets.append("mcd")
    return targets


def _is_allowed(name: str) -> bool:
    return any(
        name == prefix or name.startswith(prefix + ".")
        for prefix in ALLOWED_MCD_PREFIXES
    )


@pytest.mark.parametrize("module_path", _iter_afu_modules(), ids=lambda p: str(p))
def test_no_theory_imports_in_afu_module(module_path: Path):
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module_path))
    for target in _import_targets(tree):
        assert _is_allowed(target), (
            f"{module_path} imports forbidden theory module {target!r}; "
            f"AFU may only import from {ALLOWED_MCD_PREFIXES}"
        )


def test_afu_root_exists_and_is_a_package():
    assert (AFU_ROOT / "__init__.py").is_file()


def test_guard_actually_scans_more_than_one_module():
    # Sanity: the parametrize must have picked up real files; otherwise
    # the guard would silently pass.
    assert len(_iter_afu_modules()) >= 5
