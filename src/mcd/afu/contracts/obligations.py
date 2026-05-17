"""Contract: Obligations — answer obligations derived from understanding.

Stage 5 of the AFU spine. *Obligations* here are **answer obligations**
("what must this answer do / not do"), not normative rulings.
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
class Obligations:
    must_do: tuple[str, ...] = ()
    must_not_do: tuple[str, ...] = ()
    should_do: tuple[str, ...] = ()
    answer_shape: tuple[str, ...] = ()
    required_depth: str = "standard"
    residuals_to_disclose: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        must_do = freeze_strings(self.must_do)
        must_not_do = freeze_strings(self.must_not_do)
        overlap = set(must_do) & set(must_not_do)
        if overlap:
            raise AFUContractError(
                "Obligations: must_do and must_not_do overlap on: "
                + ", ".join(sorted(overlap))
            )
        object.__setattr__(self, "must_do", must_do)
        object.__setattr__(self, "must_not_do", must_not_do)
        object.__setattr__(self, "should_do", freeze_strings(self.should_do))
        object.__setattr__(self, "answer_shape", freeze_strings(self.answer_shape))
        object.__setattr__(self, "required_depth", str(self.required_depth or "standard").strip() or "standard")
        object.__setattr__(self, "residuals_to_disclose", freeze_residuals(self.residuals_to_disclose))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=(),
            evidence=self.must_do,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["Obligations"]
