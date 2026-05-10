# Phase 8.3 — Jamid/Mushtaq Concept Geometry Layer

## Overview

Phase 8.3 introduces the **Concept Geometry Layer** — a CFK-compatible layer that models Arabic concept geometry through two complementary lenses:

- **Jamid (الجامد)** — Essence Geometry: fixes the ontological center of a primitive noun (genus, species, differentia, intrinsic properties).
- **Mushtaq (المشتق)** — Derivational Relation Geometry: unfolds the folded event/attribute relation encoded in a derived word (root + pattern → projected relation).

## Key Rules

| Rule | Value |
|------|-------|
| `can_create_evidence` | **False** (immutable) |
| `can_issue_certificate` | **False** (immutable) |
| `can_form_concept` | True |
| `can_raise_epistemic_certainty` | False |
| Validation score target | **≥ 0.95** |

Neither Jamid nor Mushtaq creates evidence or issues a Certificate. Both feed `KernelProjection` in CFK.

## Module Structure

```
src/mcd/concept_geometry/
├── __init__.py
├── jamid_schema.py              # JamidEssence dataclass + EssenceType enum
├── mushtaq_schema.py            # MushtaqUnit dataclass + DerivationType + ProjectedRelation
├── jamid_essence_ontology.py    # JamidEssenceOntology with 12+ built-in essences
├── mushtaq_derivation_engine.py # MushtaqDerivationEngine (known-word DB + unknown fallback)
├── root_family_linker.py        # RootFamilyLinker — surface → root family
├── pattern_operator_linker.py   # PatternOperatorLinker — pattern → operator type
├── masdar_event_linker.py       # MasdarEventLinker — masdar → event class
├── essence_attribute_binder.py  # EssenceAttributeBinder — Jamid ↔ Mushtaq binding
├── concept_center.py            # ConceptCenter + build_concept_center()
├── concept_geometry_graph.py    # ConceptGeometryGraph + ConceptGeometryGraphBuilder
├── concept_geometry_projection.py  # ConceptGeometryProjection + CONCEPT_GEOMETRY_CONTRACT
├── concept_geometry_validator.py   # ConceptGeometryValidator (score ≥ 0.95)
├── concept_geometry_report.py      # Markdown/JSON report generation
└── serializers.py                  # JSON serialization helpers
```

## Jamid Essence Ontology

12 built-in Arabic essences:

| Word | Type | Genus | Species |
|------|------|-------|---------|
| إنسان | species | حيوان | إنسان |
| حجر | natural_object | جماد | صخرة |
| ماء | material | مادة | سائل |
| نار | natural_object | طاقة | حرارة |
| شجرة | living_being | نبات | شجرة |
| كتاب | artifact | وعاء | وعاء معرفي |
| قلم | tool | أداة | أداة كتابة |
| بيت | artifact | مكان | مسكن |
| مدرسة | institution | مؤسسة | مؤسسة تعليمية |
| علم | abstract_concept | معرفة | معرفة منهجية |
| عدل | abstract_concept | قيمة | قيمة أخلاقية |
| حق | abstract_concept | قيمة | قيمة قانونية |

## Mushtaq Derivation Engine

Analyzes Arabic derived words and infers:
- Root family (e.g. `ك ت ب`)
- Morphological pattern (e.g. `فاعل`)
- Derivation type (e.g. `ism_faail`)
- Projected relation (e.g. `agent_of`)
- Certainty policy (`pattern_confirmed` vs `context_required`)

### Known words

| Word | Root | Type | Projected Relation |
|------|------|------|--------------------|
| كاتب | ك ت ب | ism_faail | agent_of |
| مكتوب | ك ت ب | ism_mafool | patient_of |
| مكتب | ك ت ب | ism_makan | unknown (context_required) |
| كتابة | ك ت ب | masdar | has_property |
| مكتبة | ك ت ب | ism_makan | place_of |
| كتابي | ك ت ب | nisba | attributed_to |
| عالم | ع ل م | ism_faail | agent_of |
| زارع | ز ر ع | ism_faail | agent_of |

## CLI Commands

```bash
# Analyze a Jamid word
mcd jamid-analyze --word إنسان --output json
mcd jamid-analyze --word حجر --output markdown

# Analyze a Mushtaq word
mcd mushtaq-analyze --word كاتب --output json
mcd mushtaq-analyze --word مكتب --output markdown

# Build concept geometry graph
mcd concept-geometry-graph --word كاتب --output json
mcd concept-geometry-graph --word إنسان --output markdown

# Run validation (score >= 0.95)
mcd concept-geometry-validate --output json
mcd concept-geometry-validate --output markdown
```

## Data Files

```
data/concept_geometry/
├── jamid_essence_seed_ar.jsonl     # Seed Jamid essences (JSONL)
└── mushtaq_derivation_seed_ar.jsonl  # Seed Mushtaq derivations (JSONL)
```

## Tests

9 test files covering all components:

| Test File | Coverage |
|-----------|----------|
| `test_jamid_schema.py` | JamidEssence schema, hard rules, serialization |
| `test_mushtaq_schema.py` | MushtaqUnit schema, hard rules, serialization |
| `test_jamid_essence_ontology.py` | Ontology loading, classification, projection |
| `test_mushtaq_derivation_engine.py` | Derivation analysis, known words, hard rules |
| `test_concept_center.py` | ConceptCenter construction, axes, hard rules |
| `test_concept_geometry_graph.py` | Graph building, edge types, markdown output |
| `test_concept_geometry_projection.py` | CFK projection, contract validation |
| `test_concept_geometry_validator.py` | Validation score ≥ 0.95, violation detection |
| `test_concept_geometry_cli.py` | CLI command integration tests |

Run all tests:

```bash
cd /home/runner/work/Salehan19-6-67/Salehan19-6-67
PYTHONPATH=src python -m pytest tests/test_jamid_schema.py tests/test_mushtaq_schema.py tests/test_jamid_essence_ontology.py tests/test_mushtaq_derivation_engine.py tests/test_concept_center.py tests/test_concept_geometry_graph.py tests/test_concept_geometry_projection.py tests/test_concept_geometry_validator.py tests/test_concept_geometry_cli.py -v
```

## CFK Integration Contract

```python
CONCEPT_GEOMETRY_CONTRACT = CFKIntegrationContract(
    source_layer="concept_geometry",
    projection_type="concept_formation",
    allowed_outputs=["concept_formation", "essence_projection", "derivational_projection", "domain_attribution"],
    forbidden_outputs=["certificate", "evidence", "epistemic_certainty", "factual_certainty"],
    can_create_evidence=False,
    can_issue_certificate=False,
    ...
)
```
