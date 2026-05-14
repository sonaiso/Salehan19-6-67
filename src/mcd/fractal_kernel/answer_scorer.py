"""AnswerScorer — 7-dimensional weighted certainty gate.

Implements the canonical AnswerScore formula from the Bayani Knowledge System
base theory:

    AnswerScore =
        0.25 × RealityMatch
      + 0.20 × LinguisticCoherence
      + 0.20 × EvidenceStrength
      + 0.15 × SemanticValidity
      + 0.10 × InferenceValidity
      + 0.10 × CertaintyClarity
      − 0.30 × HallucinationRisk          ← dominant penalty

    Minimum score to permit output:  AnswerScore >= 0.60

The HallucinationRisk weight (0.30) is deliberately the largest single factor
so that an otherwise high-scoring answer is blocked when LLM contamination is
suspected.  This is the primary guard against GPT proposals being mistaken for
verified knowledge.

Design constraints (from the base theory):
  - Scores are always in [0, 1].
  - The formula can produce a negative intermediate value; it is clamped to 0.
  - Only three verdicts are possible: CERTIFICATE, HYPOTHESIS, ZERO.
    CERTIFICATE requires score >= 0.75 AND hallucination_risk == 0.0.
    HYPOTHESIS  requires score >= 0.60.
    ZERO        is everything below 0.60 or any hard blocker.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from mcd.core.measures import clamp


# ── Weights ───────────────────────────────────────────────────────────────────

WEIGHTS: dict[str, float] = {
    "reality_match":        0.25,
    "linguistic_coherence": 0.20,
    "evidence_strength":    0.20,
    "semantic_validity":    0.15,
    "inference_validity":   0.10,
    "certainty_clarity":    0.10,
    "hallucination_risk":  -0.30,   # penalty — negative weight
}

# Output thresholds
CERTIFICATE_THRESHOLD = 0.75
HYPOTHESIS_THRESHOLD  = 0.60


# ── Output enum ───────────────────────────────────────────────────────────────

class AnswerVerdict(str, Enum):
    CERTIFICATE = "certificate"   # شهادة — proven
    HYPOTHESIS  = "hypothesis"    # فرضية — plausible but unproven
    ZERO        = "zero"          # صفر  — blocked


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class AnswerScore:
    """Full scoring result with per-dimension breakdown and final verdict."""

    # Input dimensions
    reality_match:        float = 0.5
    linguistic_coherence: float = 0.5
    evidence_strength:    float = 0.0
    semantic_validity:    float = 0.5
    inference_validity:   float = 0.5
    certainty_clarity:    float = 0.5
    hallucination_risk:   float = 0.0

    # Computed outputs (filled by AnswerScorer.score())
    raw_score:   float = 0.0
    final_score: float = 0.0
    verdict:     AnswerVerdict = AnswerVerdict.ZERO
    blockers:    list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "dimensions": {
                "reality_match":        self.reality_match,
                "linguistic_coherence": self.linguistic_coherence,
                "evidence_strength":    self.evidence_strength,
                "semantic_validity":    self.semantic_validity,
                "inference_validity":   self.inference_validity,
                "certainty_clarity":    self.certainty_clarity,
                "hallucination_risk":   self.hallucination_risk,
            },
            "weights": WEIGHTS,
            "raw_score":   round(self.raw_score, 4),
            "final_score": round(self.final_score, 4),
            "verdict":     self.verdict.value,
            "blockers":    self.blockers,
            "explanation": self.explanation,
        }


# ── Scorer ────────────────────────────────────────────────────────────────────

class AnswerScorer:
    """Computes the canonical 7-dimension AnswerScore and issues a verdict.

    Usage::

        scorer = AnswerScorer()
        result = scorer.score(
            reality_match=0.85,
            linguistic_coherence=0.90,
            evidence_strength=0.70,
            semantic_validity=0.80,
            inference_validity=0.75,
            certainty_clarity=0.80,
            hallucination_risk=0.10,
        )
        # result.verdict => AnswerVerdict.CERTIFICATE | HYPOTHESIS | ZERO
    """

    def score(
        self,
        reality_match:        float = 0.5,
        linguistic_coherence: float = 0.5,
        evidence_strength:    float = 0.0,
        semantic_validity:    float = 0.5,
        inference_validity:   float = 0.5,
        certainty_clarity:    float = 0.5,
        hallucination_risk:   float = 0.0,
        extra_blockers:       Optional[list[str]] = None,
    ) -> AnswerScore:
        """Compute the AnswerScore and return a fully populated result object.

        All input dimensions are floats in [0, 1].
        hallucination_risk is a penalty: 0.0 = no risk, 1.0 = maximum risk.
        """
        blockers: list[str] = list(extra_blockers or [])

        # ── Validate inputs ────────────────────────────────────────────────
        dims = {
            "reality_match":        reality_match,
            "linguistic_coherence": linguistic_coherence,
            "evidence_strength":    evidence_strength,
            "semantic_validity":    semantic_validity,
            "inference_validity":   inference_validity,
            "certainty_clarity":    certainty_clarity,
            "hallucination_risk":   hallucination_risk,
        }
        for name, val in dims.items():
            if not (0.0 <= val <= 1.0):
                blockers.append(f"DIMENSION_OUT_OF_RANGE: {name}={val}")

        # ── Formula ────────────────────────────────────────────────────────
        raw = (
            reality_match        * WEIGHTS["reality_match"]
          + linguistic_coherence * WEIGHTS["linguistic_coherence"]
          + evidence_strength    * WEIGHTS["evidence_strength"]
          + semantic_validity    * WEIGHTS["semantic_validity"]
          + inference_validity   * WEIGHTS["inference_validity"]
          + certainty_clarity    * WEIGHTS["certainty_clarity"]
          + hallucination_risk   * WEIGHTS["hallucination_risk"]   # weight is negative
        )
        final = clamp(raw)

        # ── Hard blockers ──────────────────────────────────────────────────
        # Zero evidence always blocks Certificate regardless of other scores.
        if evidence_strength == 0.0:
            blockers.append("ZERO_EVIDENCE: evidence_strength=0.0 blocks Certificate")

        # High hallucination risk is a categorical block — it prevents any
        # positive output regardless of what other dimensions score.  This is
        # the primary anti-hallucination guard (>= 0.5 is considered high risk;
        # the penalty weight alone cannot drive the score below 0.60 at this
        # level, so an explicit block is required to honour the theory).
        if hallucination_risk >= 0.50:
            blockers.append(
                f"HIGH_HALLUCINATION: hallucination_risk={hallucination_risk:.2f} >= 0.50 "
                "blocks all positive output"
            )

        # ── Verdict ────────────────────────────────────────────────────────
        has_hard_block = any(
            "DIMENSION_OUT_OF_RANGE" in b
            or "HIGH_HALLUCINATION" in b
            or "ZERO_EVIDENCE" in b
            for b in blockers
        )

        if has_hard_block:
            verdict = AnswerVerdict.ZERO
        elif final >= CERTIFICATE_THRESHOLD and hallucination_risk == 0.0 and evidence_strength > 0.0:
            verdict = AnswerVerdict.CERTIFICATE
        elif final >= HYPOTHESIS_THRESHOLD and evidence_strength > 0.0:
            verdict = AnswerVerdict.HYPOTHESIS
        else:
            verdict = AnswerVerdict.ZERO

        # ── Explanation ────────────────────────────────────────────────────
        parts = [f"score={final:.3f}", f"verdict={verdict.value}"]
        if hallucination_risk > 0.0:
            penalty = hallucination_risk * abs(WEIGHTS["hallucination_risk"])
            parts.append(f"hallucination_penalty=-{penalty:.3f}")
        if blockers:
            parts.append(f"blockers={len(blockers)}")
        explanation = " | ".join(parts)

        return AnswerScore(
            reality_match        = reality_match,
            linguistic_coherence = linguistic_coherence,
            evidence_strength    = evidence_strength,
            semantic_validity    = semantic_validity,
            inference_validity   = inference_validity,
            certainty_clarity    = certainty_clarity,
            hallucination_risk   = hallucination_risk,
            raw_score            = raw,
            final_score          = final,
            verdict              = verdict,
            blockers             = blockers,
            explanation          = explanation,
        )

    def score_from_nerl_output(self, nerl_result: dict) -> AnswerScore:
        """Convenience: derive the 7 dimensions from a NabhaniDecoder output dict.

        Maps NERL pipeline fields to AnswerScore dimensions:
          reality_match        ← mcd_analysis certainty score
          linguistic_coherence ← domain.can_reason_without_revelation (proxy)
          evidence_strength    ← rational_judgment evidence_strength
          semantic_validity    ← dal_madlul grounding_status ratio
          inference_validity   ← rational_judgment.status score
          certainty_clarity    ← certainty_score directly
          hallucination_risk   ← fake_evidence.risk_score
        """
        mcd = nerl_result.get("mcd_analysis", {})
        mcd_certainty: float = float(nerl_result.get("certainty_score", 0.5))

        domain = nerl_result.get("domain", {})
        can_reason: bool = domain.get("can_reason_without_revelation", True)
        linguistic_coherence = 0.85 if can_reason else 0.40

        rational = nerl_result.get("rational_judgment", {})
        evidence_strength: float = float(rational.get("evidence_strength", 0.0))
        rational_status: str = rational.get("status", "unknown")
        inference_validity = (
            1.0 if rational_status == "accepted"
            else 0.5 if rational_status == "probable"
            else 0.2
        )

        # Semantic validity: fraction of dal-madlul entries that are grounded
        dal_list: list = nerl_result.get("dal_madlul", [])
        if dal_list:
            grounded = sum(
                1 for d in dal_list if d.get("grounding_status") == "grounded"
            )
            semantic_validity = grounded / len(dal_list)
        else:
            semantic_validity = mcd_certainty  # fallback to overall score

        fake = nerl_result.get("fake_evidence", {})
        hallucination_risk: float = float(fake.get("risk_score", 0.0))

        extra_blockers: list[str] = []
        if nerl_result.get("epistemic_status") in ("rejected", "suspended"):
            extra_blockers.append(
                f"NERL_STATUS_BLOCKER: epistemic_status={nerl_result['epistemic_status']}"
            )

        return self.score(
            reality_match        = mcd_certainty,
            linguistic_coherence = linguistic_coherence,
            evidence_strength    = evidence_strength,
            semantic_validity    = semantic_validity,
            inference_validity   = inference_validity,
            certainty_clarity    = mcd_certainty,
            hallucination_risk   = hallucination_risk,
            extra_blockers       = extra_blockers,
        )
