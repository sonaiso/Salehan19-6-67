"""Contract: UnderstandingJudgment + UnderstandingPayload.

Stage 4 of the AFU spine. Issues a *understanding* judgment — not a
fiqh ruling. The bundled :class:`UnderstandingPayload` is what later
stages (ObligationPlanner, AnswerPlan, ResponseAudit, LicensedResponse)
consume. The "No Answer Before UnderstandingPayload" rule is enforced
by :class:`~mcd.afu.contracts.licensed_response.LicensedResponse`, which
refuses to be built without a complete payload.
"""
from __future__ import annotations

from dataclasses import dataclass

from mcd.afu import AFU_CONTRACT_VERSION, AFU_SCHEMA_VERSION

from ._common import (
    AFUContractError,
    EpistemicRank,
    LicensedOutput,
    TraceStep,
    freeze_residuals,
    freeze_strings,
    normalize_rank,
    residuals_block_certificate,
)
from .linked_understanding import LinkedUnderstanding
from .prior_filter import PriorInformationFilter
from .prompt_reality import PromptReality


@dataclass(frozen=True)
class UnderstandingJudgment:
    """A general understanding judgment (NOT a normative ruling)."""

    main_judgment: str
    supporting_evidence: tuple[str, ...] = ()
    rejected_interpretations: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.main_judgment, str) or not self.main_judgment.strip():
            raise AFUContractError("UnderstandingJudgment.main_judgment must be non-empty")
        object.__setattr__(self, "main_judgment", self.main_judgment.strip())
        object.__setattr__(self, "supporting_evidence", freeze_strings(self.supporting_evidence))
        object.__setattr__(self, "rejected_interpretations", freeze_strings(self.rejected_interpretations))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        rank = normalize_rank(self.rank)
        # A judgment cannot be CERTIFICATE without supporting evidence.
        if rank == EpistemicRank.CERTIFICATE and not self.supporting_evidence:
            rank = EpistemicRank.HYPOTHESIS
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)


@dataclass(frozen=True)
class UnderstandingPayload:
    """Bundle consumed by every downstream stage.

    The Linker output and the judgment are joined here. Constructing
    this object is the **precondition** for any answer-generation
    stage. The runner (future PR) must refuse to advance to
    ObligationPlanner / AnswerPlan / LicensedResponse if this payload
    is not :meth:`complete`.
    """

    prompt_reality: PromptReality
    prior_filter: PriorInformationFilter
    linked_understanding: LinkedUnderstanding
    judgment: UnderstandingJudgment
    explicit_request: tuple[str, ...] = ()
    implicit_request: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    task_type: str = "unknown"
    user_goal: str = ""
    required_output_shape: str | None = None
    selected_gates: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    trace: tuple[TraceStep, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.prompt_reality, PromptReality):
            raise AFUContractError("UnderstandingPayload.prompt_reality must be PromptReality")
        if not isinstance(self.prior_filter, PriorInformationFilter):
            raise AFUContractError("UnderstandingPayload.prior_filter must be PriorInformationFilter")
        if not isinstance(self.linked_understanding, LinkedUnderstanding):
            raise AFUContractError("UnderstandingPayload.linked_understanding must be LinkedUnderstanding")
        if not isinstance(self.judgment, UnderstandingJudgment):
            raise AFUContractError("UnderstandingPayload.judgment must be UnderstandingJudgment")
        # Block silent_level_skip: linked_understanding must reference the
        # same prompt_reality and prior_filter instances (by equality).
        if self.linked_understanding.prompt_reality != self.prompt_reality:
            raise AFUContractError(
                "silent_level_skip: linked_understanding.prompt_reality mismatch"
            )
        if self.linked_understanding.prior_filter != self.prior_filter:
            raise AFUContractError(
                "silent_level_skip: linked_understanding.prior_filter mismatch"
            )

        object.__setattr__(self, "explicit_request", freeze_strings(self.explicit_request))
        object.__setattr__(self, "implicit_request", freeze_strings(self.implicit_request))
        object.__setattr__(self, "exclusions", freeze_strings(self.exclusions))
        object.__setattr__(self, "task_type", str(self.task_type or "unknown").strip() or "unknown")
        object.__setattr__(self, "user_goal", str(self.user_goal or ""))
        object.__setattr__(self, "selected_gates", freeze_strings(self.selected_gates))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))
        # Trace is a tuple of TraceStep; validate type strictly.
        trace = tuple(self.trace or ())
        for step in trace:
            if not isinstance(step, TraceStep):
                raise AFUContractError("UnderstandingPayload.trace entries must be TraceStep")
        object.__setattr__(self, "trace", trace)

        rank = normalize_rank(self.rank)
        # The payload rank is the meet of its components — never above
        # the weakest stage. This implements rank monotonicity at the
        # contract level without needing a runner.
        component_ranks = (
            self.prompt_reality.rank,
            self.prior_filter.rank,
            self.linked_understanding.rank,
            self.judgment.rank,
        )
        meet = min(component_ranks)
        if rank > meet:
            rank = normalize_rank(meet)
        if rank == EpistemicRank.CERTIFICATE and residuals_block_certificate(self.residuals):
            rank = EpistemicRank.HYPOTHESIS
        object.__setattr__(self, "rank", rank)

    def complete(self) -> bool:
        """A payload is *complete* when all four upstream stages exist
        and the judgment provides supporting evidence. Without a
        complete payload no answer may be emitted (enforced by
        :class:`LicensedResponse`)."""
        return bool(
            self.prompt_reality
            and self.prior_filter
            and self.linked_understanding
            and self.judgment
            and self.judgment.main_judgment
            and self.judgment.supporting_evidence
        )

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=self.selected_gates,
            evidence=self.judgment.supporting_evidence,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["UnderstandingJudgment", "UnderstandingPayload"]
