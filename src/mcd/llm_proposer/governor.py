"""AFJGGovernor — applies AFJG governance gates to an LLM Proposal."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.core.residual_taxonomy import classify_residuals, has_blocking_residuals
from mcd.llm_proposer.governed_payload import from_governed_payload, to_governed_payload
from mcd.llm_proposer.types import GovernedAnswer, Proposal, Verdict
from mcd.nabhani.rational_method_judge import RationalMethodJudge

_CONTRADICTION_PATTERNS: tuple[str, ...] = (
    "متناقض",
    "مستحيل",
    "contradiction",
    "impossible",
    "inconsistent",
    "self-contradictory",
)
_RAW_TEXT_ANCHOR_MARKERS: tuple[str, ...] = ("raw_text", "raw-text", "raw text")

_rational_judge = RationalMethodJudge()


@dataclass
class GovernanceResult:
    verdict: Verdict
    violated_rules: list[str] = field(default_factory=list)
    trace_entries: list[str] = field(default_factory=list)


@dataclass
class ReverseTraceAssessment:
    trace_entries: list[str]
    complete: bool
    raw_text_units: list[str]
    residuals: list[str]


class AFJGGovernor:
    """Apply the full AFJG governance pipeline to a Proposal."""

    def govern(
        self,
        proposal: Proposal,
        *,
        evidence: list[Any] | None = None,
        reverse_trace: list[str] | dict[str, Any] | None = None,
    ) -> GovernedAnswer:
        ev = list(evidence or [])
        evidence_ok, evidence_residuals = self._validate_evidence(ev)
        rt_assessment = self._assess_reverse_trace(reverse_trace)
        rt = list(rt_assessment.trace_entries)
        violated: list[str] = [*evidence_residuals, *rt_assessment.residuals]
        trace: list[str] = ["governor:start"]

        result = self._gate_emptiness(proposal)
        if result is not None:
            return self._build(proposal, result, ev, rt, rt_assessment)

        result = self._gate_contradiction(proposal, evidence_ok)
        if result is not None:
            return self._build(proposal, result, ev, rt, rt_assessment)

        nabhani_result = self._gate_nabhani(proposal, ev)
        violated.extend(nabhani_result.violated_rules)
        trace.extend(nabhani_result.trace_entries)

        if nabhani_result.verdict == "ZERO":
            final = GovernanceResult(verdict="ZERO", violated_rules=self._dedupe(violated), trace_entries=trace)
            return self._build(proposal, final, ev, rt, rt_assessment)

        if not evidence_ok:
            trace.append("governor:hypothesis:invalid_or_missing_evidence")
            final = GovernanceResult(
                verdict="HYPOTHESIS",
                violated_rules=self._dedupe(violated),
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt, rt_assessment)

        if not rt_assessment.complete:
            trace.append("governor:hypothesis:incomplete_reverse_trace")
            final = GovernanceResult(
                verdict="HYPOTHESIS",
                violated_rules=self._dedupe(violated),
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt, rt_assessment)

        residual_specs = classify_residuals(self._dedupe(violated))
        if any(spec.blocks_certificate for spec in residual_specs):
            trace.append("governor:hypothesis:blocking_residuals")
            final = GovernanceResult(
                verdict="HYPOTHESIS",
                violated_rules=self._dedupe(violated),
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt, rt_assessment)

        trace.append("governor:certificate:all_gates_passed")
        final = GovernanceResult(verdict="CERTIFICATE", violated_rules=[], trace_entries=trace)
        return self._build(proposal, final, ev, rt, rt_assessment)

    @staticmethod
    def _gate_emptiness(proposal: Proposal) -> GovernanceResult | None:
        if not proposal.prompt or not proposal.prompt.strip():
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=["empty_proposal_text"],
                trace_entries=["governor:zero:empty_proposal"],
            )
        return None

    @staticmethod
    def _gate_contradiction(proposal: Proposal, evidence_ok: bool) -> GovernanceResult | None:
        text_lower = proposal.raw_text.lower()
        has_contradiction = any(kw.lower() in text_lower for kw in _CONTRADICTION_PATTERNS)
        if has_contradiction and not evidence_ok:
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=["contradiction_claim_without_evidence"],
                trace_entries=["governor:zero:contradiction_no_evidence"],
            )
        return None

    @staticmethod
    def _gate_nabhani(proposal: Proposal, evidence: list[Any]) -> GovernanceResult:
        metadata = dict(proposal.metadata or {})
        claim: dict[str, object] = {
            "target_reality": proposal.prompt or proposal.raw_text,
            "evidence": evidence if evidence else None,
            "sense_source": metadata.get("sense_source", "governed_external_source"),
            "prior_information": metadata.get("prior_information", ["governed_prior_information"]),
            "relation_chain": metadata.get("relation_chain", ["claim_to_evidence_relation"]),
            "correspondence_test": metadata.get("correspondence_test", {"matches_reality": True}),
            "certainty": metadata.get("certainty", {"score": 0.75}),
        }
        if isinstance(metadata.get("nabhani_claim"), dict):
            claim.update(metadata["nabhani_claim"])

        judgment = _rational_judge.judge(claim)
        trace_entries = [f"governor:nabhani:{judgment.status}"]

        if judgment.status == "rejected":
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=list(judgment.violated_axioms),
                trace_entries=trace_entries,
            )

        if judgment.status == "suspended":
            return GovernanceResult(
                verdict="HYPOTHESIS",
                violated_rules=["nabhani_rational_gate_suspended"],
                trace_entries=trace_entries,
            )

        return GovernanceResult(verdict="HYPOTHESIS", violated_rules=[], trace_entries=trace_entries)

    @staticmethod
    def _validate_evidence(evidence: list[Any]) -> tuple[bool, list[str]]:
        if not evidence:
            return False, ["evidence_missing_or_blank"]
        for item in evidence:
            if isinstance(item, str):
                if not item.strip():
                    return False, ["evidence_missing_or_blank"]
                continue
            if isinstance(item, dict):
                if not item:
                    return False, ["evidence_missing_or_blank"]
                continue
            return False, ["evidence_missing_or_blank"]
        return True, []

    @classmethod
    def _assess_reverse_trace(
        cls,
        reverse_trace: list[str] | dict[str, Any] | None,
    ) -> ReverseTraceAssessment:
        if reverse_trace is None:
            return ReverseTraceAssessment(
                trace_entries=[],
                complete=False,
                raw_text_units=[],
                residuals=["reverse_trace_missing"],
            )
        if isinstance(reverse_trace, dict):
            complete = bool(reverse_trace.get("complete", False))
            raw_units = [str(item).strip() for item in list(reverse_trace.get("raw_text_units", [])) if str(item).strip()]
            entries = [str(item).strip() for item in list(reverse_trace.get("trace", [])) if str(item).strip()]
            residuals: list[str] = []
            if not complete:
                residuals.append("certificate_without_reverse_trace")
            if not raw_units:
                residuals.append("reverse_trace_missing_raw_text")
                complete = False
            return ReverseTraceAssessment(
                trace_entries=entries,
                complete=complete,
                raw_text_units=raw_units,
                residuals=residuals,
            )
        entries = [str(item).strip() for item in list(reverse_trace) if str(item).strip()]
        if not entries:
            return ReverseTraceAssessment(
                trace_entries=[],
                complete=False,
                raw_text_units=[],
                residuals=["reverse_trace_missing"],
            )
        anchored_entries = [entry for entry in entries if any(marker in entry.lower() for marker in _RAW_TEXT_ANCHOR_MARKERS)]
        if not anchored_entries:
            return ReverseTraceAssessment(
                trace_entries=entries,
                complete=False,
                raw_text_units=[],
                residuals=["reverse_trace_missing_raw_text"],
            )
        return ReverseTraceAssessment(
            trace_entries=entries,
            complete=True,
            raw_text_units=anchored_entries,
            residuals=[],
        )

    @staticmethod
    def _proof_object_ref(proposal: Proposal) -> str:
        metadata = dict(proposal.metadata or {})
        for key in ("proof_object_ref", "proof_id"):
            value = metadata.get(key)
            if value and str(value).strip():
                return str(value).strip()
        return f"llm-proposer:{proposal.provider}:{proposal.model}"

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        return [item for item in dict.fromkeys(str(i).strip() for i in items) if item]

    def _build(
        self,
        proposal: Proposal,
        result: GovernanceResult,
        ev: list[Any],
        rt: list[str],
        rt_assessment: ReverseTraceAssessment,
    ) -> GovernedAnswer:
        answer = GovernedAnswer(
            proposal=proposal,
            verdict=result.verdict,
            evidence=ev,
            reverse_trace=result.trace_entries + rt,
            violated_rules=self._dedupe(result.violated_rules),
        )
        payload = to_governed_payload(
            answer,
            governance_gate_passed=result.verdict == "CERTIFICATE" and not has_blocking_residuals(answer.violated_rules),
            proof_object_ref=self._proof_object_ref(proposal),
            reverse_trace_obj={
                "complete": rt_assessment.complete,
                "raw_text_units": list(rt_assessment.raw_text_units),
                "trace": list(rt_assessment.trace_entries),
            },
        )
        return from_governed_payload(payload, proposal=proposal)
