"""Contract: ResponseAudit — post-hoc audit of a planned/produced answer.

Stage 7 of the AFU spine. If exclusions are violated or overclaims
exist, the audit rank is downgraded. If required parts are missing,
the system must return ZERO/HYPOTHESIS with a clarification request
rather than a false answer.
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
class ResponseAudit:
    answers_user_request: bool = False
    violates_exclusions: bool = False
    overclaims: tuple[str, ...] = ()
    missing_required_parts: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "overclaims", freeze_strings(self.overclaims))
        object.__setattr__(self, "missing_required_parts", freeze_strings(self.missing_required_parts))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))

        rank = normalize_rank(self.rank)
        # Fail-closed downgrade rules from the constitutional brief
        # (audit questions of §16). The audit's rank can never sit
        # above what its own findings allow.
        if self.missing_required_parts:
            # Required parts missing → at most ZERO.
            rank = EpistemicRank.ZERO
        elif self.violates_exclusions or self.overclaims or not self.answers_user_request:
            # Soft violations → at most HYPOTHESIS.
            if rank == EpistemicRank.CERTIFICATE:
                rank = EpistemicRank.HYPOTHESIS
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def passed(self) -> bool:
        """Audit passes only when nothing is missing and nothing is
        flagged. A passed audit is *necessary* but not *sufficient*
        for a CERTIFICATE — narrow-claim certification still has to be
        explicitly attested by ``LicensedResponse.narrow_certificates``.
        """
        return (
            self.answers_user_request
            and not self.violates_exclusions
            and not self.overclaims
            and not self.missing_required_parts
        )

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=(),
            evidence=(),
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["ResponseAudit"]
