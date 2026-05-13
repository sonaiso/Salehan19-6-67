from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_formal_theorem_contract_check_script_passes():
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "research/formal/lean/scripts/contract_check.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"script failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "Lean fallback contract checks passed." in result.stdout
