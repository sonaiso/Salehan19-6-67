"""Contract: LicensedResponse — the final, traceable AFU artefact.

Stage 8 of the AFU spine. Bundles every prior stage. Enforces two of
the most important constitutional invariants at construction time:

* ``answer_before_understanding_payload`` — refuses to be built when
  the bundled :class:`UnderstandingPayload` is not :meth:`complete`.
* ``global_certificate_from_pipeline`` — refuses a CERTIFICATE
  ``rank`` unless every component stage is itself CERTIFICATE *and* at
  least one ``narrow_certificate`` is explicitly attested. Even then,
  the rank is the meet of every component rank.
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
from .answer_plan import AnswerPlan
from .obligations import Obligations
from .response_audit import ResponseAudit
from .understanding_judgment import UnderstandingPayload


@dataclass(frozen=True)
class LicensedResponse:
    answer: str
    understanding: UnderstandingPayload
    obligations: Obligations
    answer_plan: AnswerPlan
    audit: ResponseAudit
    narrow_certificates: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    trace: tuple[TraceStep, ...] = ()
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    schema_version: str = AFU_SCHEMA_VERSION
    contract_version: str = AFU_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.understanding, UnderstandingPayload):
            raise AFUContractError("LicensedResponse.understanding must be UnderstandingPayload")
        if not isinstance(self.obligations, Obligations):
            raise AFUContractError("LicensedResponse.obligations must be Obligations")
        if not isinstance(self.answer_plan, AnswerPlan):
            raise AFUContractError("LicensedResponse.answer_plan must be AnswerPlan")
        if not isinstance(self.audit, ResponseAudit):
            raise AFUContractError("LicensedResponse.audit must be ResponseAudit")

        # Rule: No Answer Before UnderstandingPayload.
        if not self.understanding.complete():
            if str(self.answer or "").strip():
                raise AFUContractError(
                    "answer_before_understanding_payload: cannot emit an answer "
                    "without a complete UnderstandingPayload"
                )

        object.__setattr__(self, "answer", str(self.answer or ""))
        object.__setattr__(self, "narrow_certificates", freeze_strings(self.narrow_certificates))
        object.__setattr__(self, "residuals", freeze_residuals(self.residuals))

        trace = tuple(self.trace or ())
        for step in trace:
            if not isinstance(step, TraceStep):
                raise AFUContractError("LicensedResponse.trace entries must be TraceStep")
        object.__setattr__(self, "trace", trace)

        # Compute the final rank as the meet of every component rank,
        # then apply the global-certificate guard.
        component_ranks = (
            self.understanding.rank,
            self.obligations.rank,
            self.answer_plan.rank,
            self.audit.rank,
        )
        meet = min(component_ranks)
        rank = normalize_rank(self.rank)
        if rank > meet:
            rank = normalize_rank(meet)

        if rank == EpistemicRank.CERTIFICATE:
            # Global CERTIFICATE is only legal when:
            #  - the audit passed,
            #  - no blocking residuals remain, and
            #  - at least one narrow certificate is explicitly attested.
            if (
                not self.audit.passed()
                or residuals_block_certificate(self.residuals)
                or not self.narrow_certificates
            ):
                rank = EpistemicRank.HYPOTHESIS

        object.__setattr__(self, "rank", rank)

    def to_licensed_output(self) -> LicensedOutput:
        return LicensedOutput(
            selected_gates=self.understanding.selected_gates,
            evidence=self.understanding.judgment.supporting_evidence,
            residuals=self.residuals,
            rank=self.rank,
        )


__all__ = ["LicensedResponse"]
