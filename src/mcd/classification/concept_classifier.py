"""ConceptClassifier — maps individual concepts to classification vectors.

Uses lexicon-based, additive scoring. No LLM.
Returns dicts with scores for each taxonomy dimension.
"""
from __future__ import annotations

from mcd.classification.prompt_frame import PromptConcept
from mcd.classification.taxonomy import (
    ConceptType,
    EvidenceNeed,
    JudgmentType,
    KnowledgeCategory,
    RootDomain,
)


# ---------------------------------------------------------------------------
# Lexicons  (word → {dimension: score})
# ---------------------------------------------------------------------------

# Each entry: normalized Arabic word → partial scores
# Scores are additive: concept gets union of all matching entries

_ROOT_DOMAIN_LEXICON: dict[str, dict[str, float]] = {
    # universe
    "نار": {RootDomain.UNIVERSE: 0.90},
    "ماء": {RootDomain.UNIVERSE: 0.90},
    "ارض": {RootDomain.UNIVERSE: 0.85},
    "سماء": {RootDomain.UNIVERSE: 0.85},
    "طبيعه": {RootDomain.UNIVERSE: 0.85},
    "طبيعة": {RootDomain.UNIVERSE: 0.85},
    "حرق": {RootDomain.UNIVERSE: 0.80},
    "تحرق": {RootDomain.UNIVERSE: 0.70},
    "احتراق": {RootDomain.UNIVERSE: 0.80},
    "حراره": {RootDomain.UNIVERSE: 0.80},
    "ضوء": {RootDomain.UNIVERSE: 0.75},
    "فيزياء": {RootDomain.UNIVERSE: 0.90},
    # human
    "عقل": {RootDomain.HUMAN: 0.95},
    "ادراك": {RootDomain.HUMAN: 0.90},
    "لغه": {RootDomain.HUMAN: 0.85, RootDomain.HUMAN: 0.85},
    "لغة": {RootDomain.HUMAN: 0.85},
    "تفكير": {RootDomain.HUMAN: 0.90},
    "كذب": {RootDomain.HUMAN: 0.80, RootDomain.LIFE: 0.60},
    "انسان": {RootDomain.HUMAN: 0.95},
    "علم": {RootDomain.HUMAN: 0.70, RootDomain.UNIVERSE: 0.40},
    "تعلم": {RootDomain.HUMAN: 0.80},
    # life
    "نظام": {RootDomain.LIFE: 0.80, RootDomain.HUMAN: 0.40},
    "مجتمع": {RootDomain.LIFE: 0.90},
    "تربيه": {RootDomain.LIFE: 0.85, RootDomain.HUMAN: 0.60},
    "تربية": {RootDomain.LIFE: 0.85, RootDomain.HUMAN: 0.60},
    "اقتصاد": {RootDomain.LIFE: 0.85},
    "حضاره": {RootDomain.LIFE: 0.90},
    "حضارة": {RootDomain.LIFE: 0.90},
    "api": {RootDomain.LIFE: 0.50, RootDomain.HUMAN: 0.30},
    "ذكاء اصطناعي": {RootDomain.HUMAN: 0.70, RootDomain.LIFE: 0.60},
    "نظام تعليمي": {RootDomain.LIFE: 0.85, RootDomain.HUMAN: 0.70},
}

