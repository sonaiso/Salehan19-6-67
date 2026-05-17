"""Mapping helpers between llm_proposer verdicts and public judgments."""
from __future__ import annotations

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO

VERDICT_ZERO = "ZERO"
VERDICT_HYPOTHESIS = "HYPOTHESIS"
VERDICT_CERTIFICATE = "CERTIFICATE"

VERDICT_TO_PUBLIC_JUDGMENT: dict[str, str] = {
    VERDICT_ZERO: JUDGMENT_ZERO,
    VERDICT_HYPOTHESIS: JUDGMENT_HYPOTHESIS,
    VERDICT_CERTIFICATE: JUDGMENT_CERTIFICATE,
}

PUBLIC_JUDGMENT_TO_VERDICT: dict[str, str] = {
    JUDGMENT_ZERO: VERDICT_ZERO,
    JUDGMENT_HYPOTHESIS: VERDICT_HYPOTHESIS,
    JUDGMENT_CERTIFICATE: VERDICT_CERTIFICATE,
}


def verdict_to_public_judgment(verdict: str) -> str:
    try:
        return VERDICT_TO_PUBLIC_JUDGMENT[verdict]
    except KeyError as exc:
        raise ValueError(f"Unknown llm_proposer verdict: {verdict!r}") from exc


def public_judgment_to_verdict(judgment: str) -> str:
    normalized = str(judgment or "").strip().lower()
    try:
        return PUBLIC_JUDGMENT_TO_VERDICT[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown public judgment: {judgment!r}") from exc
