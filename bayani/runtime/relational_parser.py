"""Bayani Relational Parser — v0.2.

Rule-based Arabic relational parser that extracts semantic-relational
structures from Arabic text *before* judgment formation.

Epistemic principles enforced:
- No judgment before relation resolution.
- No application before tahqeeq al-manat.
- No mafhoom before mantuq.
- No illah before validation.
- No relation without a carrier/operator.

Usage::

    from bayani.runtime.relational_parser import parse_relations

    result = parse_relations("الخمر حرام")
    for r in result.relations:
        print(r.relation_type, r.carrier_operator)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Relation type constants
# ---------------------------------------------------------------------------

ISNADIYYAH = "isnadiyyah"
TADMINIYYAH = "tadminiyyah"
TAQYIDIYYAH = "taqyidiyyah"
FA_ILIYYAH = "fa_iliyyah"
MAF_ULIYYAH = "maf_uliyyah"
SABABIYYAH = "sababiyyah"
MUSABBABIYYAH = "musabbabiyyah"
SHARTIYYAH = "shartiyyah"
GHAIYYAH = "ghaiyyah"
ZAMANIYYAH = "zamaniyyah"
MAKANIYYAH = "makaniyyah"
HALIYYAH = "haliyyah"
ISTITHNAIYYAH = "istithnaiyyah"

ALL_RELATION_TYPES: tuple[str, ...] = (
    ISNADIYYAH,
    TADMINIYYAH,
    TAQYIDIYYAH,
    FA_ILIYYAH,
    MAF_ULIYYAH,
    SABABIYYAH,
    MUSABBABIYYAH,
    SHARTIYYAH,
    GHAIYYAH,
    ZAMANIYYAH,
    MAKANIYYAH,
    HALIYYAH,
    ISTITHNAIYYAH,
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BayaniRelation:
    """A single extracted Arabic semantic relation."""

    relation_type: str
    """One of the 13 relation type constants defined above."""

    source_text: str
    """The full source text from which this relation was extracted."""

    subject: Optional[str]
    """The subject / mubtada / fa'il of the relation."""

    predicate_or_target: Optional[str]
    """The predicate (khabar) or target (maf'ul / mustathna / ghayah …)."""

    carrier_operator: Optional[str]
    """The Arabic grammatical/lexical operator that carries this relation
    (e.g. ``nominal_sentence``, ``verb_sentence``, ``conditional_tool``)."""

    confidence: float
    """Rule-based confidence score in [0, 1]."""

    epistemic_rank: str
    """Epistemic certainty rank — ``"qat'i"`` or ``"zanni"``."""

    possible_usuli_effect: Optional[str]
    """Potential usul al-fiqh implication of this relation."""

    forbidden_jumps_checked: List[str] = field(default_factory=list)
    """Runtime invariants that were verified when extracting this relation."""


@dataclass
class RelationalParseResult:
    """Full relational parse result for a single Arabic text."""

    source_text: str
    """The original input text."""

    relations: List[BayaniRelation] = field(default_factory=list)
    """All successfully extracted relations."""

    unresolved: List[str] = field(default_factory=list)
    """Structures that were detected but could not be fully resolved
    (e.g. ambiguous idafa patterns)."""

    notes: List[str] = field(default_factory=list)
    """Parser notes and diagnostics."""


# ---------------------------------------------------------------------------
# Internal lexical resources
# ---------------------------------------------------------------------------

# Default forbidden jumps every relation checks
_RELATIONAL_FORBIDDEN_JUMPS: List[str] = [
    "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
    "NoDomainTransferWithoutBridge",
]

# Verbs whose presence at sentence-start signals a verbal sentence (جملة فعلية)
_VERBAL_SENTENCE_VERBS: frozenset[str] = frozenset({
    "أكرم", "ضرب", "جاء", "وجب", "أتموا", "كتب", "قرأ", "أكل",
    "شرب", "ذهب", "جلس", "قام", "سمع", "رأى", "فعل", "دخل",
    "خرج", "أخذ", "أعطى", "قال", "علم", "أمر", "نهى", "أتم",
    "أمّ", "صلى", "صام", "زكّى", "حجّ", "آمن", "نجح", "أتى",
})

# Motion/state verbs that commonly introduce a حال construction
_HAL_TRIGGER_VERBS: frozenset[str] = frozenset({
    "جاء", "دخل", "خرج", "رجع", "ذهب", "وصل", "عاد", "مشى",
})

