"""Governed Arabic ``QuantityMention`` extractor (Phase 3B-1).

The extractor is a *local* operator with a single typed transition
``PromptTextSpan / ArabicSpan -> QuantityMention``. It is intentionally
*narrow*: it discovers numeric or number-word spans inside a raw prompt,
binds each to a recognised unit when possible, anchors the result to the
raw prompt span, and emits typed residuals. It must never emit a final
judgment, certificate, feasibility verdict, or final answer.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Sequence

from mcd.core.public_schema import JUDGMENT_CERTIFICATE, JUDGMENT_HYPOTHESIS, JUDGMENT_ZERO
from mcd.fractal_learning.operator_contract import OperatorContract

QUANTITY_EXTRACTION_SCHEMA_VERSION = "1.0.0"
QUANTITY_EXTRACTION_CONTRACT_VERSION = "1.0.0"
QUANTITY_EXTRACTION_OPERATOR_ID = "quantity.extract.arabic_mention"

_SUPPORTED_SCHEMA_VERSIONS = frozenset({QUANTITY_EXTRACTION_SCHEMA_VERSION})

# --- Tokenization -----------------------------------------------------------
_ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"  # U+0660..U+0669
_EASTERN_ARABIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹"  # U+06F0..U+06F9 (Persian)
_DIGIT_TRANSLATION = {
    **{ord(c): str(i) for i, c in enumerate(_ARABIC_INDIC_DIGITS)},
    **{ord(c): str(i) for i, c in enumerate(_EASTERN_ARABIC_DIGITS)},
}

# Sub-token: digit run, Arabic word, single slash, or other punctuation.
_SUBTOKEN_RE = re.compile(
    r"[0-9\u0660-\u0669\u06F0-\u06F9]+(?:[\.,][0-9\u0660-\u0669\u06F0-\u06F9]+)?"
    r"|[\u0600-\u06FF]+"
    r"|/",
)

# --- Lexicons ---------------------------------------------------------------
_NUMBER_WORDS: dict[str, int] = {
    "صفر": 0,
    "واحد": 1, "واحدة": 1,
    "اثنان": 2, "اثنين": 2, "اثنتان": 2, "اثنتين": 2,
    "ثلاثة": 3, "ثلاث": 3,
    "أربعة": 4, "اربعة": 4, "أربع": 4, "اربع": 4,
    "خمسة": 5, "خمس": 5,
    "ستة": 6, "ست": 6,
    "سبعة": 7, "سبع": 7,
    "ثمانية": 8, "ثماني": 8,
    "تسعة": 9, "تسع": 9,
    "عشرة": 10, "عشر": 10,
}

# Unit aliases (single-token) → canonical normalized form.
_UNIT_ALIASES: dict[str, str] = {
    "كم": "km",
    "كيلو": "km",
    "كيلومتر": "km",
    "كلم": "km",
    "متر": "m",
    "أمتار": "m",
    "امتار": "m",
    "ميل": "mile",
    "أميال": "mile",
    "دقيقة": "minute",
    "دقائق": "minute",
    "د": "minute",
    "ثانية": "second",
    "ثواني": "second",
    "ث": "second",
    "ساعة": "hour",
    "ساعات": "hour",
    "س": "hour",
    "يوم": "day",
    "أيام": "day",
}

# Compound speed unit forms recognised as a single semantic unit.
# Each entry maps a *sequence of consecutive sub-tokens* (already normalized)
# to a canonical normalized unit.
_COMPOUND_UNIT_SEQUENCES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("كم", "/", "ساعة"), "km_per_hour"),
    (("كم", "بالساعة"), "km_per_hour"),
    (("كم", "في", "الساعة"), "km_per_hour"),
    (("كم", "في", "ساعة"), "km_per_hour"),
    (("كيلومتر", "/", "ساعة"), "km_per_hour"),
    (("كيلومتر", "بالساعة"), "km_per_hour"),
    (("كيلومتر", "في", "الساعة"), "km_per_hour"),
    (("متر", "/", "ثانية"), "m_per_second"),
    (("متر", "في", "الثانية"), "m_per_second"),
    (("متر", "بالثانية"), "m_per_second"),
)

# Tokens that signal a compound unit but are not themselves units. They are
# only meaningful when they appear inside a compound sequence above.
_COMPOUND_HELPER_TOKENS = frozenset({"بالساعة", "بالثانية", "في", "الساعة", "الثانية", "/"})

# Final-output guard set (mirrors operator_contract / composition rules).
_FORBIDDEN_OUTPUT_TYPES = frozenset(
    {"Judgment", "Certificate", "FinalAnswer", "ProjectConclusion", "GovernedJudgment"}
)

_PAYLOAD_KEYS = frozenset(
    {
        "quantity_extraction_schema_version",
        "quantity_extraction_contract_version",
        "operator_id",
        "raw_prompt",
        "quantity_mentions",
        "residuals",
        "rank",
    }
)


@dataclass(frozen=True)
class QuantityMention:
    """A single typed quantity mention extracted from an Arabic prompt."""

    raw_text: str
    value: float | int | None
    normalized_value: float | None
    unit_raw: str | None
    unit_normalized: str | None
    span_start: int
    span_end: int
    rank: str = JUDGMENT_HYPOTHESIS
    confidence: float = 0.0
    residuals: list[str] = field(default_factory=list)
    trace_anchor: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["residuals"] = list(self.residuals)
        data["trace_anchor"] = dict(self.trace_anchor)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuantityMention":
        return cls(
            raw_text=str(data.get("raw_text", "")),
            value=_coerce_value(data.get("value")),
            normalized_value=_coerce_normalized_value(data.get("normalized_value")),
            unit_raw=_coerce_optional_str(data.get("unit_raw")),
            unit_normalized=_coerce_optional_str(data.get("unit_normalized")),
            span_start=int(data.get("span_start", 0)),
            span_end=int(data.get("span_end", 0)),
            rank=_normalize_rank(data.get("rank")),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            residuals=[str(c) for c in (data.get("residuals") or []) if str(c).strip()],
            trace_anchor=dict(data.get("trace_anchor") or {}),
        )


# --- Public API -------------------------------------------------------------

def extract_quantity_mentions(prompt: str) -> list[QuantityMention]:
    """Extract every QuantityMention found in ``prompt``.

    This function MUST NOT compute feasibility, judgments, or final answers.
    It only returns typed mentions with hypothesis rank, each anchored to its
    raw prompt span and accompanied by any non-erasing residuals.
    """

    text = "" if prompt is None else str(prompt)
    if not text.strip():
        return []

    subtokens = _subtokenize(text)
    mentions: list[QuantityMention] = []
    index = 0
    while index < len(subtokens):
        token = subtokens[index]

        # Try number (digit or word) first; bind to following unit (compound aware).
        number_info = _as_number(token.text)
        if number_info is not None:
            value, normalized_value, number_residuals = number_info
            unit_consumed = _match_unit_after(subtokens, index + 1)
            if unit_consumed is not None:
                unit_raw, unit_normalized, end_index, unit_residuals = unit_consumed
                span_start = token.start
                span_end = subtokens[end_index].end
                mention = _build_mention(
                    raw_prompt=text,
                    raw_text=text[span_start:span_end],
                    value=value,
                    normalized_value=normalized_value,
                    unit_raw=unit_raw,
                    unit_normalized=unit_normalized,
                    span_start=span_start,
                    span_end=span_end,
                    residuals=number_residuals + unit_residuals,
                )
                mentions.append(mention)
                index = end_index + 1
                continue

            # Number with no recognised following unit.
            mention = _build_mention(
                raw_prompt=text,
                raw_text=token.text,
                value=value,
                normalized_value=normalized_value,
                unit_raw=None,
                unit_normalized=None,
                span_start=token.start,
                span_end=token.end,
                residuals=number_residuals + ["quantity_number_without_unit"],
            )
            mentions.append(mention)
            index += 1
            continue

        # Standalone unit (no preceding consumed number).
        unit_consumed = _match_unit_at(subtokens, index)
        if unit_consumed is not None:
            unit_raw, unit_normalized, end_index, unit_residuals = unit_consumed
            span_start = token.start
            span_end = subtokens[end_index].end
            mention = _build_mention(
                raw_prompt=text,
                raw_text=text[span_start:span_end],
                value=None,
                normalized_value=None,
                unit_raw=unit_raw,
                unit_normalized=unit_normalized,
                span_start=span_start,
                span_end=span_end,
                residuals=unit_residuals + ["quantity_unit_without_number"],
            )
            mentions.append(mention)
            index = end_index + 1
            continue

        index += 1

    return mentions


def build_quantity_extraction_operator_contract(
    *,
    operator_id: str = QUANTITY_EXTRACTION_OPERATOR_ID,
    rank: str = JUDGMENT_HYPOTHESIS,
) -> OperatorContract:
    """Return the Phase 3A ``OperatorContract`` describing this extractor.

    The contract is a single typed transition ``PromptTextSpan ->
    QuantityMention`` and refuses any rank above ``JUDGMENT_HYPOTHESIS``.
    """

    safe_rank = _normalize_rank(rank)
    if safe_rank == JUDGMENT_CERTIFICATE:
        # Phase 3B-1 is explicitly hypothesis-only. We refuse to silently
        # promote a quantitative extractor to certificate rank.
        safe_rank = JUDGMENT_HYPOTHESIS
    return OperatorContract(
        operator_id=operator_id,
        layer_from="PromptTextSpan",
        layer_to="QuantityMention",
        input_type="ArabicSpan",
        output_type="QuantityMention",
        missing_gate="quantity_extraction_gate",
        gates=["numeric_or_number_word_present", "unit_expression_present"],
        evidence_requirements=["span_trace_required"],
        residual_policy=[
            "quantity_number_without_unit",
            "quantity_unit_without_number",
            "quantity_unit_ambiguous",
            "quantity_word_number_unresolved",
            "quantity_span_trace_missing",
            "quantity_extraction_payload_invalid",
        ],
        forbidden_outputs=[
            "feasibility_judgment",
            "Judgment",
            "Certificate",
            "FinalAnswer",
            "ProjectConclusion",
        ],
        rank=safe_rank,
        reverse_trace_required=True,
        tests_required=["positive", "negative"],
    )


def build_quantity_extraction_payload(prompt: str) -> dict[str, Any]:
    """Build a governed payload bundling extracted mentions + residuals."""

    text = "" if prompt is None else str(prompt)
    mentions = extract_quantity_mentions(text)
    residuals: list[str] = []
    for mention in mentions:
        residuals.extend(mention.residuals)
    payload: dict[str, Any] = {
        "quantity_extraction_schema_version": QUANTITY_EXTRACTION_SCHEMA_VERSION,
        "quantity_extraction_contract_version": QUANTITY_EXTRACTION_CONTRACT_VERSION,
        "operator_id": QUANTITY_EXTRACTION_OPERATOR_ID,
        "raw_prompt": text,
        "quantity_mentions": [m.to_dict() for m in mentions],
        "residuals": list(dict.fromkeys(residuals)),
        "rank": JUDGMENT_HYPOTHESIS,
    }
    payload["residuals"] = validate_quantity_extraction_payload(payload)
    return payload


def validate_quantity_extraction_payload(payload: dict[str, Any]) -> list[str]:
    residuals: list[str] = []
    if not isinstance(payload, dict):
        return ["quantity_extraction_payload_invalid"]

    existing = payload.get("residuals")
    if isinstance(existing, list):
        residuals.extend(str(c) for c in existing if str(c).strip())

    schema_version = str(payload.get("quantity_extraction_schema_version", "")).strip()
    if not schema_version or schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
        residuals.append("quantity_extraction_payload_invalid")

    if not str(payload.get("operator_id", "")).strip():
        residuals.append("quantity_extraction_payload_invalid")

    raw_prompt = payload.get("raw_prompt")
    if not isinstance(raw_prompt, str):
        residuals.append("quantity_extraction_payload_invalid")

    mentions = payload.get("quantity_mentions")
    if not isinstance(mentions, list):
        residuals.append("quantity_extraction_payload_invalid")
    else:
        for mention in mentions:
            if not isinstance(mention, dict):
                residuals.append("quantity_extraction_payload_invalid")
                continue
            anchor = mention.get("trace_anchor")
            if not isinstance(anchor, dict) or not anchor:
                residuals.append("quantity_span_trace_missing")
            else:
                start = anchor.get("start")
                end = anchor.get("end")
                if not isinstance(start, int) or not isinstance(end, int) or end <= start:
                    residuals.append("quantity_span_trace_missing")

    rank = _normalize_rank(payload.get("rank"))
    if rank == JUDGMENT_CERTIFICATE:
        residuals.append("quantity_extraction_payload_invalid")

    return list(dict.fromkeys(residuals))


def serialize_quantity_extraction_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_quantity_extraction_payload(payload):
        return deepcopy(payload)
    out = deepcopy(payload)
    out.setdefault("quantity_extraction_schema_version", QUANTITY_EXTRACTION_SCHEMA_VERSION)
    out.setdefault("quantity_extraction_contract_version", QUANTITY_EXTRACTION_CONTRACT_VERSION)
    out["residuals"] = validate_quantity_extraction_payload(out)
    return json.loads(json.dumps(out, ensure_ascii=False, sort_keys=True))


def deserialize_quantity_extraction_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not _is_quantity_extraction_payload(payload):
        return deepcopy(payload)
    out = deepcopy(payload)
    out.setdefault("quantity_extraction_schema_version", QUANTITY_EXTRACTION_SCHEMA_VERSION)
    out.setdefault("quantity_extraction_contract_version", QUANTITY_EXTRACTION_CONTRACT_VERSION)
    incoming_rank = _normalize_rank(out.get("rank"))
    if incoming_rank == JUDGMENT_CERTIFICATE:
        out["rank"] = JUDGMENT_HYPOTHESIS
    out["residuals"] = validate_quantity_extraction_payload(out)
    return out


# --- Internals --------------------------------------------------------------

@dataclass(frozen=True)
class _SubToken:
    text: str
    start: int
    end: int


def _subtokenize(text: str) -> list[_SubToken]:
    tokens: list[_SubToken] = []
    for match in _SUBTOKEN_RE.finditer(text):
        tokens.append(_SubToken(text=match.group(0), start=match.start(), end=match.end()))
    return tokens


def _as_number(raw: str) -> tuple[float | int, float, list[str]] | None:
    if not raw:
        return None
    normalized = raw.translate(_DIGIT_TRANSLATION)
    if _is_numeric(normalized):
        try:
            if "." in normalized or "," in normalized:
                value: float | int = float(normalized.replace(",", "."))
            else:
                value = int(normalized)
        except ValueError:
            return None
        return value, float(value), []
    # Try Arabic number word.
    word = raw.strip()
    if word in _NUMBER_WORDS:
        value = _NUMBER_WORDS[word]
        return value, float(value), []
    # Heuristic: token looks like an Arabic word that *could* be a number
    # word we don't know. We do not emit a mention for it, but it does not
    # block extraction of other mentions either.
    return None


def _is_numeric(value: str) -> bool:
    if not value:
        return False
    core = value.replace(".", "", 1).replace(",", "", 1)
    return core.isdigit()


def _match_unit_after(
    subtokens: Sequence[_SubToken], start_index: int
) -> tuple[str, str, int, list[str]] | None:
    if start_index >= len(subtokens):
        return None
    return _match_unit_at(subtokens, start_index)


def _match_unit_at(
    subtokens: Sequence[_SubToken], start_index: int
) -> tuple[str, str, int, list[str]] | None:
    if start_index >= len(subtokens):
        return None

    # 1) Try the longest compound unit sequence first.
    for sequence, normalized in _COMPOUND_UNIT_SEQUENCES:
        end_index = start_index + len(sequence) - 1
        if end_index >= len(subtokens):
            continue
        actual = tuple(
            subtokens[start_index + offset].text for offset in range(len(sequence))
        )
        if actual == sequence:
            span_start = subtokens[start_index].start
            span_end = subtokens[end_index].end
            unit_raw = " ".join(actual) if "/" not in actual else "".join(actual)
            # Preserve the literal span from the prompt for unit_raw when
            # the tokens were contiguous (best fidelity for trace).
            literal = _literal_span(subtokens, start_index, end_index)
            if literal:
                unit_raw = literal
            return unit_raw, normalized, end_index, []

    # 2) Single-token alias.
    token = subtokens[start_index]
    alias = _UNIT_ALIASES.get(token.text)
    if alias is not None:
        residuals: list[str] = []
        # "كيلو" can also mean kilogram in some dialects; flag as ambiguous
        # alias so downstream normalization can decide.
        if token.text == "كيلو":
            residuals.append("quantity_unit_ambiguous")
        return token.text, alias, start_index, residuals

    # 3) Helper tokens by themselves are not units.
    if token.text in _COMPOUND_HELPER_TOKENS:
        return None

    return None


def _literal_span(subtokens: Sequence[_SubToken], start_index: int, end_index: int) -> str:
    if start_index > end_index or end_index >= len(subtokens):
        return ""
    parts: list[str] = []
    prev_end: int | None = None
    for offset in range(start_index, end_index + 1):
        token = subtokens[offset]
        if prev_end is not None and token.start > prev_end:
            parts.append(" ")
        parts.append(token.text)
        prev_end = token.end
    return "".join(parts)


def _build_mention(
    *,
    raw_prompt: str,
    raw_text: str,
    value: float | int | None,
    normalized_value: float | None,
    unit_raw: str | None,
    unit_normalized: str | None,
    span_start: int,
    span_end: int,
    residuals: Iterable[str],
) -> QuantityMention:
    deduped: list[str] = []
    for code in residuals:
        code = str(code).strip()
        if code and code not in deduped:
            deduped.append(code)
    anchor = {
        "label": "quantity_mention_span",
        "start": int(span_start),
        "end": int(span_end),
        "text": raw_prompt[span_start:span_end],
    }
    if not anchor["text"]:
        deduped.append("quantity_span_trace_missing")
    confidence = 0.7 if value is not None and unit_normalized is not None else 0.3
    return QuantityMention(
        raw_text=raw_text,
        value=value,
        normalized_value=normalized_value,
        unit_raw=unit_raw,
        unit_normalized=unit_normalized,
        span_start=int(span_start),
        span_end=int(span_end),
        rank=JUDGMENT_HYPOTHESIS,
        confidence=confidence,
        residuals=deduped,
        trace_anchor=anchor,
    )


def _normalize_rank(raw: Any) -> str:
    rank = str(raw or "").strip().lower()
    if rank in {JUDGMENT_ZERO, JUDGMENT_HYPOTHESIS, JUDGMENT_CERTIFICATE}:
        return rank
    return JUDGMENT_HYPOTHESIS


def _is_quantity_extraction_payload(payload: Any) -> bool:
    return isinstance(payload, dict) and bool(set(payload.keys()) & _PAYLOAD_KEYS)


def _coerce_value(raw: Any) -> float | int | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return int(raw)
    if isinstance(raw, (int, float)):
        return raw
    try:
        text = str(raw).strip()
        if not text:
            return None
        if "." in text or "," in text:
            return float(text.replace(",", "."))
        return int(text)
    except (TypeError, ValueError):
        return None


def _coerce_normalized_value(raw: Any) -> float | None:
    value = _coerce_value(raw)
    if value is None:
        return None
    return float(value)


def _coerce_optional_str(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None