_CONCEPT_TYPE_LEXICON: dict[str, dict[str, float]] = {
    "نار": {ConceptType.THING: 0.85, ConceptType.PROPERTY: 0.20},
    "ماء": {ConceptType.THING: 0.90},
    "عقل": {ConceptType.THING: 0.40, ConceptType.SYSTEM: 0.35, ConceptType.PROPERTY: 0.25},
    "ضار": {ConceptType.PROPERTY: 0.90},
    "ضاره": {ConceptType.PROPERTY: 0.90},
    "نافع": {ConceptType.PROPERTY: 0.90},
    "مفيد": {ConceptType.PROPERTY: 0.85},
    "حرام": {ConceptType.VALUE: 0.90},
    "واجب": {ConceptType.VALUE: 0.90},
    "خير": {ConceptType.VALUE: 0.90},
    "شر": {ConceptType.VALUE: 0.90},
    "عدل": {ConceptType.VALUE: 0.90},
    "يسبب": {ConceptType.RELATION: 0.90},
    "يدل": {ConceptType.RELATION: 0.85},
    "يتضمن": {ConceptType.RELATION: 0.80},
    "يقيد": {ConceptType.RELATION: 0.80},
    "تحرق": {ConceptType.RELATION: 0.70, ConceptType.PROPERTY: 0.40},
    "نظام": {ConceptType.SYSTEM: 0.80},
    "api": {ConceptType.TOOL: 0.95},
    "ديكودر": {ConceptType.TOOL: 0.85},
    "برنامج": {ConceptType.TOOL: 0.80},
    "كود": {ConceptType.TOOL: 0.85},
    "لماذا": {ConceptType.PURPOSE: 0.90},
    "هدف": {ConceptType.PURPOSE: 0.85},
    "غايه": {ConceptType.PURPOSE: 0.85},
    "غاية": {ConceptType.PURPOSE: 0.85},
    "لاجل": {ConceptType.PURPOSE: 0.80},
    "نظام تعليمي": {ConceptType.SYSTEM: 0.90},
    "ذكاء اصطناعي": {ConceptType.TOOL: 0.75, ConceptType.SYSTEM: 0.60},
}

_KNOWLEDGE_CATEGORY_LEXICON: dict[str, dict[str, float]] = {
    "نار": {KnowledgeCategory.SCIENCE: 0.70},
    "ماء": {KnowledgeCategory.SCIENCE: 0.80},
    "فيزياء": {KnowledgeCategory.SCIENCE: 0.95},
    "كيمياء": {KnowledgeCategory.SCIENCE: 0.95},
    "احتراق": {KnowledgeCategory.SCIENCE: 0.80},
    "تجربه": {KnowledgeCategory.SCIENCE: 0.80},
    "تجربة": {KnowledgeCategory.SCIENCE: 0.80},
    "قياس": {KnowledgeCategory.SCIENCE: 0.75},
    "عقل": {KnowledgeCategory.METHOD: 0.80, KnowledgeCategory.CULTURE: 0.50},
    "ادراك": {KnowledgeCategory.METHOD: 0.75},
    "منهج": {KnowledgeCategory.METHOD: 0.90},
    "استدلال": {KnowledgeCategory.METHOD: 0.90},
    "تصنيف": {KnowledgeCategory.METHOD: 0.85},
    "يقين": {KnowledgeCategory.METHOD: 0.85},
    "درجه يقين": {KnowledgeCategory.METHOD: 0.90},
    "علم": {KnowledgeCategory.METHOD: 0.50, KnowledgeCategory.SCIENCE: 0.60, KnowledgeCategory.LANGUAGE: 0.30},
    "لغه": {KnowledgeCategory.LANGUAGE: 0.90},
    "لغة": {KnowledgeCategory.LANGUAGE: 0.90},
    "معنى": {KnowledgeCategory.LANGUAGE: 0.85},
    "كلمه": {KnowledgeCategory.LANGUAGE: 0.85},
    "كلمة": {KnowledgeCategory.LANGUAGE: 0.85},
    "دال": {KnowledgeCategory.LANGUAGE: 0.90},
    "مدلول": {KnowledgeCategory.LANGUAGE: 0.90},
    "دلاله": {KnowledgeCategory.LANGUAGE: 0.90},
    "نحو": {KnowledgeCategory.LANGUAGE: 0.90},
    "صرف": {KnowledgeCategory.LANGUAGE: 0.90},
    "حضاره": {KnowledgeCategory.CIVILIZATION: 0.90, KnowledgeCategory.CULTURE: 0.60},
    "حضارة": {KnowledgeCategory.CIVILIZATION: 0.90, KnowledgeCategory.CULTURE: 0.60},
    "مجتمع": {KnowledgeCategory.CULTURE: 0.70, KnowledgeCategory.CIVILIZATION: 0.50},
    "ثقافه": {KnowledgeCategory.CULTURE: 0.90},
    "ثقافة": {KnowledgeCategory.CULTURE: 0.90},
    "قيمه": {KnowledgeCategory.CULTURE: 0.80},
    "قيمة": {KnowledgeCategory.CULTURE: 0.80},
    "كذب": {KnowledgeCategory.CULTURE: 0.60, KnowledgeCategory.METHOD: 0.30},
    "api": {KnowledgeCategory.TECHNOLOGY: 0.95},
    "برمجه": {KnowledgeCategory.TECHNOLOGY: 0.95},
    "برمجة": {KnowledgeCategory.TECHNOLOGY: 0.95},
    "كود": {KnowledgeCategory.TECHNOLOGY: 0.90},
    "تقنيه": {KnowledgeCategory.TECHNOLOGY: 0.90},
    "تقنية": {KnowledgeCategory.TECHNOLOGY: 0.90},
    "برنامج": {KnowledgeCategory.TECHNOLOGY: 0.85},
    "ديكودر": {KnowledgeCategory.TECHNOLOGY: 0.85},
    "ذكاء اصطناعي": {KnowledgeCategory.TECHNOLOGY: 0.90, KnowledgeCategory.SCIENCE: 0.50},
    "نظام تعليمي": {KnowledgeCategory.CIVILIZATION: 0.70, KnowledgeCategory.CULTURE: 0.60},
    "تربيه": {KnowledgeCategory.CULTURE: 0.70, KnowledgeCategory.CIVILIZATION: 0.50},
    "تربية": {KnowledgeCategory.CULTURE: 0.70, KnowledgeCategory.CIVILIZATION: 0.50},
}

