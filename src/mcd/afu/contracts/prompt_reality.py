"""Contract: PromptReality — purely descriptive view of the prompt.

Stage 1 of the AFU spine. No interpretation, no theory call. The only
CERTIFICATEs allowed at this stage are *directly observable* text
properties (e.g. ``has_arabic``, ``has_diacritics``). Anything that
requires interpretation must remain at HYPOTHESIS.
"""
from __future__ import annotations

from dataclasses import dataclass, field

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
class PromptReality:
    """What is *literally* present in the prompt — no interpretation."""

    raw_text: str
    normalized_text: str = ""
    language: str = "unknown"
    has_arabic: bool = False
    has_diacritics: bool = False
    explicit_segments: tuple[str, ...] = ()
    user_stated_goal: str | None = None
    user_stated_exclusions: tuple[str, ...] = ()
    detected_pressure: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.raw_text, str) or self.raw_text == "":
            raise AFUContractError("PromptReality.raw_text must be a non-empty string")
        object.__setattr__(self, "normalized_text", str(self.normalized_text or ""))
        object.__setattr__(self, "language", str(self.language or "unknown").strip() or "unknown")
        object.__setattr__(self, "explicit_segments", freeze_strings(self.explicit_segments))
        object.__setattr__(self, "user_stated_exclusions", freeze_strings(self.user_stated_exclusions))
        object.__setattr__(self, "detected_pressure", freeze_strings(self.detected_pressure))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        """Wrap the contract in the canonical Φᵢ license envelope."""
        return LicensedOutput(
            selected_gates=(),  # no gates yet in PR 1
            evidence=(self.raw_text,),
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["PromptReality"]
