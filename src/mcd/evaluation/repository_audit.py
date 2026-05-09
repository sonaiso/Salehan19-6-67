"""Repository Audit — inspects the repository structure and reports findings."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
from pathlib import Path


@dataclass
class RepositoryAuditResult:
    src_file_count: int
    test_file_count: int
    docs_file_count: int
    packages_detected: list[str]
    missing_expected_packages: list[str]
    cli_detected: bool
    readme_detected: bool
    pyproject_detected: bool
    status: str  # "pass" | "warning" | "fail"
    findings: list[str]
    recommendations: list[str]


class RepositoryAudit:
    """Inspect the MCD repository structure and return an audit result."""

    EXPECTED_PACKAGES = ["core", "engines", "knowledge", "nabhani", "classification", "grounding", "evaluation"]
    EXPECTED_LAYERS = ["core", "engines", "knowledge", "nabhani", "classification"]

    def __init__(self, root: str | None = None) -> None:
        if root is None:
            # Detect root from this file's location: src/mcd/evaluation/repository_audit.py
            self._root = Path(__file__).resolve().parents[3]
        else:
            self._root = Path(root)

    def run(self) -> RepositoryAuditResult:
        src_mcd = self._root / "src" / "mcd"
        tests_dir = self._root / "tests"
        docs_dir = self._root / "docs"

        src_files = list(src_mcd.rglob("*.py")) if src_mcd.exists() else []
        test_files = list(tests_dir.rglob("*.py")) if tests_dir.exists() else []
        docs_files = list(docs_dir.rglob("*.md")) if docs_dir.exists() else []

        packages_detected = [
            d.name for d in src_mcd.iterdir()
            if d.is_dir() and (d / "__init__.py").exists()
        ] if src_mcd.exists() else []

        missing = [p for p in self.EXPECTED_PACKAGES if p not in packages_detected]

        cli_detected = (src_mcd / "cli.py").exists()
        readme_detected = (self._root / "README.md").exists()
        pyproject_detected = (self._root / "pyproject.toml").exists()

        findings: list[str] = []
        recommendations: list[str] = []

        if not cli_detected:
            findings.append("cli.py not found")
            recommendations.append("Add src/mcd/cli.py")
        if not readme_detected:
            findings.append("README.md missing")
            recommendations.append("Add README.md")
        if not pyproject_detected:
            findings.append("pyproject.toml missing")
            recommendations.append("Add pyproject.toml")
        if missing:
            findings.append(f"Missing expected packages: {missing}")
            recommendations.append(f"Add packages: {missing}")

        findings.append(f"src files: {len(src_files)}, test files: {len(test_files)}, docs: {len(docs_files)}")

        # Layer test coverage
        for layer in self.EXPECTED_LAYERS:
            layer_tests = [f for f in test_files if layer in f.name]
            if not layer_tests:
                findings.append(f"No tests detected for layer: {layer}")
                recommendations.append(f"Add tests for {layer} layer")

        # Status
        critical_missing = not cli_detected or not readme_detected or not pyproject_detected
        if critical_missing or len(missing) > 2:
            status = "fail"
        elif missing:
            status = "warning"
        else:
            status = "pass"

        return RepositoryAuditResult(
            src_file_count=len(src_files),
            test_file_count=len(test_files),
            docs_file_count=len(docs_files),
            packages_detected=sorted(packages_detected),
            missing_expected_packages=missing,
            cli_detected=cli_detected,
            readme_detected=readme_detected,
            pyproject_detected=pyproject_detected,
            status=status,
            findings=findings,
            recommendations=recommendations,
        )