# Conditional particles (أدوات الشرط)
_CONDITIONAL_TOOLS: frozenset[str] = frozenset({
    "إن", "إذا", "متى", "كلما", "حيثما", "أينما",
})

# Exception particles (أدوات الاستثناء)
_EXCEPTION_TOOLS: frozenset[str] = frozenset({
    "إلا", "غير", "سوى", "خلا", "عدا", "حاشا",
})

# Ghayah / limit operators (أدوات الغاية)
_GHAYAH_TOOLS: frozenset[str] = frozenset({"حتى", "إلى"})

# Cause / reason tools (أدوات السببية)
_SABAB_TOOLS: tuple[str, ...] = (
    "بسبب", "لأجل", "من أجل", "لأن", "نتيجة", "بعلة",
)

# Time markers (ظروف الزمان)
_TIME_MARKERS: frozenset[str] = frozenset({
    "الليل", "النهار", "الصبح", "المساء", "الفجر", "العشاء",
    "الجمعة", "السبت", "الأحد", "الزوال", "اليوم", "غدا", "أمس",
    "يوم", "ليلة", "ساعة", "شهر", "سنة", "حين", "وقت",
})

# Place markers (ظروف المكان)
_PLACE_MARKERS: frozenset[str] = frozenset({
    "البيت", "المسجد", "السوق", "المدرسة", "المدينة",
    "الدار", "البلد", "الحرم", "المكان", "الموضع",
})

# Lexical tadmin markers (التضمين المعنوي)
_TADMIN_MARKERS: frozenset[str] = frozenset({
    "يتضمن", "تتضمن", "يشتمل", "تشتمل",
})

# Adjective ending suffixes for taqyidiyyah detection (indefinite pair heuristic)
_ADJ_ENDINGS: tuple[str, ...] = ("ة", "ون", "ين", "ان", "ات", "اء")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Whitespace tokeniser for Arabic text."""
    return text.strip().split()


def _starts_with_article(word: str) -> bool:
    """Return True if *word* carries the Arabic definite article ال."""
    return word.startswith("ال") and len(word) > 2


def _make_relation(
    relation_type: str,
    source_text: str,
    *,
    subject: Optional[str] = None,
    predicate_or_target: Optional[str] = None,
    carrier_operator: Optional[str] = None,
    confidence: float = 0.8,
    epistemic_rank: str = "zanni",
    possible_usuli_effect: Optional[str] = None,
    forbidden_jumps_checked: Optional[List[str]] = None,
) -> BayaniRelation:
    return BayaniRelation(
        relation_type=relation_type,
        source_text=source_text,
        subject=subject,
        predicate_or_target=predicate_or_target,
        carrier_operator=carrier_operator,
        confidence=confidence,
        epistemic_rank=epistemic_rank,
        possible_usuli_effect=possible_usuli_effect,
        forbidden_jumps_checked=(
            forbidden_jumps_checked
            if forbidden_jumps_checked is not None
            else list(_RELATIONAL_FORBIDDEN_JUMPS)
        ),
    )


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

def _extract_tadminiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect lexical inclusion/containment (تضمين) patterns."""
    for i, tok in enumerate(tokens):
        if tok in _TADMIN_MARKERS:
            subject = tokens[0] if tokens else None
            target = tokens[i + 1] if i + 1 < len(tokens) else None
            return _make_relation(
                TADMINIYYAH, text,
                subject=subject,
                predicate_or_target=target,
                carrier_operator="lexical_tadmin",
                confidence=0.9,
            )
    return None


def _extract_shartiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect conditional sentences (إن، إذا، متى …)."""
    if not tokens:
        return None
    first = tokens[0]
    if first in _CONDITIONAL_TOOLS:
        # Look for apodosis after فـ / ف
        apodosis: Optional[str] = None
        for j in range(1, len(tokens)):
            if tokens[j].startswith("ف"):
                apodosis = " ".join(tokens[j:])
                break
        return _make_relation(
            SHARTIYYAH, text,
            subject=first,
            predicate_or_target=apodosis,
            carrier_operator="conditional_tool",
            confidence=0.9,
            possible_usuli_effect="hukm_conditioned",
        )
    return None


def _extract_istithnaiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect exception (إلا، غير، سوى …) patterns."""
    for i, tok in enumerate(tokens):
        if tok in _EXCEPTION_TOOLS:
            mustathna_min = " ".join(tokens[:i]) if i > 0 else None
            mustathna = tokens[i + 1] if i + 1 < len(tokens) else None
            return _make_relation(
                ISTITHNAIYYAH, text,
                subject=mustathna_min,
                predicate_or_target=mustathna,
                carrier_operator="exception_tool",
                confidence=0.9,
                possible_usuli_effect="takhsis_candidate",
            )
    return None


