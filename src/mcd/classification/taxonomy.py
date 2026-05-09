"""Taxonomy enumerations for Fractal Prompt Classification Layer (FPCL)."""
from __future__ import annotations

from enum import Enum


class RootDomain(str, Enum):
    """The three root domains of reality according to Nabhani's framework."""

    UNIVERSE = "universe"   # كون — physical world, nature, matter, causality
    HUMAN = "human"         # إنسان — mind, perception, language, instinct
    LIFE = "life"           # حياة — society, relations, systems, civilisation


class ConceptType(str, Enum):
    """Classification of a concept's ontological type."""

    THING = "thing"           # شيء — a concrete or abstract entity
    PROPERTY = "property"     # خاصية — an attribute or quality
    RELATION = "relation"     # علاقة — a connection or dependency between things
    VALUE = "value"           # قيمة — an evaluative concept (good/bad, just/unjust)
    SYSTEM = "system"         # نظام — an organised whole with structure and rules
    TOOL = "tool"             # أداة — an instrument used to achieve a goal
    PURPOSE = "purpose"       # غاية — a goal, intention, or aim


class KnowledgeCategory(str, Enum):
    """Category of knowledge the prompt belongs to."""

    SCIENCE = "science"             # علم — observable, experimental, measurable
    CULTURE = "culture"             # ثقافة — ideas, values, worldview, concepts
    CIVILIZATION = "civilization"   # حضارة — integrated system of life concepts
    TECHNOLOGY = "technology"       # مدنية — tools, engineering, programming, AI
    LANGUAGE = "language"           # لغة — signs, meanings, grammar, semantics
    METHOD = "method"               # منهج — reasoning, classification, epistemology


class JudgmentType(str, Enum):
    """The type of judgment the prompt is asking for."""

    EPISTEMIC = "epistemic"     # معرفي — what is it? is it true? what is the evidence?
    TECHNICAL = "technical"     # تقني — how to build/code/design?
    VALUE = "value"             # قيمي — is it beneficial/harmful/good/bad?
    SHARI = "shari"             # شرعي — is it obligatory/forbidden/permissible?
    PRACTICAL = "practical"     # عملي — what steps? what plan? what should we do?


class EvidenceNeed(str, Enum):
    """The type of evidence required to answer the prompt."""

    SENSORY = "sensory"           # حسي — direct sensory observation
    EXPERIMENTAL = "experimental" # تجريبي — repeatable experiment or measurement
    LINGUISTIC = "linguistic"     # لغوي — meaning, etymology, semantics
    TEXTUAL = "textual"           # نصي — written source (book, document, hadith, ayah)
    HISTORICAL = "historical"     # تاريخي — historical record or precedent
    SHARI = "shari"               # شرعي — Quran, Sunnah, scholarly consensus
    TECHNICAL = "technical"       # تقني — specifications, code, API documentation
    CONTEXTUAL = "contextual"     # سياقي — situational context, pragmatics


class CertaintyPolicy(str, Enum):
    """The certainty policy to apply before answering."""

    NEAR_CERTAINTY = "near_certainty"       # يقين — strong evidence, decisive domain
    STRONG_KNOWLEDGE = "strong_knowledge"   # معرفة راجحة — good evidence, minor uncertainty
    HYPOTHESIS = "hypothesis"               # فرضية — clues present, evidence incomplete
    SUSPEND = "suspend"                     # تعليق — shari without evidence, ambiguous, conflict
