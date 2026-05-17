"""Contract: LinkedUnderstanding — output of the Linker stage.

Stage 3 of the AFU spine. Pure join of :class:`PromptReality` with the
``allowed_prior_information`` from :class:`PriorInformationFilter`.

Architectural law (enforced in ``__post_init__``):

* Every entry in ``linked_prior_information`` must appear in the
  upstream filter's ``allowed_prior_information``. Any entry that
  appears in ``blocked_prior_opinions`` is rejected — that is the
  ``prior_opinion_into_linker`` forbidden transition.
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
from .prior_filter import PriorInformationFilter
from .prompt_reality import PromptReality


@dataclass(frozen=True)
class LinkedUnderstanding:
    prompt_reality: PromptReality
    prior_filter: PriorInformationFilter
    linked_prior_information: tuple[str, ...] = ()
    linked_summary: str = ""
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.prompt_reality, PromptReality):
            raise AFUContractError("LinkedUnderstanding.prompt_reality must be PromptReality")
        if not isinstance(self.prior_filter, PriorInformationFilter):
            raise AFUContractError("LinkedUnderstanding.prior_filter must be PriorInformationFilter")

        linked = freeze_strings(self.linked_prior_information)
        blocked = set(self.prior_filter.blocked_prior_opinions)
        allowed = set(self.prior_filter.allowed_prior_information)

        intruding = [item for item in linked if item in blocked]
        if intruding:
            # Forbidden transition: prior_opinion_into_linker.
            raise AFUContractError(
                "prior_opinion_into_linker: blocked prior opinions reached Linker: "
                + ", ".join(intruding)
            )
        unknown = [item for item in linked if item not in allowed]
        if unknown:
            raise AFUContractError(
                "LinkedUnderstanding.linked_prior_information must be a subset of "
                "PriorInformationFilter.allowed_prior_information; unknown: "
                + ", ".join(unknown)
            )

        object.__setattr__(self, "linked_prior_information", linked)
        object.__setattr__(self, "linked_summary", str(self.linked_summary or ""))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=(),
            evidence=self.linked_prior_information,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["LinkedUnderstanding"]
