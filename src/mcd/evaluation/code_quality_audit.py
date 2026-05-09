"""Code Quality Audit — static analysis of code quality indicators."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class CodeQualityAuditResult:
    long_files: list[str]        # files with > 300 lines
    long_functions: list[str]    # functions with > 80 lines
    print_statements: list[str]  # files with print() in src/mcd
    todo_count: int
    potential_magic_strings: list[str]
    quality_score: float         # 0.0 - 1.0
    findings: list[str]
    recommendations: list[str]


class CodeQualityAudit:
    MAX_FILE_LINES = 300
    MAX_FUNC_LINES = 80
    LONG_FILE_THRESHOLD = 300
    LONG_FUNC_THRESHOLD = 80

    def __init__(self, root: str | None = None) -> None:
        if root is None:
            self._root = Path(__file__).resolve().parents[3]
        else:
            self._root = Path(root)
        self._src = self._root / "src" / "mcd"

    def run(self) -> CodeQualityAuditResult:
        findings: list[str] = []
        recommendations: list[str] = []
        long_files: list[str] = []
        long_functions: list[str] = []
        print_statements: list[str] = []
        todo_count = 0
        magic_strings: list[str] = []

        if not self._src.exists():
            return CodeQualityAuditResult(
                long_files=[], long_functions=[], print_statements=[],
                todo_count=0, potential_magic_strings=[], quality_score=0.0,
                findings=["src/mcd not found"], recommendations=["Create src/mcd"],
            )

        py_files = list(self._src.rglob("*.py"))
        total_files = len(py_files)
        issues = 0

        for f in py_files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()

            # Long files
            if len(lines) > self.LONG_FILE_THRESHOLD:
                long_files.append(f"{f.relative_to(self._root)} ({len(lines)} lines)")
                issues += 1

            # print() in src
            if "cli.py" not in f.name:  # CLI prints are expected
                if re.search(r"^\s*print\(", content, re.MULTILINE):
                    print_statements.append(str(f.relative_to(self._root)))
                    issues += 1

            # TODO count
            todos = len(re.findall(r"#\s*TODO", content, re.IGNORECASE))
            todo_count += todos

            # Long functions
            func_starts = [(m.start(), m.group(1)) for m in re.finditer(r"def (test_\w+|\w+)\(", content)]
            for i, (start, fname) in enumerate(func_starts):
                end = func_starts[i + 1][0] if i + 1 < len(func_starts) else len(content)
                func_lines = content[start:end].count("\n")
                if func_lines > self.LONG_FUNC_THRESHOLD:
                    long_functions.append(f"{f.relative_to(self._root)}::{fname} ({func_lines} lines)")
                    issues += 1

            # Magic strings (classification-like strings outside enums)
            if "classification" in str(f) or "taxonomy" in f.name:
                raw_strings = re.findall(r'"(epistemic|technical|shari|practical|value)\w*"', content)
                if len(raw_strings) > 10:
                    magic_strings.append(str(f.relative_to(self._root)))

        # Quality score
        penalty = min(issues, total_files) / max(total_files, 1)
        quality_score = max(0.0, round(1.0 - penalty * 0.5, 3))

        if todo_count > 10:
            findings.append(f"High TODO count: {todo_count}")
            recommendations.append("Resolve or track TODOs in an issue tracker")
        if long_files:
            findings.append(f"Long files (>{self.LONG_FILE_THRESHOLD} lines): {len(long_files)}")
            recommendations.append("Consider splitting long files into smaller modules")
        if print_statements:
            findings.append(f"print() found in non-CLI source files: {print_statements}")
            recommendations.append("Replace print() with logging in src/ modules")
        if long_functions:
            findings.append(f"Long functions (>{self.LONG_FUNC_THRESHOLD} lines): {len(long_functions)}")
            recommendations.append("Refactor long functions into smaller helpers")

        findings.append(f"Code quality score: {quality_score:.2f}")

        return CodeQualityAuditResult(
            long_files=long_files,
            long_functions=long_functions,
            print_statements=print_statements,
            todo_count=todo_count,
            potential_magic_strings=magic_strings,
            quality_score=quality_score,
            findings=findings,
            recommendations=recommendations,
        )
