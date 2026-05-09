"""Test Audit — analyses the test suite distribution and quality."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class TestAuditResult:
    total_tests_detected: int
    tests_by_layer: dict[str, int]
    critical_tests_present: list[str]
    estimated_coverage_quality: str  # "weak" | "moderate" | "strong"
    findings: list[str]
    recommendations: list[str]


LAYER_PATTERNS = {
    "core": re.compile(r"test_(core|measures|certainty|evidence|nodes|relations|roles|symbols|vectors)"),
    "engines": re.compile(r"test_(decoder|normalizer|reasoning|fractal_composer|unicode|pattern|learning|evidence_gate|role_inf)"),
    "nabhani": re.compile(r"test_nabhani"),
    "classification": re.compile(r"test_(classif|prompt_frame|vector_composer|prompt_router|certainty_policy|evidence_need|judgment|concept_extract|concept_class|taxonomy|fractal_prompt)"),
    "grounding": re.compile(r"test_grounding"),
    "evaluation": re.compile(r"test_evaluation"),
    "cli": re.compile(r"test_cli"),
}

CRITICAL_TESTS = [
    "test_nabhani_decoder",
    "test_fractal_prompt_classifier",
    "test_grounded_reasoning_builder",
    "test_cli_classify",
    "test_cli_ground",
]


def _count_test_functions(path: Path) -> int:
    """Count def test_ functions in a file."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return len(re.findall(r"^\s*def test_", content, re.MULTILINE))
    except Exception:
        return 0


class TestAudit:
    def __init__(self, root: str | None = None) -> None:
        if root is None:
            self._root = Path(__file__).resolve().parents[3]
        else:
            self._root = Path(root)

    def run(self) -> TestAuditResult:
        tests_dir = self._root / "tests"
        findings: list[str] = []
        recommendations: list[str] = []

        if not tests_dir.exists():
            return TestAuditResult(
                total_tests_detected=0,
                tests_by_layer={},
                critical_tests_present=[],
                estimated_coverage_quality="weak",
                findings=["tests/ directory not found"],
                recommendations=["Create tests/ directory and add tests"],
            )

        test_files = list(tests_dir.rglob("test_*.py"))
        total = sum(_count_test_functions(f) for f in test_files)

        tests_by_layer: dict[str, int] = {}
        for layer, pattern in LAYER_PATTERNS.items():
            layer_files = [f for f in test_files if pattern.search(f.name)]
            tests_by_layer[layer] = sum(_count_test_functions(f) for f in layer_files)

        critical_present = [t for t in CRITICAL_TESTS if any(f.name.startswith(t) for f in test_files)]
        missing_critical = [t for t in CRITICAL_TESTS if t not in critical_present]

        if missing_critical:
            findings.append(f"Missing critical tests: {missing_critical}")
            recommendations.extend([f"Add {t}.py" for t in missing_critical])

        # Estimate quality
        layers_covered = sum(1 for v in tests_by_layer.values() if v > 0)
        if total >= 400 and layers_covered >= 5:
            quality = "strong"
        elif total >= 100 and layers_covered >= 3:
            quality = "moderate"
        else:
            quality = "weak"

        findings.append(f"Total test functions detected: {total}")
        findings.append(f"Layers with tests: {layers_covered}/{len(LAYER_PATTERNS)}")

        if tests_by_layer.get("cli", 0) == 0:
            findings.append("No CLI tests detected")
            recommendations.append("Add CLI smoke tests")
        if tests_by_layer.get("evaluation", 0) == 0:
            findings.append("No evaluation layer tests yet")
            recommendations.append("Add evaluation tests")

        return TestAuditResult(
            total_tests_detected=total,
            tests_by_layer=tests_by_layer,
            critical_tests_present=critical_present,
            estimated_coverage_quality=quality,
            findings=findings,
            recommendations=recommendations,
        )