_JUDGMENT_HINT_LEXICON: dict[str, dict[str, float]] = {
    "api": {JudgmentType.TECHNICAL: 0.80, JudgmentType.PRACTICAL: 0.60},
    "ابن": {JudgmentType.PRACTICAL: 0.75, JudgmentType.TECHNICAL: 0.60},
    "انشئ": {JudgmentType.PRACTICAL: 0.75, JudgmentType.TECHNICAL: 0.60},
    "برمجه": {JudgmentType.TECHNICAL: 0.90},
    "برمجة": {JudgmentType.TECHNICAL: 0.90},
    "كود": {JudgmentType.TECHNICAL: 0.90, JudgmentType.PRACTICAL: 0.60},
    "خطوات": {JudgmentType.PRACTICAL: 0.90},
    "خطه": {JudgmentType.PRACTICAL: 0.85},
    "خطة": {JudgmentType.PRACTICAL: 0.85},
    "حرام": {JudgmentType.SHARI: 0.95},
    "واجب": {JudgmentType.SHARI: 0.95},
    "مكروه": {JudgmentType.SHARI: 0.90},
    "مندوب": {JudgmentType.SHARI: 0.85},
    "مباح": {JudgmentType.SHARI: 0.80},
    "ثواب": {JudgmentType.SHARI: 0.85},
    "عقاب": {JudgmentType.SHARI: 0.85},
    "ضار": {JudgmentType.VALUE: 0.80, JudgmentType.EPISTEMIC: 0.60},
    "ضاره": {JudgmentType.VALUE: 0.80, JudgmentType.EPISTEMIC: 0.60},
    "نافع": {JudgmentType.VALUE: 0.80, JudgmentType.EPISTEMIC: 0.60},
    "يسبب": {JudgmentType.EPISTEMIC: 0.75},
    "يدل": {JudgmentType.EPISTEMIC: 0.80},
    "علم": {JudgmentType.EPISTEMIC: 0.60},
    "منهج": {JudgmentType.EPISTEMIC: 0.70},
    "ذكاء اصطناعي": {JudgmentType.TECHNICAL: 0.70, JudgmentType.PRACTICAL: 0.50},
    "نظام تعليمي": {JudgmentType.PRACTICAL: 0.70, JudgmentType.TECHNICAL: 0.50},
}

