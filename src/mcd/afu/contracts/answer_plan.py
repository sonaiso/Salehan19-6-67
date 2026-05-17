"""Contract: AnswerPlan — shape of the planned answer.

Stage 6 of the AFU spine. No answer text yet — only the planned shape.
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu import AFU_CONTRACT_VERSION, AFU_SCHEMA_VERSION

from ._common import (
    AFUContractError,
    EpistemicRank,
    LicensedOutput,
    freeze_residuals,
    freeze_strings,
    normalize_rank,
    residuals_block_certificate,
)


@dataclass(frozen=True)
class AnswerPlan:
    sections: tuple[str, ...] = ()
    sequence: tuple[str, ...] = ()
    examples_needed: tuple[str, ...] = ()
    code_needed: bool = False
    diagrams_needed: bool = False
    risk_notes: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        sections = freeze_strings(self.sections)
        sequence = freeze_strings(self.sequence)
        if sequence and set(sequence) - set(sections):
            unknown = sorted(set(sequence) - set(sections))
            raise AFUContractError(
                "AnswerPlan.sequence references unknown sections: " + ", ".join(unknown)
            )
        object.__setattr__(self, "sections", sections)
        object.__setattr__(self, "sequence", sequence)
        object.__setattr__(self, "examples_needed", freeze_strings(self.examples_needed))
        object.__setattr__(self, "risk_notes", freeze_strings(self.risk_notes))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=(),
            evidence=self.sections,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["AnswerPlan"]