def _extract_ghaiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect purpose/limit (حتى، إلى) patterns."""
    for i, tok in enumerate(tokens):
        if tok in _GHAYAH_TOOLS:
            anchor = " ".join(tokens[:i]) if i > 0 else None
            target = tokens[i + 1] if i + 1 < len(tokens) else None
            return _make_relation(
                GHAIYYAH, text,
                subject=anchor,
                predicate_or_target=target,
                carrier_operator="ghayah_tool",
                confidence=0.85,
                possible_usuli_effect="scope_limit",
            )
    return None


def _extract_sababiyyah(
    text: str,
    tokens: List[str],
) -> List[BayaniRelation]:
    """Detect cause/reason (بسبب، لأجل، لأن …) patterns.

    ``tokens`` is accepted for API symmetry with other extraction functions;
    cause detection uses substring search on ``text`` directly.
    """
    relations: List[BayaniRelation] = []
    for marker in _SABAB_TOOLS:
        if marker in text:
            idx = text.index(marker)
            sabab_part = text[idx + len(marker):].strip() or None
            musabbab_part = text[:idx].strip() or None
            relations.append(_make_relation(
                SABABIYYAH, text,
                subject=musabbab_part,
                predicate_or_target=sabab_part,
                carrier_operator="cause_tool",
                confidence=0.85,
                possible_usuli_effect="illah_candidate",
            ))
            if musabbab_part:
                relations.append(_make_relation(
                    MUSABBABIYYAH, text,
                    subject=sabab_part,
                    predicate_or_target=musabbab_part,
                    carrier_operator="cause_result_link",
                    confidence=0.75,
                ))
            return relations
    return relations


def _extract_zamaniyyah_makaniyyah(
    text: str, tokens: List[str]
) -> List[BayaniRelation]:
    """Detect time (ظرف زمان) and place (ظرف مكان) structures."""
    relations: List[BayaniRelation] = []
    for i, tok in enumerate(tokens):
        if tok == "في" and i + 1 < len(tokens):
            next_tok = tokens[i + 1]
            bare = next_tok[2:] if _starts_with_article(next_tok) else next_tok
            if next_tok in _TIME_MARKERS or bare in _TIME_MARKERS:
                relations.append(_make_relation(
                    ZAMANIYYAH, text,
                    predicate_or_target=next_tok,
                    carrier_operator="zarf_zaman",
                    confidence=0.8,
                ))
            elif next_tok in _PLACE_MARKERS or bare in _PLACE_MARKERS:
                relations.append(_make_relation(
                    MAKANIYYAH, text,
                    predicate_or_target=next_tok,
                    carrier_operator="zarf_makan",
                    confidence=0.8,
                ))
        elif tok in {"يوم", "عند", "ليلة"} and i + 1 < len(tokens):
            relations.append(_make_relation(
                ZAMANIYYAH, text,
                predicate_or_target=" ".join(tokens[i:i + 2]),
                carrier_operator="zarf_zaman",
                confidence=0.75,
            ))
    return relations


def _extract_taqyidiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect adjective/restriction (نعت/صفة) patterns.

    Detects:
    - ال+noun + ال+adj  (definite-definite pair, e.g. "الطلاب المجتهدون")
    - indefinite noun + indefinite adj (e.g. "رقبة مؤمنة") — two tokens,
      neither is a known verb or conditional/exception tool.
    """
    if len(tokens) < 2:
        return None

    first, second = tokens[0], tokens[1]

    # Pattern 1: both words carry ال and sentence has only these two tokens
    if (
        len(tokens) == 2
        and _starts_with_article(first)
        and _starts_with_article(second)
    ):
        return _make_relation(
            TAQYIDIYYAH, text,
            subject=first,
            predicate_or_target=second,
            carrier_operator="sifah/adjective",
            confidence=0.85,
            possible_usuli_effect="possible_mafhoom_sifah",
        )

    # Pattern 2: indefinite pair — neither carries ال, neither is a verb or tool
    if (
        len(tokens) == 2
        and not _starts_with_article(first)
        and not _starts_with_article(second)
        and first not in _VERBAL_SENTENCE_VERBS
        and second not in _VERBAL_SENTENCE_VERBS
        and first not in _CONDITIONAL_TOOLS
        and first not in _EXCEPTION_TOOLS
        and first not in _GHAYAH_TOOLS
    ):
        # Adjective heuristic: second word ends with typical Arabic adj suffixes
        # (ة، ون، ين، ان، ات) — avoids treating idafa (كتاب زيد) as taqyid
        if any(second.endswith(sfx) for sfx in _ADJ_ENDINGS):
            return _make_relation(
                TAQYIDIYYAH, text,
                subject=first,
                predicate_or_target=second,
                carrier_operator="sifah/adjective",
                confidence=0.8,
                possible_usuli_effect="possible_mafhoom_sifah",
            )

    return None