_EVIDENCE_HINT_LEXICON: dict[str, dict[str, float]] = {
    "نار": {EvidenceNeed.SENSORY: 0.85, EvidenceNeed.EXPERIMENTAL: 0.70},
    "تحرق": {EvidenceNeed.SENSORY: 0.85, EvidenceNeed.EXPERIMENTAL: 0.70},
    "احتراق": {EvidenceNeed.EXPERIMENTAL: 0.85, EvidenceNeed.SENSORY: 0.70},
    "لغه": {EvidenceNeed.LINGUISTIC: 0.90, EvidenceNeed.CONTEXTUAL: 0.70},
    "لغة": {EvidenceNeed.LINGUISTIC: 0.90, EvidenceNeed.CONTEXTUAL: 0.70},
    "معنى": {EvidenceNeed.LINGUISTIC: 0.90, EvidenceNeed.CONTEXTUAL: 0.80},
    "علم": {EvidenceNeed.CONTEXTUAL: 0.70, EvidenceNeed.LINGUISTIC: 0.60},
    "حرام": {EvidenceNeed.SHARI: 0.95, EvidenceNeed.TEXTUAL: 0.90},
    "واجب": {EvidenceNeed.SHARI: 0.95, EvidenceNeed.TEXTUAL: 0.90},
    "دليل شرعي": {EvidenceNeed.SHARI: 0.95, EvidenceNeed.TEXTUAL: 0.90},
    "api": {EvidenceNeed.TECHNICAL: 0.90, EvidenceNeed.TEXTUAL: 0.60},
    "كود": {EvidenceNeed.TECHNICAL: 0.90},
    "ذكاء اصطناعي": {EvidenceNeed.TECHNICAL: 0.80, EvidenceNeed.TEXTUAL: 0.50},
    "نظام تعليمي": {EvidenceNeed.CONTEXTUAL: 0.70, EvidenceNeed.TEXTUAL: 0.50},
    "تاريخ": {EvidenceNeed.HISTORICAL: 0.90, EvidenceNeed.TEXTUAL: 0.70},
    "حضاره": {EvidenceNeed.HISTORICAL: 0.75, EvidenceNeed.TEXTUAL: 0.60},
    "حضارة": {EvidenceNeed.HISTORICAL: 0.75, EvidenceNeed.TEXTUAL: 0.60},
    "ضار": {EvidenceNeed.CONTEXTUAL: 0.70, EvidenceNeed.TEXTUAL: 0.50},
    "كذب": {EvidenceNeed.CONTEXTUAL: 0.65, EvidenceNeed.HISTORICAL: 0.50},
}


# ---------------------------------------------------------------------------
# ConceptClassifier
# ---------------------------------------------------------------------------

def _lookup(lexicon: dict[str, dict[str, float]], key: str) -> dict[str, float]:
    """Return lexicon entry for key, its lowercase, or its ال-stripped form."""
    def _strip_al(w: str) -> str:
        if w.startswith("ال") and len(w) > 2:
            return w[2:]
        return w

    for candidate in (key, key.lower(), _strip_al(key), _strip_al(key).lower()):
        if candidate in lexicon:
            return lexicon[candidate]
    return {}


class ConceptClassifier:
    """Classify a PromptConcept into multi-dimensional vectors."""

    def classify(self, concept: PromptConcept) -> PromptConcept:
        """Return a new PromptConcept enriched with classification scores."""
        key = concept.normalized or concept.surface

        root_domain = _merge(
            _lookup(_ROOT_DOMAIN_LEXICON, key),
            dict(concept.root_domain),
        )
        concept_type = _merge(
            _lookup(_CONCEPT_TYPE_LEXICON, key),
            dict(concept.concept_type),
        )
        knowledge_category = _merge(
            _lookup(_KNOWLEDGE_CATEGORY_LEXICON, key),
            dict(concept.knowledge_category),
        )
        judgment_hint = _merge(
            _lookup(_JUDGMENT_HINT_LEXICON, key),
            dict(concept.judgment_hint),
        )
        evidence_hint = _merge(
            _lookup(_EVIDENCE_HINT_LEXICON, key),
            dict(concept.evidence_hint),
        )

        return PromptConcept(
            surface=concept.surface,
            normalized=concept.normalized,
            span_start=concept.span_start,
            span_end=concept.span_end,
            root_domain=root_domain,
            concept_type=concept_type,
            knowledge_category=knowledge_category,
            judgment_hint=judgment_hint,
            evidence_hint=evidence_hint,
        )

    def classify_all(self, concepts: list[PromptConcept]) -> list[PromptConcept]:
        return [self.classify(c) for c in concepts]


def _merge(*dicts: dict[str, float]) -> dict[str, float]:
    """Merge multiple score dicts by taking the max score per label."""
    merged: dict[str, float] = {}
    for d in dicts:
        for k, v in d.items():
            merged[k] = max(merged.get(k, 0.0), v)
    return merged
