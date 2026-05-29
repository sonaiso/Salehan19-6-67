"""Dal Transition Algebra (DTA) — Constitutional kernel for pre-meaning transitions.

DAL (Dalalah) layer governs transitions from linguistic carriers to isolated
lexical units WITHOUT producing meaning, ifadah, or hukm.

Constitutional law:
- No transition to meaning/ifadah/hukm is permitted.
- Every transition requires TransitionProof or is rejected/postponed.
- LafzMufrad is NOT meaning — it is a governed dal candidate preserving:
  * carriers
  * identity
  * rank
  * residuals
  * trace

This layer sits BEFORE semantic interpretation in the supreme architecture:
Reality → Cognitive Distinction → Linguistic Signification → [DAL] →
Conceptual Geometry → Direct Meaning → ...

Internal-only package. Not exported from mcd.__init__ unless explicitly
approved by constitutional review.
"""
from __future__ import annotations

DAL_CORE_VERSION = "1.0.0"

__all__ = [
    "DAL_CORE_VERSION",
]
