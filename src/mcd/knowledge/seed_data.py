"""Seed data: things, properties, relations."""
from __future__ import annotations

from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.things import Thing
from mcd.knowledge.properties import Property
from mcd.knowledge.facts import Fact
from mcd.knowledge.sources import Source
from mcd.core.evidence import Evidence, EvidenceType
from mcd.core.certainty import Certainty
from mcd.core.relations import Relation, RelationType


def load_seed_data(store: PriorKnowledgeStore) -> None:
    """Populate the store with seed things, properties, relations, and facts."""

    # --- Sources ---
    src_empirical = Source(
        source_id="src_empirical",
        source_type=EvidenceType.EXPERIMENTAL.value,
        name="empirical_observation",
        reliability=0.95,
        language="ar",
        description="Direct empirical observation",
    )
    src_linguistic = Source(
        source_id="src_linguistic",
        source_type=EvidenceType.LINGUISTIC.value,
        name="arabic_lexicon",
        reliability=0.90,
        language="ar",
        description="Classical Arabic lexicon",
    )
    store.add_source(src_empirical)
    store.add_source(src_linguistic)

    ev_strong = Evidence(
        source_id="src_empirical",
        source_type=EvidenceType.EXPERIMENTAL.value,
        description="حقيقة ثابتة بالملاحظة",
        strength=0.95,
        reliability=0.95,
    )
    ev_linguistic = Evidence(
        source_id="src_linguistic",
        source_type=EvidenceType.LINGUISTIC.value,
        description="ثابت لغوياً",
        strength=0.90,
        reliability=0.90,
    )

    # --- Properties ---
    props = [
        Property("prop_hot",       {"ar": "حار",           "en": "hot"},          "physical",   "boolean", [ev_strong], Certainty.from_score(0.92, "experimental")),
        Property("prop_cold",      {"ar": "بارد",          "en": "cold"},         "physical",   "boolean", [ev_strong], Certainty.from_score(0.92, "experimental")),
        Property("prop_alive",     {"ar": "حي",            "en": "alive"},        "biological", "boolean", [ev_strong], Certainty.from_score(0.90, "experimental")),
        Property("prop_solid",     {"ar": "جامد",          "en": "solid"},        "physical",   "boolean", [ev_strong], Certainty.from_score(0.90, "experimental")),
        Property("prop_liquid",    {"ar": "سائل",          "en": "liquid"},       "physical",   "boolean", [ev_strong], Certainty.from_score(0.90, "experimental")),
        Property("prop_luminous",  {"ar": "مضيء",          "en": "luminous"},     "physical",   "boolean", [ev_strong], Certainty.from_score(0.90, "experimental")),
        Property("prop_flammable", {"ar": "قابل للاحتراق", "en": "flammable"},    "physical",   "boolean", [ev_strong], Certainty.from_score(0.88, "experimental")),
        Property("prop_rational",  {"ar": "عاقل",          "en": "rational"},     "cognitive",  "boolean", [ev_strong], Certainty.from_score(0.85, "logical")),
        Property("prop_growing",   {"ar": "ينمو",          "en": "growing"},      "biological", "boolean", [ev_strong], Certainty.from_score(0.85, "experimental")),
        Property("prop_hard",      {"ar": "صلب",           "en": "hard"},         "physical",   "boolean", [ev_strong], Certainty.from_score(0.90, "experimental")),
        Property("prop_fast",      {"ar": "سريع",          "en": "fast"},         "physical",   "scalar",  [ev_strong], Certainty.from_score(0.88, "experimental")),
    ]
    for p in props:
        store.properties.add(p)

    # --- Things ---
    # نار (fire)
    fire = Thing(
        thing_id="thing_fire",
        names={"ar": "نار", "en": "fire"},
        haqiqa="ظاهرة احتراق تنتج حرارة وضوءاً",
        properties=["prop_hot", "prop_luminous", "prop_flammable"],
        effects=["احتراق", "ضوء", "حرارة"],
        affordances=["يحرق", "يضيء", "يدفئ"],
        relations=["rel_fire_causes_burning"],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.92, "experimental", "ثابت بالملاحظة"),
    )

    # ماء (water)
    water = Thing(
        thing_id="thing_water",
        names={"ar": "ماء", "en": "water"},
        haqiqa="مادة سائلة ضرورية للحياة",
        properties=["prop_cold", "prop_liquid"],
        effects=["يروي", "يطفئ"],
        affordances=["يشرب", "يروي", "يطهر"],
        relations=["rel_water_patient_of_irwa"],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.92, "experimental", "ثابت بالملاحظة"),
    )

    # إنسان (human)
    human = Thing(
        thing_id="thing_human",
        names={"ar": "إنسان", "en": "human"},
        haqiqa="كائن حي عاقل قادر على التفكير والكلام",
        properties=["prop_alive", "prop_rational"],
        effects=["يفكر", "يتكلم", "يكتب"],
        affordances=["يفكر", "يتكلم", "يكتب"],
        relations=["rel_human_predicates_reason"],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.90, "logical", "ثابت بالعقل والملاحظة"),
    )

    # شجرة (tree)
    tree = Thing(
        thing_id="thing_tree",
        names={"ar": "شجرة", "en": "tree"},
        haqiqa="كائن نباتي حي ينمو في الأرض",
        properties=["prop_alive", "prop_solid", "prop_growing"],
        effects=["يعطي ظلاً", "يعطي ثمراً"],
        affordances=["يُقطع", "يُزرع"],
        relations=[],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.88, "experimental"),
    )

    # حجر (stone)
    stone = Thing(
        thing_id="thing_stone",
        names={"ar": "حجر", "en": "stone"},
        haqiqa="جسم صلب جامد من مواد الأرض",
        properties=["prop_solid", "prop_hard"],
        effects=["يمنع المرور"],
        affordances=["يُرمى", "يُبنى به"],
        relations=[],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.90, "experimental"),
    )

    # ضوء (light)
    light = Thing(
        thing_id="thing_light",
        names={"ar": "ضوء", "en": "light"},
        haqiqa="إشعاع كهرومغناطيسي مرئي",
        properties=["prop_luminous", "prop_fast"],
        effects=["يضيء", "يكشف"],
        affordances=["يُرى به"],
        relations=[],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.92, "experimental"),
    )

    # حرارة (heat)
    heat = Thing(
        thing_id="thing_heat",
        names={"ar": "حرارة", "en": "heat"},
        haqiqa="طاقة حرارية تنتقل من الأجسام الساخنة",
        properties=["prop_hot"],
        effects=["يُسخّن", "يُحرق"],
        affordances=["يُقاس"],
        relations=[],
        evidence=[ev_strong],
        certainty=Certainty.from_score(0.90, "experimental"),
    )

    # كتابة (writing)
    writing = Thing(
        thing_id="thing_writing",
        names={"ar": "كتابة", "en": "writing"},
        haqiqa="فعل تدوين الأفكار بالرموز الكتابية",
        properties=[],
        effects=["يوثّق", "يعلّم"],
        affordances=["يُكتب"],
        relations=["rel_writing_agent_of_human"],
        evidence=[ev_linguistic],
        certainty=Certainty.from_score(0.85, "linguistic"),
    )

    # علم (knowledge/learning)
    ilm = Thing(
        thing_id="thing_ilm",
        names={"ar": "علم", "en": "knowledge"},
        haqiqa="إدراك الحقائق أو فعل التعلم حسب السياق",
        properties=["prop_rational"],
        effects=["يُفيد", "يُنير"],
        affordances=["يُتعلم", "يُعلَّم"],
        relations=[],
        evidence=[ev_linguistic],
        certainty=Certainty.from_score(0.75, "linguistic", "يحتمل التأويل — يحتاج سياقاً"),
    )

    for thing in [fire, water, human, tree, stone, light, heat, writing, ilm]:
        store.add_thing(thing)

    # --- Relations ---
    relations = [
        Relation(
            relation_id="rel_fire_causes_burning",
            relation_type=RelationType.CAUSES.value,
            source="thing_fire",
            target="احتراق",
            conditions=["وجود_وقود", "وجود_هواء"],
            evidence=[ev_strong],
            certainty=0.92,
        ),
        Relation(
            relation_id="rel_water_patient_of_irwa",
            relation_type=RelationType.PATIENT_OF.value,
            source="thing_water",
            target="يروي",
            evidence=[ev_strong],
            certainty=0.88,
        ),
        Relation(
            relation_id="rel_human_predicates_reason",
            relation_type=RelationType.PREDICATES.value,
            source="thing_human",
            target="عقل",
            evidence=[ev_strong],
            certainty=0.90,
        ),
        Relation(
            relation_id="rel_writing_agent_of_human",
            relation_type=RelationType.AGENT_OF.value,
            source="thing_writing",
            target="thing_human",
            evidence=[ev_linguistic],
            certainty=0.85,
        ),
    ]
    for rel in relations:
        store.add_relation(rel)

    # --- Facts ---
    facts = [
        Fact(
            fact_id="fact_fire_hot",
            claim="النار ساخنة",
            source_ids=["src_empirical"],
            evidence=[ev_strong],
            certainty=Certainty.from_score(0.95, "experimental"),
        ),
        Fact(
            fact_id="fact_fire_burns",
            claim="النار تحرق",
            source_ids=["src_empirical"],
            evidence=[ev_strong],
            certainty=Certainty.from_score(0.92, "experimental"),
        ),
        Fact(
            fact_id="fact_human_writes",
            claim="الإنسان يكتب",
            source_ids=["src_empirical"],
            evidence=[ev_strong],
            certainty=Certainty.from_score(0.88, "experimental"),
        ),
        Fact(
            fact_id="fact_water_quenches",
            claim="الماء يروي",
            source_ids=["src_empirical"],
            evidence=[ev_strong],
            certainty=Certainty.from_score(0.90, "experimental"),
        ),
    ]
    for fact in facts:
        store.add_fact(fact)
