"""CLI Audit — checks which CLI commands are available and functional."""
from __future__ import annotations
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CLIAuditResult:
    commands_detected: list[str]
    expected_commands: list[str]
    missing_commands: list[str]
    smoke_test_results: dict[str, bool]
    json_output_supported: bool
    findings: list[str]
    recommendations: list[str]


EXPECTED_COMMANDS = ["decode", "nabhani", "classify", "ground", "evaluate-project", "benchmark-simulation", "readiness-score"]


class CLIAudit:
    def __init__(self, root: str | None = None) -> None:
        if root is None:
            self._root = Path(__file__).resolve().parents[3]
        else:
            self._root = Path(root)

    def _detect_commands(self) -> list[str]:
        """Parse cli.py to find add_parser calls."""
        cli_path = self._root / "src" / "mcd" / "cli.py"
        if not cli_path.exists():
            return []
        import re
        content = cli_path.read_text(encoding="utf-8", errors="ignore")
        return re.findall(r'add_parser\s*\(\s*["\']([^"\']+)["\']', content)

    def _smoke_test(self, command: str, sample_text: str = "النار تحرق") -> bool:
        """Run a CLI command and return True if exit code is 0."""
        src_dir = str(self._root / "src")
        cmd = [sys.executable, "-m", "mcd.cli", command]
        # Commands that need text argument
        text_commands = {"decode", "nabhani", "classify", "ground"}
        if command in text_commands:
            cmd.append(sample_text)
        elif command in {"evaluate-project", "benchmark-simulation", "readiness-score"}:
            cmd += ["--output", "json"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                env={**__import__("os").environ, "PYTHONPATH": src_dir},
            )
            return result.returncode == 0
        except Exception:
            return False

    def run(self, run_smoke_tests: bool = False) -> CLIAuditResult:
        findings: list[str] = []
        recommendations: list[str] = []

        commands_detected = self._detect_commands()
        missing = [c for c in EXPECTED_COMMANDS if c not in commands_detected]

        smoke_results: dict[str, bool] = {}
        if run_smoke_tests:
            for cmd in commands_detected:
                smoke_results[cmd] = self._smoke_test(cmd)

        json_supported = any(
            "json" in cmd for cmd in
            (self._root / "src" / "mcd" / "cli.py").read_text(encoding="utf-8", errors="ignore").split("\n")
            if "output" in cmd
        ) if (self._root / "src" / "mcd" / "cli.py").exists() else False

        if missing:
            findings.append(f"Missing commands: {missing}")
            for m in missing:
                recommendations.append(f"Implement CLI command: {m}")

        failures = [k for k, v in smoke_results.items() if not v]
        if failures:
            findings.append(f"Smoke test failures: {failures}")
            recommendations.append("Fix CLI commands that fail smoke tests")

        findings.append(f"Commands detected: {commands_detected}")

        return CLIAuditResult(
            commands_detected=commands_detected,
            expected_commands=EXPECTED_COMMANDS,
            missing_commands=missing,
            smoke_test_results=smoke_results,
            json_output_supported=json_supported,
            findings=findings,
            recommendations=recommendations,
        )
