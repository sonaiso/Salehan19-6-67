"""Contract: PriorInformationFilter — Nabhani-style separation of
*prior information* (allowed) from *prior opinion* (blocked).

Stage 2 of the AFU spine. This is the gate that prevents prior opinion
from contaminating understanding. The Linker (stage 3) is then required
to only consume ``allowed_prior_information``.
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
class PriorInformationFilter:
    """Partition of prior context into allowed information vs blocked opinion."""

    allowed_prior_information: tuple[str, ...] = ()
    blocked_prior_opinions: tuple[str, ...] = ()
    contamination_risks: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        allowed = freeze_strings(self.allowed_prior_information)
        blocked = freeze_strings(self.blocked_prior_opinions)
        # An item must not be simultaneously allowed and blocked.
        overlap = set(allowed) & set(blocked)
        if overlap:
            raise AFUContractError(
                "PriorInformationFilter: items cannot be both allowed and blocked: "
                + ", ".join(sorted(overlap))
            )
        object.__setattr__(self, "allowed_prior_information", allowed)
        object.__setattr__(self, "blocked_prior_opinions", blocked)
        object.__setattr__(self, "contamination_risks", freeze_strings(self.contamination_risks))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=(),
            evidence=self.allowed_prior_information,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["PriorInformationFilter"]
