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


def validate_contracts(base: Path) -> None:
    for file_name, tokens in REQUIRED_TOKENS.items():
        text = (base / file_name).read_text(encoding="utf-8")
        if "sorry" in text:
            raise AssertionError(f'"sorry" is not allowed in {file_name}')
        for token in tokens:
            if token not in text:
                raise AssertionError(f"missing token {token} in {file_name}")


def main() -> None:
    validate_contracts(Path("research/formal/lean"))
    print("Lean fallback contract checks passed.")


if __name__ == "__main__":
    main()