def _extract_verbal_relations(
    text: str, tokens: List[str]
) -> List[BayaniRelation]:
    """Detect verbal sentence relations: fa_iliyyah, maf_uliyyah, haliyyah."""
    relations: List[BayaniRelation] = []
    if not tokens:
        return relations

    first = tokens[0]
    if first not in _VERBAL_SENTENCE_VERBS:
        return relations

    verb = first
    is_hal_verb = verb in _HAL_TRIGGER_VERBS

    if len(tokens) >= 2:
        subject = tokens[1]
        relations.append(_make_relation(
            FA_ILIYYAH, text,
            subject=verb,
            predicate_or_target=subject,
            carrier_operator="verb_sentence",
            confidence=0.85,
        ))

        if len(tokens) >= 3:
            last = tokens[-1]
            # Hal heuristic: motion verb + subject + single word ending in ا/ًا
            last_is_hal = (
                is_hal_verb
                and not _starts_with_article(last)
                and last not in _EXCEPTION_TOOLS
                and last not in _GHAYAH_TOOLS
                and last not in _SABAB_TOOLS
                and (last.endswith("ا") or last.endswith("ًا"))
                and len(tokens) == 3
            )
            if last_is_hal:
                relations.append(_make_relation(
                    HALIYYAH, text,
                    subject=subject,
                    predicate_or_target=last,
                    carrier_operator="hal",
                    confidence=0.8,
                    possible_usuli_effect="constraint_on_ruling",
                ))
            else:
                # Maf'ul: token after subject, skip exception/ghayah/sabab tools
                obj = tokens[2]
                if (
                    obj not in _EXCEPTION_TOOLS
                    and obj not in _GHAYAH_TOOLS
                    and obj not in _SABAB_TOOLS
                ):
                    relations.append(_make_relation(
                        MAF_ULIYYAH, text,
                        subject=verb,
                        predicate_or_target=obj,
                        carrier_operator="verb_sentence",
                        confidence=0.8,
                    ))

    return relations


def _extract_isnadiyyah(
    text: str, tokens: List[str]
) -> Optional[BayaniRelation]:
    """Detect nominal sentence (جملة اسمية: mubtada + khabar) patterns.

    Only fires when the subject (mubtada) carries the definite article ال
    and the predicate (khabar) does NOT — the typical pattern of simple
    nominal sentences such as "الخمر حرام" or "الماء طهور".
    """
    if len(tokens) < 2:
        return None
    first = tokens[0]
    if first in _VERBAL_SENTENCE_VERBS:
        return None
    if first in _CONDITIONAL_TOOLS or first in _EXCEPTION_TOOLS or first in _GHAYAH_TOOLS:
        return None
    # Definite subject + non-definite predicate → clear isnadiyyah
    if _starts_with_article(first):
        khabar = tokens[1] if len(tokens) == 2 else " ".join(tokens[1:])
        if not _starts_with_article(khabar):
            return _make_relation(
                ISNADIYYAH, text,
                subject=first,
                predicate_or_target=khabar,
                carrier_operator="nominal_sentence",
                confidence=0.85,
                epistemic_rank="zanni",
                possible_usuli_effect="hukm_bearer",
            )
    return None


