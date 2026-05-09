"""MultiDimensionalCertaintyScorer — nine-dimensional epistemic certainty.

The certainty formula from the Nabhani-grounded specification:

    Certainty =
        w1 * unicode_integrity
      + w2 * morphological_fit
      + w3 * syntactic_fit
      + w4 * semantic_fit
      + w5 * context_fit
      + w6 * evidence_strength
      + w7 * reality_match
      - w8 * ambiguity_penalty
      - w9 * contradiction_penalty

Each dimension is a float in [0, 1].  The composite score is also clamped
to [0, 1] after weighting.

The scorer also converts numeric scores to the Nabhani epistemic scale:

    0.00 – 0.15  → لفظ بلا واقع        (word without reality)
    0.15 – 0.30  → إحساس بلا تفسير     (sensation without interpretation)
    0.30 – 0.45  → معلومة بلا تحقق     (unverified information)
    0.45 – 0.55  → ربط أولي            (initial linking)
    0.55 – 0.65  → فكر محتمل           (probable thought)
    0.65 – 0.75  → معرفة راجحة         (probable knowledge)
    0.75 – 0.85  → معرفة صحيحة         (correct knowledge)
    0.85 – 0.93  → يقين                (certainty)
    0.93 – 0.98  → يقين صار مقياسًا    (certainty become standard)
    0.98 – 1.00  → مقياس صار سلوكًا    (standard become behaviour)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Default weights (sum of positive weights = 1.0)
# ---------------------------------------------------------------------------

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "unicode_integrity":       0.05,   # w1
    "morphological_fit":       0.18,   # w2
    "syntactic_fit":           0.17,   # w3
    "semantic_fit":            0.20,   # w4
    "context_fit":             0.15,   # w5
    "evidence_strength":       0.15,   # w6
    "reality_match":           0.10,   # w7
    "ambiguity_penalty":       0.12,   # w8  (subtracted)
    "contradiction_penalty":   0.18,   # w9  (subtracted)
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class CertaintyResult:
    """Nine-dimensional certainty evaluation for one epistemic claim."""

    claim: str
    """The claim / concept being evaluated."""

    # --- Positive dimensions (higher = better) ---
    unicode_integrity: float = 1.0
    morphological_fit: float = 0.0
    syntactic_fit: float = 0.0
    semantic_fit: float = 0.0
    context_fit: float = 0.0
    evidence_strength: float = 0.0
    reality_match: float = 0.0

    # --- Penalty dimensions (higher = worse) ---
    ambiguity_penalty: float = 0.0
    contradiction_penalty: float = 0.0

    # --- Computed ---
    final_certainty: float = field(init=False, default=0.0)
    status: str = field(init=False, default="unknown")
    label_ar: str = field(init=False, default="")

    # Weights used (copied from default, can be overridden)
    weights: Dict[str, float] = field(default_factory=lambda: dict(_DEFAULT_WEIGHTS))

    def __post_init__(self) -> None:
        self.compute()

    def compute(self) -> float:
        """Recompute :attr:`final_certainty` from current dimension values."""
        w = self.weights
        score = (
            w["unicode_integrity"]     * self.unicode_integrity
            + w["morphological_fit"]   * self.morphological_fit
            + w["syntactic_fit"]       * self.syntactic_fit
            + w["semantic_fit"]        * self.semantic_fit
            + w["context_fit"]         * self.context_fit
            + w["evidence_strength"]   * self.evidence_strength
            + w["reality_match"]       * self.reality_match
            - w["ambiguity_penalty"]   * self.ambiguity_penalty
            - w["contradiction_penalty"] * self.contradiction_penalty
        )
        self.final_certainty = round(max(0.0, min(1.0, score)), 4)
        self._update_status()
        return self.final_certainty

    def _update_status(self) -> None:
        s = self.final_certainty
        if s < 0.15:
            self.status, self.label_ar = "no_reality",          "لفظ بلا واقع"
        elif s < 0.30:
            self.status, self.label_ar = "sensation",           "إحساس بلا تفسير"
        elif s < 0.45:
            self.status, self.label_ar = "unverified",          "معلومة بلا تحقق"
        elif s < 0.55:
            self.status, self.label_ar = "initial_link",        "ربط أولي"
        elif s < 0.65:
            self.status, self.label_ar = "probable_thought",    "فكر محتمل"
        elif s < 0.75:
            self.status, self.label_ar = "probable_knowledge",  "معرفة راجحة"
        elif s < 0.85:
            self.status, self.label_ar = "correct_knowledge",   "معرفة صحيحة"
        elif s < 0.93:
            self.status, self.label_ar = "certainty",           "يقين"
        elif s < 0.98:
            self.status, self.label_ar = "strong_certainty",    "يقين صار مقياسًا"
        else:
            self.status, self.label_ar = "behavioural_norm",    "مقياس صار سلوكًا"

    def passes_threshold(self, threshold: float = 0.60) -> bool:
        """Return True if :attr:`final_certainty` ≥ *threshold*."""
        return self.final_certainty >= threshold

    def to_dict(self) -> Dict[str, object]:
        """Serialise to a JSON-compatible dict."""
        return {
            "claim": self.claim,
            "scores": {
                "unicode_integrity":    self.unicode_integrity,
                "morphological_fit":    self.morphological_fit,
                "syntactic_fit":        self.syntactic_fit,
                "semantic_fit":         self.semantic_fit,
                "context_fit":          self.context_fit,
                "evidence_strength":    self.evidence_strength,
                "reality_match":        self.reality_match,
                "ambiguity_penalty":    self.ambiguity_penalty,
                "contradiction_penalty": self.contradiction_penalty,
            },
            "final_certainty": self.final_certainty,
            "status": self.status,
            "label_ar": self.label_ar,
        }


# ---------------------------------------------------------------------------
# Scorer class
# ---------------------------------------------------------------------------

class MultiDimensionalCertaintyScorer:
    """Compute nine-dimensional certainty scores for epistemic claims.

    Usage::

        scorer = MultiDimensionalCertaintyScorer()
        result = scorer.score(
            claim="الطالب فاعل فعل الكتابة",
            morphological_fit=0.88,
            syntactic_fit=0.91,
            semantic_fit=0.82,
            context_fit=0.76,
            evidence_strength=0.85,
            reality_match=0.80,
        )
        print(result.final_certainty)   # → ~0.84
        print(result.label_ar)          # → معرفة صحيحة
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        self.weights = weights or dict(_DEFAULT_WEIGHTS)

    def score(
        self,
        claim: str,
        *,
        unicode_integrity: float = 1.0,
        morphological_fit: float = 0.0,
        syntactic_fit: float = 0.0,
        semantic_fit: float = 0.0,
        context_fit: float = 0.0,
        evidence_strength: float = 0.0,
        reality_match: float = 0.0,
        ambiguity_penalty: float = 0.0,
        contradiction_penalty: float = 0.0,
    ) -> CertaintyResult:
        """Compute and return a :class:`CertaintyResult` for *claim*."""
        result = CertaintyResult(
            claim=claim,
            unicode_integrity=unicode_integrity,
            morphological_fit=morphological_fit,
            syntactic_fit=syntactic_fit,
            semantic_fit=semantic_fit,
            context_fit=context_fit,
            evidence_strength=evidence_strength,
            reality_match=reality_match,
            ambiguity_penalty=ambiguity_penalty,
            contradiction_penalty=contradiction_penalty,
            weights=dict(self.weights),
        )
        # __post_init__ calls compute(), but we call it again to be explicit
        result.compute()
        return result

    def score_morphological_claim(
        self,
        claim: str,
        root_cert: float,
        pattern_cert: float,
        context_evidence: float = 0.5,
    ) -> CertaintyResult:
        """Convenience method for morphological analysis claims."""
        return self.score(
            claim=claim,
            unicode_integrity=1.0,
            morphological_fit=root_cert * 0.6 + pattern_cert * 0.4,
            syntactic_fit=context_evidence * 0.8,
            semantic_fit=root_cert * 0.5,
            context_fit=context_evidence,
            evidence_strength=pattern_cert,
            reality_match=root_cert * 0.4,
            ambiguity_penalty=max(0.0, 0.5 - pattern_cert),
            contradiction_penalty=0.0,
        )
