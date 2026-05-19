"""Shared fixture loader for the six worked examples (§§6–12 of the brief)."""
from __future__ import annotations

from pathlib import Path

import yaml

from mcd.afu.contracts._common import EpistemicRank
from mcd.afu.fractal_definition import Evidence, FractalDefinition, Residual

FIXTURE_DIR = Path(__file__).parent / "fixtures"

EXAMPLE_NAMES: tuple[str, ...] = (
    "letter",
    "vowel",
    "root",
    "pattern",
    "signifier",
    "relation",
    "judgment",
)


def load_definition(name: str) -> FractalDefinition:
    """Load a fixture YAML and construct a :class:`FractalDefinition`."""
    raw = yaml.safe_load((FIXTURE_DIR / f"{name}.yaml").read_text(encoding="utf-8"))

    evidence: list[Evidence] = []
    for e in raw.get("evidence") or ():
        evidence.append(
            Evidence(
                source=e["source"],
                claim=e["claim"],
                strength=EpistemicRank[e.get("strength", "HYPOTHESIS").upper()],
            )
        )
    residuals: list[Residual] = [
        Residual.of(code) for code in (raw.get("residuals") or ())
    ]
    rank = EpistemicRank[(raw.get("rank") or "HYPOTHESIS").upper()]
    return FractalDefinition.build(
        name=raw["name"],
        layer=raw["layer"],
        carrier=raw["carrier"],
        domain=raw["domain"],
        function=raw["function"],
        formation_gate=raw["formation_gate"],
        backward_gate=raw["backward_gate"],
        output_contract=raw["output_contract"],
        distinction=raw.get("distinction") or (),
        prior_information=raw.get("prior_information") or (),
        relation_before=raw.get("relation_before") or (),
        relation_after=raw.get("relation_after") or (),
        evidence=evidence,
        residuals=residuals,
        rank=rank,
    )
