from __future__ import annotations

from pathlib import Path


REQUIRED_TOKENS = {
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
    "TriadClosure.lean": ["theorem triad_closure"],
}


def _line_number_for(text: str, token: str) -> int | None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return line_number
    return None


def validate_contracts(base: Path) -> None:
    for file_name, tokens in REQUIRED_TOKENS.items():
        path = base / file_name
        text = path.read_text(encoding="utf-8")
        if "sorry" in text:
            line_number = _line_number_for(text, "sorry")
            location = f":{line_number}" if line_number is not None else ""
            raise AssertionError(f'"sorry" is not allowed in {path}{location}')
        for token in tokens:
            if token not in text:
                raise AssertionError(f"missing token {token} in {path}")


def main() -> None:
    validate_contracts(Path("research/formal/lean"))
    print("Lean fallback contract checks passed.")


if __name__ == "__main__":
    main()
