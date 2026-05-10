"""Runtime ZeroGuard for blocking invalid product-equivalence claims."""

from __future__ import annotations

import re

from bayani.runtime.contracts import ZeroResult


_BLOCKING_PATTERNS = (
    # Patterns are lowercase because input text is normalized with casefold().
    r"يحاكي\s*gpt(?:[-\s]?\d+(?:\.\d+)*)?\s*بالكامل",
    r"بديل\s*gpt",
    r"(?:مكافئ|مكافي)\s*(?:ل|لـ)\s*gpt(?:[-\s]?\d+(?:\.\d+)*)?",
    r"نموذج\s+لغوي\s+عام\s+كامل",
    r"general\s+llm\s+equivalent",
    r"full\s+gpt(?:[-\s]?\d+(?:\.\d+)*)?\s+equivalent",
)


def detect_blocking_product_claim(text: str) -> ZeroResult | None:
    """Return a blocking ZeroResult when text claims full GPT/LLM equivalence."""
    normalized = text.casefold()
    if not any(re.search(pattern, normalized) for pattern in _BLOCKING_PATTERNS):
        return None

    return ZeroResult(
        zero_type="NoGeneralLLMEquivalenceClaim",
        severity="BLOCKING",
        required_layer="ZeroGuard",
        claim=text,
        reason=(
            "دعوى مكافئة نموذج لغوي عام غير صحيحة في المرحلة الحالية؛ "
            "المشروع طبقة تحقق معرفية فوق النماذج وليس نموذجًا عامًا مكافئًا."
        ),
        allowed_reframe="Bayani is an Arabic epistemic verifier layer for LLM outputs.",
        blocks=[
            "FullLLMEquivalenceCertificate",
            "GeneralModelEquivalenceClaim",
        ],
    )