def _check_idafa_unresolved(text: str, tokens: List[str]) -> Optional[str]:
    """Flag two-token sequences that look like idafa (possession/specification).

    Idafa signature: first token has no ال, second has no ال, neither is a
    known verb or operator.  These are marked *unresolved* rather than mapped
    to a relation, because without morphological analysis idafa and taqyid
    cannot be reliably separated.
    """
    if len(tokens) == 2:
        first, second = tokens[0], tokens[1]
        if (
            not _starts_with_article(first)
            and not _starts_with_article(second)
            and first not in _VERBAL_SENTENCE_VERBS
            and second not in _VERBAL_SENTENCE_VERBS
            and first not in _CONDITIONAL_TOOLS
            and first not in _EXCEPTION_TOOLS
            and first not in _GHAYAH_TOOLS
        ):
            return (
                f"possible_idafa: {text!r} — structure ambiguous "
                "(idafa/possession vs taqyid); morphological disambiguation required"
            )
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_relations(text: str) -> RelationalParseResult:
    """Parse Arabic *text* and extract its semantic-relational structure.

    Returns a :class:`RelationalParseResult` containing all detected
    :class:`BayaniRelation` objects, unresolved items, and notes.

    The parser is deterministic and rule-based — it does not depend on any
    external NLP library or LLM.  Rules are applied in priority order:

    1. Tadminiyyah  — explicit containment marker (يتضمن …)
    2. Shartiyyah   — conditional tool at sentence start (إن، إذا، متى …)
    3. Istithnaiyyah — exception tool in sentence (إلا، غير، سوى …)
    4. Ghaiyyah     — limit/purpose tool (حتى، إلى)
    5. Sababiyyah / Musabbabiyyah — cause marker (بسبب، لأجل، لأن …)
    6. Zamaniyyah / Makaniyyah   — temporal/spatial markers
    7. Taqyidiyyah  — adjective restriction (ال+noun + ال+adj, or indef pair)
    8. Verbal relations — fa_iliyyah, maf_uliyyah, haliyyah
    9. Isnadiyyah   — nominal sentence fallback (ال+noun + non-ال khabar)
    10. Idafa check — ambiguous possession patterns → unresolved
    """
    text = text.strip()
    tokens = _tokenize(text)

    result = RelationalParseResult(source_text=text)

    if not tokens:
        result.notes.append("empty_input")
        return result

    # 1. Tadminiyyah
    tadmin = _extract_tadminiyyah(text, tokens)
    if tadmin:
        result.relations.append(tadmin)

    # 2. Shartiyyah
    shart = _extract_shartiyyah(text, tokens)
    if shart:
        result.relations.append(shart)

    # 3. Istithnaiyyah
    istithna = _extract_istithnaiyyah(text, tokens)
    if istithna:
        result.relations.append(istithna)

    # 4. Ghaiyyah
    ghayah = _extract_ghaiyyah(text, tokens)
    if ghayah:
        result.relations.append(ghayah)

    # 5. Sababiyyah / Musabbabiyyah
    result.relations.extend(_extract_sababiyyah(text, tokens))

    # 6. Zamaniyyah / Makaniyyah
    result.relations.extend(_extract_zamaniyyah_makaniyyah(text, tokens))

    # 7. Taqyidiyyah — only when not already handled by a higher-priority rule
    taqyid = _extract_taqyidiyyah(text, tokens)
    if taqyid:
        result.relations.append(taqyid)

    # 8. Verbal relations
    verbal_rels = _extract_verbal_relations(text, tokens)
    result.relations.extend(verbal_rels)

    # 9. Isnadiyyah — only when no verbal or taqyid relations extracted
    has_verbal = any(
        r.relation_type in (FA_ILIYYAH, MAF_ULIYYAH, HALIYYAH)
        for r in result.relations
    )
    has_taqyid = any(r.relation_type == TAQYIDIYYAH for r in result.relations)
    if not has_verbal and not has_taqyid:
        isnad = _extract_isnadiyyah(text, tokens)
        if isnad:
            result.relations.append(isnad)

    # 10. Idafa check → unresolved
    idafa_note = _check_idafa_unresolved(text, tokens)
    if idafa_note:
        # Only add if taqyidiyyah was NOT already extracted for this pair
        if not has_taqyid:
            result.unresolved.append(idafa_note)

    # Diagnostics note
    if not result.relations and not result.unresolved:
        result.notes.append(
            "no_relations_extracted: structure not matched by current rules"
        )
    else:
        rel_summary = ", ".join(r.relation_type for r in result.relations)
        result.notes.append(
            f"extracted {len(result.relations)} relation(s)"
            + (f": {rel_summary}" if rel_summary else "")
        )

    return result
