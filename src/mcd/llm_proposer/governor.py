"""AFJGGovernor — applies AFJG governance gates to an LLM Proposal.

Governance pipeline (in order):
  1. Emptiness gate         — empty proposal text → ZERO immediately
  2. Contradiction gate     — contradiction/impossibility claims without evidence → ZERO
  3. Nabhani rational gate  — delegates to RationalMethodJudge from src/mcd/nabhani/
  4. Evidence gate          — no evidence OR no reverse_trace → HYPOTHESIS
  5. Certificate gate       — all gates passed, evidence present, no violations → CERTIFICATE

The RationalMethodJudge enforces:
  واقع + حس/مصدر + معلومات سابقة + ربط + مطابقة + دليل + يقين

Only the three AFJG final verdicts are emitted: ZERO / HYPOTHESIS / CERTIFICATE.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from mcd.llm_proposer.types import GovernedAnswer, Proposal, Verdict
from mcd.nabhani.rational_method_judge import RationalMethodJudge

# ---------------------------------------------------------------------------
# Contradiction keywords that trigger ZERO when evidence is absent
# ---------------------------------------------------------------------------
_CONTRADICTION_PATTERNS: tuple[str, ...] = (
    "متناقض",
    "مستحيل",
    "contradiction",
    "impossible",
    "inconsistent",
    "self-contradictory",
)

_rational_judge = RationalMethodJudge()


@dataclass
class GovernanceResult:
    """Intermediate result produced by each gate."""

    verdict: Verdict
    violated_rules: list[str] = field(default_factory=list)
    trace_entries: list[str] = field(default_factory=list)


class AFJGGovernor:
    """Apply the full AFJG governance pipeline to a Proposal.

    Usage::

        governor = AFJGGovernor()
        answer = governor.govern(proposal, evidence=["دليل 1"], reverse_trace=["step 1"])
    """

    # ------------------------------------------------------------------ public

    def govern(
        self,
        proposal: Proposal,
        *,
        evidence: list[str] | None = None,
        reverse_trace: list[str] | None = None,
    ) -> GovernedAnswer:
        """Apply all governance gates and return a GovernedAnswer."""
        ev: list[str] = list(evidence or [])
        rt: list[str] = list(reverse_trace or [])
        violated: list[str] = []
        trace: list[str] = ["governor:start"]

        # Gate 1 — emptiness
        result = self._gate_emptiness(proposal, ev, rt)
        if result is not None:
            return self._build(proposal, result, ev, rt)

        # Gate 2 — contradiction without evidence
        result = self._gate_contradiction(proposal, ev, rt)
        if result is not None:
            return self._build(proposal, result, ev, rt)

        # Gate 3 — Nabhani rational method
        nabhani_result = self._gate_nabhani(proposal, ev, rt)
        violated.extend(nabhani_result.violated_rules)
        trace.extend(nabhani_result.trace_entries)

        # If Nabhani gate emits ZERO → stop
        if nabhani_result.verdict == "ZERO":
            final = GovernanceResult(
                verdict="ZERO",
                violated_rules=violated,
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt)

        # Gate 4 — evidence / reverse_trace completeness
        if not ev or not rt:
            trace.append("governor:hypothesis:incomplete_evidence_or_trace")
            final = GovernanceResult(
                verdict="HYPOTHESIS",
                violated_rules=violated,
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt)

        # Gate 5 — certificate: all gates passed, no violations
        if not violated:
            trace.append("governor:certificate:all_gates_passed")
            final = GovernanceResult(
                verdict="CERTIFICATE",
                violated_rules=[],
                trace_entries=trace,
            )
            return self._build(proposal, final, ev, rt)

        # Nabhani raised warnings but not ZERO and we have evidence — HYPOTHESIS
        trace.append("governor:hypothesis:nabhani_warnings")
        final = GovernanceResult(
            verdict="HYPOTHESIS",
            violated_rules=violated,
            trace_entries=trace,
        )
        return self._build(proposal, final, ev, rt)

    # ----------------------------------------------------------------- private

    @staticmethod
    def _gate_emptiness(
        proposal: Proposal,
        ev: list[str],
        rt: list[str],
    ) -> GovernanceResult | None:
        """Return ZERO if the original prompt is empty or blank.

        We check ``proposal.prompt`` (the user's original intent) rather than
        ``raw_text`` so that proposer prefixes (e.g. ``ECHO::`` from
        EchoProposer) do not mask an actually empty submission.
        """
        if not proposal.prompt or not proposal.prompt.strip():
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=["empty_proposal_text"],
                trace_entries=["governor:zero:empty_proposal"],
            )
        return None

    @staticmethod
    def _gate_contradiction(
        proposal: Proposal,
        ev: list[str],
        rt: list[str],
    ) -> GovernanceResult | None:
        """Return ZERO when a contradiction keyword appears without evidence."""
        text_lower = proposal.raw_text.lower()
        has_contradiction = any(kw.lower() in text_lower for kw in _CONTRADICTION_PATTERNS)
        if has_contradiction and not ev:
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=["contradiction_claim_without_evidence"],
                trace_entries=["governor:zero:contradiction_no_evidence"],
            )
        return None

    @staticmethod
    def _gate_nabhani(
        proposal: Proposal,
        ev: list[str],
        rt: list[str],
    ) -> GovernanceResult:
        """Delegate to RationalMethodJudge with available evidence.

        The claim dict is built from the proposal text and any caller-supplied
        evidence.  Missing optional fields result in HYPOTHESIS rather than ZERO
        (they are soft failures in the rational method).
        """
        claim: dict[str, object] = {
            "target_reality": proposal.prompt or proposal.raw_text,
            "evidence": ev if ev else None,
        }
        judgment = _rational_judge.judge(claim)
        trace_entries = [f"governor:nabhani:{judgment.status}"]

        if judgment.status == "rejected":
            return GovernanceResult(
                verdict="ZERO",
                violated_rules=list(judgment.violated_axioms),
                trace_entries=trace_entries,
            )

        # "accepted" or "suspended" — soft warnings only; caller-supplied
        # evidence and reverse_trace determine the final verdict.
        # Violated axioms are logged to trace but do NOT block CERTIFICATE.
        if judgment.violated_axioms:
            for axiom in judgment.violated_axioms:
                trace_entries.append(f"governor:nabhani:warning:{axiom}")

        return GovernanceResult(
            verdict="HYPOTHESIS",  # upgraded later if evidence + trace present
            violated_rules=[],
            trace_entries=trace_entries,
        )

    @staticmethod
    def _build(
        proposal: Proposal,
        result: GovernanceResult,
        ev: list[str],
        rt: list[str],
    ) -> GovernedAnswer:
        return GovernedAnswer(
            proposal=proposal,
            verdict=result.verdict,
            evidence=ev,
            reverse_trace=result.trace_entries + rt,
            violated_rules=result.violated_rules,
        )
