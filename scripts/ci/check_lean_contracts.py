#!/usr/bin/env python3
"""Fallback contract checks for the minimal Lean core.

Used by the Formal Theorem Track CI workflow when the `lean` binary
is not available on the runner. Verifies that each required Lean file
exists, contains no `sorry`, and declares the expected theorem/inductive
contract tokens.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED: dict[str, list[str]] = {
    "CoreJudgment.lean": [
        "inductive PublicJudgment",
        "def certificateAllowed",
        "def publicJudgment",
    ],
    "NoIllicitCertification.lean": [
        "theorem no_illicit_certification",
        "theorem missing_gate_blocks_certificate",
        "theorem forbidden_transition_blocks_certificate",
        "theorem residual_erasure_blocks_certificate",
    ],
    "TriadClosure.lean": [
        "theorem triad_closure",
    ],
}

BASE = Path("research/formal/lean")


def main() -> int:
    errors: list[str] = []
    for file_name, tokens in REQUIRED.items():
        path = BASE / file_name
        if not path.is_file():
            errors.append(f"missing file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if "sorry" in text:
            errors.append(f"forbidden token 'sorry' present in {file_name}")
        for token in tokens:
            if token not in text:
                errors.append(f"missing token {token!r} in {file_name}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print("Lean fallback contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
