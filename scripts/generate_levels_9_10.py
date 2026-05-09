#!/usr/bin/env python3
"""Generate curriculum levels 9 and 10 data files (100 examples each)."""
import json
from pathlib import Path

DATA_DIR = Path("/home/runner/work/Salehan19-6-67/Salehan19-6-67/data/curriculum")

# Level 9: Domain Reasoning — 100 examples
LEVEL_9_EXAMPLES = [
    # (text, domains, certainty, difficulty, tags)
    ("الصلاة فريضة دينية.", ["religion", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("الجراحة تحتاج تدريباً طبياً.", ["medicine", "science"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("العقد القانوني ملزم للطرفين.", ["law", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الزكاة ركن من أركان الإسلام.", ["religion", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("التضخم ظاهرة اقتصادية.", ["economics", "science"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الكذب محرم شرعاً.", ["religion", "ethics"], "certain_knowledge", "medium", ["domain_reasoning", "harm_haram"]),
    ("السرقة جريمة قانونية.", ["law", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الطب يعالج الأمراض.", ["medicine", "science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الديمقراطية نظام سياسي.", ["politics", "social"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الشعر فن أدبي.", ["arts", "culture"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الفيزياء تدرس قوانين الطبيعة.", ["science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الحرب عمل سياسي وعسكري.", ["politics", "military"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الميراث مسألة شرعية وقانونية.", ["religion", "law", "fiqh"], "certain_knowledge", "hard", ["domain_reasoning", "shari"]),
    ("التعليم حق إنساني.", ["social", "ethics", "law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الوقف مؤسسة دينية واجتماعية.", ["religion", "social", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("السوق الحرة مفهوم اقتصادي.", ["economics"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("القضاء يحكم بالقانون.", ["law"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الغيبة محرمة دينياً وضارة اجتماعياً.", ["religion", "ethics", "social"], "certain_knowledge", "medium", ["domain_reasoning", "harm_haram"]),
    ("البيع بالتقسيط مشروع تجاري.", ["economics", "religion", "fiqh"], "probable_knowledge", "hard", ["domain_reasoning", "shari"]),
    ("حقوق الإنسان مبدأ عالمي.", ["law", "ethics", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الربا محرم في الإسلام.", ["religion", "economics", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("الضريبة التزام قانوني.", ["law", "economics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الفلسفة تسعى لفهم الوجود.", ["philosophy"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الزواج عقد ديني وقانوني واجتماعي.", ["religion", "law", "social"], "certain_knowledge", "hard", ["domain_reasoning", "shari"]),
    ("الديون التجارية مسؤولية قانونية.", ["law", "economics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("التطور نظرية علمية.", ["science"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الإجهاض قضية أخلاقية ودينية وقانونية.", ["ethics", "religion", "law", "medicine"], "suspend_judgment", "hard", ["domain_reasoning"]),
    ("الفن التشكيلي تعبير ثقافي.", ["arts", "culture"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الصيام عبادة دينية.", ["religion", "fiqh"], "certain_knowledge", "easy", ["domain_reasoning", "shari"]),
    ("الإضراب حق عمالي.", ["law", "social", "economics"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("التدخين يضر بالصحة.", ["medicine", "science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الطلاق ظاهرة اجتماعية وشرعية وقانونية.", ["social", "religion", "law"], "certain_knowledge", "hard", ["domain_reasoning", "shari"]),
    ("الكيمياء علم تجريبي.", ["science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الموروث الثقافي يحدد الهوية.", ["culture", "social"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("القرآن الكريم مصدر تشريعي.", ["religion", "law", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("البيئة مسؤولية أخلاقية وقانونية.", ["ethics", "law", "science"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("اللغة العربية لغة الضاد.", ["culture", "linguistics"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الاقتصاد الإسلامي له مبادئ خاصة.", ["economics", "religion", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("السياحة نشاط اقتصادي وثقافي.", ["economics", "culture"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("القتل جريمة أخلاقية ودينية وقانونية.", ["ethics", "religion", "law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الهندسة تطبيق علمي.", ["science", "technology"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الديمقراطية قد تتعارض مع الشريعة.", ["politics", "religion"], "suspend_judgment", "hard", ["domain_reasoning", "harm_haram"]),
    ("الطاقة المتجددة ضرورة بيئية.", ["science", "ethics", "economics"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("الإرهاب جريمة دولية.", ["law", "politics", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("التراث الإنساني ملك مشترك.", ["culture", "ethics", "law"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("علم النفس يدرس السلوك الإنساني.", ["science", "medicine"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("حقوق الطفل مكفولة دولياً.", ["law", "ethics", "social"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الشريعة الإسلامية تشمل العبادات والمعاملات.", ["religion", "fiqh", "law"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("الجغرافيا تدرس الأرض وظواهرها.", ["science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("العولمة ظاهرة اقتصادية وثقافية.", ["economics", "culture", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    # More examples
    ("الحرية الصحفية حق قانوني.", ["law", "ethics", "politics"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("الأخلاق الطبية تحكم ممارسة الطب.", ["medicine", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الفلسفة والدين يتقاطعان في الأسئلة الكبرى.", ["philosophy", "religion"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("الأسرة مؤسسة اجتماعية ودينية وقانونية.", ["social", "religion", "law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("العلم التجريبي لا يحكم على المسائل الأخلاقية.", ["science", "ethics"], "certain_knowledge", "hard", ["domain_reasoning"]),
    ("الغذاء الحلال مفهوم ديني.", ["religion", "fiqh"], "certain_knowledge", "easy", ["domain_reasoning", "shari"]),
    ("حقوق الملكية الفكرية قانون حديث.", ["law", "economics", "technology"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الأمن القومي مسؤولية سياسية.", ["politics", "law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("التضامن الاجتماعي قيمة أخلاقية.", ["ethics", "social"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("علم الكلام يبحث في العقيدة.", ["religion", "philosophy"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("التجارة الدولية تخضع لاتفاقيات.", ["economics", "law", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("علم الاجتماع يدرس الظواهر الإنسانية.", ["science", "social"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("المساواة مبدأ أخلاقي وقانوني.", ["ethics", "law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الصحة النفسية جزء من الصحة العامة.", ["medicine", "social"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("العدالة الاجتماعية قيمة إنسانية.", ["ethics", "social", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الاجتهاد الفقهي يتطلب شروطاً.", ["religion", "fiqh"], "certain_knowledge", "hard", ["domain_reasoning", "shari"]),
    ("الذكاء الاصطناعي يثير تساؤلات أخلاقية.", ["technology", "ethics"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("الحرب العادلة لها معايير دولية.", ["law", "ethics", "politics"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("علم الفلك تجريبي ورياضي.", ["science"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الوصية حكم شرعي وقانوني.", ["religion", "law", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("التدخل الإنساني مبرر أخلاقياً أحياناً.", ["ethics", "politics", "law"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("الاقتصاد السلوكي يجمع علم النفس والاقتصاد.", ["economics", "science"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("المسؤولية الجنائية تتطلب الأهلية القانونية.", ["law"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الأديان الإبراهيمية تشترك في مبادئ.", ["religion"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("الدستور أعلى وثيقة قانونية في الدولة.", ["law", "politics"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("السياسة النقدية تؤثر على الاقتصاد.", ["economics", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الفلسفة الأخلاقية تدرس الخير والشر.", ["philosophy", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الإعلام الرقمي غيّر المشهد الثقافي.", ["culture", "technology", "social"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("حفظ النسل مقصد شرعي.", ["religion", "fiqh"], "certain_knowledge", "medium", ["domain_reasoning", "shari"]),
    ("المحيطات مشترك إنساني.", ["science", "law", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الأنثروبولوجيا علم ثقافي وبيولوجي.", ["science", "culture"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("التوبة مفهوم ديني وإنساني.", ["religion", "ethics"], "certain_knowledge", "easy", ["domain_reasoning", "shari"]),
    ("الفساد جريمة أخلاقية وقانونية.", ["ethics", "law", "politics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("العقل مصدر معرفة في الفلسفة والكلام.", ["philosophy", "religion"], "certain_knowledge", "hard", ["domain_reasoning"]),
    ("السيادة الرقمية مفهوم سياسي وتقني ناشئ.", ["politics", "technology", "law"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("المنطق أداة فلسفية وعلمية.", ["philosophy", "science"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الكفاءة الاقتصادية لا تعني العدالة الاجتماعية دائماً.", ["economics", "ethics"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("الأمومة قيمة إنسانية واجتماعية ودينية.", ["social", "religion", "ethics"], "certain_knowledge", "easy", ["domain_reasoning"]),
    ("الهوية الثقافية تتشكل بالتاريخ واللغة.", ["culture", "social", "linguistics"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("المشاعر البشرية محل دراسة نفسية وفلسفية.", ["science", "philosophy"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("القانون الدولي يرسي السلام نظرياً.", ["law", "politics"], "probable_knowledge", "medium", ["domain_reasoning"]),
    ("الاقتصاد المعرفي يعتمد على المعلومات.", ["economics", "technology"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الإرادة الحرة مسألة فلسفية.", ["philosophy"], "probable_knowledge", "hard", ["domain_reasoning"]),
    ("المواطنة حق وواجب قانوني واجتماعي.", ["law", "social", "ethics"], "certain_knowledge", "medium", ["domain_reasoning"]),
    ("الاستدامة البيئية مسؤولية أجيال.", ["ethics", "science", "economics", "law"], "probable_knowledge", "hard", ["domain_reasoning"]),
]

# Level 10: Graph+Vector Composition — 100 examples
LEVEL_10_EXAMPLES = [
    # (text, nodes, edges, vector_hint, certainty, difficulty, tags)
    (
        "العالم يكتشف الحقيقة بالتجربة.",
        [{"id": "العالم", "type": "agent"}, {"id": "الحقيقة", "type": "concept"}, {"id": "التجربة", "type": "instrument"}],
        [{"source": "العالم", "relation": "agent_of", "target": "يكتشف"}, {"source": "التجربة", "relation": "instrument_of", "target": "يكتشف"}],
        {"role": "agent_action", "domain": "science", "certainty": "strong"},
        "strong_knowledge", "hard", ["graph_vector_composition", "science"]
    ),
    (
        "المعلم يشرح الدرس للطلاب بالسبورة.",
        [{"id": "المعلم", "type": "agent"}, {"id": "الدرس", "type": "patient"}, {"id": "الطلاب", "type": "recipient"}, {"id": "السبورة", "type": "instrument"}],
        [{"source": "المعلم", "relation": "agent_of", "target": "يشرح"}, {"source": "الدرس", "relation": "patient_of", "target": "يشرح"}],
        {"role": "agent_action_patient", "domain": "education", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "education"]
    ),
    (
        "الاحتكاك يسبب الحرارة التي تذيب الجليد.",
        [{"id": "الاحتكاك", "type": "cause"}, {"id": "الحرارة", "type": "intermediate_effect"}, {"id": "الجليد", "type": "patient"}],
        [{"source": "الاحتكاك", "relation": "causes", "target": "الحرارة"}, {"source": "الحرارة", "relation": "causes", "target": "ذوبان الجليد"}],
        {"role": "causal_chain", "domain": "physics", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "science", "causal_chain"]
    ),
    (
        "الطبيب يفحص المريض بالأجهزة في المستشفى.",
        [{"id": "الطبيب", "type": "agent"}, {"id": "المريض", "type": "patient"}, {"id": "الأجهزة", "type": "instrument"}, {"id": "المستشفى", "type": "place"}],
        [{"source": "الطبيب", "relation": "agent_of", "target": "يفحص"}, {"source": "المريض", "relation": "patient_of", "target": "يفحص"}, {"source": "المستشفى", "relation": "place_of", "target": "يفحص"}],
        {"role": "agent_patient_place", "domain": "medicine", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "medicine"]
    ),
    (
        "النموذج يدّعي اليقين دون دليل — خطأ منهجي.",
        [{"id": "النموذج", "type": "agent"}, {"id": "اليقين", "type": "claim"}, {"id": "الدليل", "type": "evidence"}],
        [{"source": "النموذج", "relation": "claims", "target": "اليقين"}, {"source": "الدليل", "relation": "missing_for", "target": "اليقين"}],
        {"role": "adversarial_claim", "domain": "epistemology", "certainty": "suspend"},
        "suspend_judgment", "adversarial", ["graph_vector_composition", "adversarial", "evidence_certainty"]
    ),
    (
        "الزكاة ركن ديني وأداة اقتصادية لتوزيع الثروة.",
        [{"id": "الزكاة", "type": "concept"}, {"id": "الركن_الديني", "type": "domain_marker"}, {"id": "توزيع_الثروة", "type": "effect"}],
        [{"source": "الزكاة", "relation": "is_a", "target": "ركن_ديني"}, {"source": "الزكاة", "relation": "causes", "target": "توزيع_الثروة"}],
        {"role": "multi_domain", "domain": "religion_economics", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "economics"]
    ),
    (
        "الكاتب يؤلف الرواية بالقلم في مكتبه ليلاً.",
        [{"id": "الكاتب", "type": "agent"}, {"id": "الرواية", "type": "patient"}, {"id": "القلم", "type": "instrument"}, {"id": "المكتب", "type": "place"}, {"id": "ليلاً", "type": "time"}],
        [{"source": "الكاتب", "relation": "agent_of", "target": "يؤلف"}, {"source": "القلم", "relation": "instrument_of", "target": "يؤلف"}],
        {"role": "full_frame", "domain": "arts", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "arts"]
    ),
    (
        "الفساد يسبب انهيار المؤسسات مما يؤدي إلى الفوضى.",
        [{"id": "الفساد", "type": "cause"}, {"id": "انهيار_المؤسسات", "type": "intermediate"}, {"id": "الفوضى", "type": "final_effect"}],
        [{"source": "الفساد", "relation": "causes", "target": "انهيار_المؤسسات"}, {"source": "انهيار_المؤسسات", "relation": "causes", "target": "الفوضى"}],
        {"role": "causal_chain_complex", "domain": "politics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "politics", "causal_chain"]
    ),
    (
        "الميراث له أحكام شرعية وقانونية متشابكة.",
        [{"id": "الميراث", "type": "concept"}, {"id": "الحكم_الشرعي", "type": "domain_marker"}, {"id": "الحكم_القانوني", "type": "domain_marker"}],
        [{"source": "الميراث", "relation": "governed_by", "target": "الحكم_الشرعي"}, {"source": "الميراث", "relation": "governed_by", "target": "الحكم_القانوني"}],
        {"role": "multi_domain_overlap", "domain": "religion_law", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "law"]
    ),
    (
        "الرياضي يتدرب في الصالة صباحاً لتحقيق الفوز.",
        [{"id": "الرياضي", "type": "agent"}, {"id": "التدريب", "type": "action"}, {"id": "الصالة", "type": "place"}, {"id": "الفوز", "type": "goal"}],
        [{"source": "الرياضي", "relation": "agent_of", "target": "يتدرب"}, {"source": "التدريب", "relation": "leads_to", "target": "الفوز"}],
        {"role": "agent_goal_causal", "domain": "sports", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "sports"]
    ),
    (
        "البرلمان يسن القوانين بتصويت الأعضاء.",
        [{"id": "البرلمان", "type": "agent"}, {"id": "القوانين", "type": "patient"}, {"id": "تصويت_الأعضاء", "type": "instrument"}],
        [{"source": "البرلمان", "relation": "agent_of", "target": "يسن"}, {"source": "تصويت_الأعضاء", "relation": "instrument_of", "target": "يسن"}],
        {"role": "institutional_action", "domain": "politics_law", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "politics", "law"]
    ),
    (
        "العالم يفترض فرضية ثم يختبرها تجريبياً.",
        [{"id": "العالم", "type": "agent"}, {"id": "الفرضية", "type": "concept"}, {"id": "التجربة", "type": "instrument"}],
        [{"source": "العالم", "relation": "proposes", "target": "الفرضية"}, {"source": "التجربة", "relation": "tests", "target": "الفرضية"}],
        {"role": "scientific_method", "domain": "science", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "science"]
    ),
    (
        "المحقق يجمع الأدلة في مسرح الجريمة ليكشف الحقيقة.",
        [{"id": "المحقق", "type": "agent"}, {"id": "الأدلة", "type": "instrument"}, {"id": "مسرح_الجريمة", "type": "place"}, {"id": "الحقيقة", "type": "goal"}],
        [{"source": "المحقق", "relation": "agent_of", "target": "يجمع"}, {"source": "الأدلة", "relation": "leads_to", "target": "الحقيقة"}],
        {"role": "investigation_frame", "domain": "law", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "law"]
    ),
    (
        "المصدر المجهول والمصدر الموثوق يتعارضان.",
        [{"id": "المصدر_المجهول", "type": "source"}, {"id": "المصدر_الموثوق", "type": "source"}, {"id": "التعارض", "type": "relation"}],
        [{"source": "المصدر_المجهول", "relation": "conflicts_with", "target": "المصدر_الموثوق"}],
        {"role": "source_conflict", "domain": "epistemology", "certainty": "suspend"},
        "suspend_judgment", "adversarial", ["graph_vector_composition", "adversarial", "evidence_certainty"]
    ),
    (
        "الجراح يجري العملية بالمشرط في غرفة العمليات.",
        [{"id": "الجراح", "type": "agent"}, {"id": "العملية", "type": "patient"}, {"id": "المشرط", "type": "instrument"}, {"id": "غرفة_العمليات", "type": "place"}],
        [{"source": "الجراح", "relation": "agent_of", "target": "يجري"}, {"source": "المشرط", "relation": "instrument_of", "target": "يجري"}],
        {"role": "medical_procedure", "domain": "medicine", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "medicine"]
    ),
    (
        "التضخم يرفع الأسعار فيقل الطلب فيركد الاقتصاد.",
        [{"id": "التضخم", "type": "cause"}, {"id": "ارتفاع_الأسعار", "type": "intermediate"}, {"id": "انخفاض_الطلب", "type": "intermediate"}, {"id": "ركود_الاقتصاد", "type": "final_effect"}],
        [{"source": "التضخم", "relation": "causes", "target": "ارتفاع_الأسعار"}, {"source": "ارتفاع_الأسعار", "relation": "causes", "target": "انخفاض_الطلب"}, {"source": "انخفاض_الطلب", "relation": "causes", "target": "ركود_الاقتصاد"}],
        {"role": "economic_causal_chain", "domain": "economics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "economics", "causal_chain"]
    ),
    (
        "المعلم الماهر يستخدم أساليب متنوعة لتحفيز الطلاب.",
        [{"id": "المعلم", "type": "agent"}, {"id": "الأساليب", "type": "instrument"}, {"id": "الطلاب", "type": "patient"}, {"id": "التحفيز", "type": "goal"}],
        [{"source": "المعلم", "relation": "agent_of", "target": "يستخدم"}, {"source": "الأساليب", "relation": "instrument_of", "target": "يحفز"}],
        {"role": "pedagogical_frame", "domain": "education", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "education"]
    ),
    (
        "الفقيه يستنبط الحكم من النص بالقياس والاجتهاد.",
        [{"id": "الفقيه", "type": "agent"}, {"id": "الحكم", "type": "patient"}, {"id": "النص", "type": "source"}, {"id": "القياس", "type": "instrument"}, {"id": "الاجتهاد", "type": "instrument"}],
        [{"source": "الفقيه", "relation": "agent_of", "target": "يستنبط"}, {"source": "النص", "relation": "source_of", "target": "الحكم"}, {"source": "القياس", "relation": "instrument_of", "target": "يستنبط"}],
        {"role": "fiqh_derivation", "domain": "religion_fiqh", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "shari", "fiqh"]
    ),
    (
        "الشركة تنتج المنتج بالآلات في المصنع ثم تبيعه في السوق.",
        [{"id": "الشركة", "type": "agent"}, {"id": "المنتج", "type": "patient"}, {"id": "الآلات", "type": "instrument"}, {"id": "المصنع", "type": "place"}, {"id": "السوق", "type": "place"}],
        [{"source": "الشركة", "relation": "agent_of", "target": "تنتج"}, {"source": "المنتج", "relation": "sold_in", "target": "السوق"}],
        {"role": "production_sales_chain", "domain": "economics", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "economics"]
    ),
    (
        "نموذج الذكاء الاصطناعي يولد استنتاجات لكنه ليس مصدراً.",
        [{"id": "نموذج_AI", "type": "tool"}, {"id": "الاستنتاجات", "type": "output"}, {"id": "المصدر", "type": "concept"}],
        [{"source": "نموذج_AI", "relation": "generates", "target": "الاستنتاجات"}, {"source": "نموذج_AI", "relation": "is_not", "target": "مصدر_موثوق"}],
        {"role": "tool_limitation", "domain": "epistemology", "certainty": "certain"},
        "certain_knowledge", "adversarial", ["graph_vector_composition", "adversarial", "tool_not_evidence"]
    ),
    # Continue with 80 more examples
    (
        "الباحث يحلل البيانات بالإحصاء ليستخلص نتائج.",
        [{"id": "الباحث", "type": "agent"}, {"id": "البيانات", "type": "patient"}, {"id": "الإحصاء", "type": "instrument"}, {"id": "النتائج", "type": "goal"}],
        [{"source": "الباحث", "relation": "agent_of", "target": "يحلل"}, {"source": "الإحصاء", "relation": "instrument_of", "target": "يحلل"}],
        {"role": "research_analysis", "domain": "science", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "science"]
    ),
    (
        "القاضي يطبق القانون بناءً على الأدلة.",
        [{"id": "القاضي", "type": "agent"}, {"id": "القانون", "type": "instrument"}, {"id": "الأدلة", "type": "basis"}],
        [{"source": "القاضي", "relation": "agent_of", "target": "يطبق"}, {"source": "الأدلة", "relation": "basis_of", "target": "التطبيق"}],
        {"role": "judicial_action", "domain": "law", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "law"]
    ),
    (
        "المزارع يزرع القمح في الربيع ويحصده في الصيف.",
        [{"id": "المزارع", "type": "agent"}, {"id": "القمح", "type": "patient"}, {"id": "الربيع", "type": "time_plant"}, {"id": "الصيف", "type": "time_harvest"}],
        [{"source": "المزارع", "relation": "plants_in", "target": "الربيع"}, {"source": "المزارع", "relation": "harvests_in", "target": "الصيف"}],
        {"role": "temporal_sequence", "domain": "agriculture", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "agriculture"]
    ),
    (
        "الإجماع العلمي يمنح الفرضية مصداقية أعلى.",
        [{"id": "الإجماع_العلمي", "type": "concept"}, {"id": "الفرضية", "type": "concept"}, {"id": "المصداقية", "type": "property"}],
        [{"source": "الإجماع_العلمي", "relation": "increases", "target": "المصداقية"}, {"source": "المصداقية", "relation": "of", "target": "الفرضية"}],
        {"role": "epistemic_upgrade", "domain": "science_epistemology", "certainty": "strong"},
        "strong_knowledge", "hard", ["graph_vector_composition", "science", "evidence_certainty"]
    ),
    (
        "الحاكم يسن القانون لتحقيق العدل في المجتمع.",
        [{"id": "الحاكم", "type": "agent"}, {"id": "القانون", "type": "patient"}, {"id": "العدل", "type": "goal"}, {"id": "المجتمع", "type": "beneficiary"}],
        [{"source": "الحاكم", "relation": "agent_of", "target": "يسن"}, {"source": "القانون", "relation": "achieves", "target": "العدل"}],
        {"role": "governance_frame", "domain": "politics_law", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "politics", "law"]
    ),
    (
        "النهر يروي الحقول التي تنتج الغذاء.",
        [{"id": "النهر", "type": "agent"}, {"id": "الحقول", "type": "patient"}, {"id": "الغذاء", "type": "final_product"}],
        [{"source": "النهر", "relation": "irrigates", "target": "الحقول"}, {"source": "الحقول", "relation": "produces", "target": "الغذاء"}],
        {"role": "natural_causal_chain", "domain": "environment", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "environment"]
    ),
    (
        "الطالب يحفظ النص ليجتاز الامتحان.",
        [{"id": "الطالب", "type": "agent"}, {"id": "النص", "type": "patient"}, {"id": "الامتحان", "type": "goal"}],
        [{"source": "الطالب", "relation": "memorizes", "target": "النص"}, {"source": "الحفظ", "relation": "enables", "target": "الاجتياز"}],
        {"role": "learning_goal", "domain": "education", "certainty": "probable"},
        "probable_knowledge", "easy", ["graph_vector_composition", "education"]
    ),
    (
        "العقد يلزم الطرفين بالأداء وإلا تترتب العقوبة.",
        [{"id": "العقد", "type": "instrument"}, {"id": "الطرف_الأول", "type": "agent"}, {"id": "الطرف_الثاني", "type": "agent"}, {"id": "الأداء", "type": "obligation"}, {"id": "العقوبة", "type": "consequence"}],
        [{"source": "العقد", "relation": "obligates", "target": "الأداء"}, {"source": "الإخلال", "relation": "causes", "target": "العقوبة"}],
        {"role": "legal_obligation_chain", "domain": "law", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "law"]
    ),
    (
        "التوبة تمحو الذنب في الفقه الإسلامي.",
        [{"id": "التوبة", "type": "action"}, {"id": "الذنب", "type": "patient"}, {"id": "المحو", "type": "effect"}],
        [{"source": "التوبة", "relation": "causes", "target": "المحو"}, {"source": "المحو", "relation": "of", "target": "الذنب"}],
        {"role": "religious_effect", "domain": "religion_fiqh", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "shari"]
    ),
    (
        "الشبكة العصبية الاصطناعية تتعلم من البيانات.",
        [{"id": "الشبكة_العصبية", "type": "agent"}, {"id": "البيانات", "type": "source"}, {"id": "التعلم", "type": "process"}],
        [{"source": "الشبكة_العصبية", "relation": "learns_from", "target": "البيانات"}],
        {"role": "ml_learning", "domain": "technology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "technology"]
    ),
    (
        "الحرب تدمر البنية التحتية مما يزيد الفقر.",
        [{"id": "الحرب", "type": "cause"}, {"id": "البنية_التحتية", "type": "patient"}, {"id": "الفقر", "type": "final_effect"}],
        [{"source": "الحرب", "relation": "destroys", "target": "البنية_التحتية"}, {"source": "الدمار", "relation": "causes", "target": "الفقر"}],
        {"role": "war_causal_chain", "domain": "politics_economics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "politics", "economics"]
    ),
    (
        "الشاعر ينظم القصيدة معبراً عن مشاعره.",
        [{"id": "الشاعر", "type": "agent"}, {"id": "القصيدة", "type": "patient"}, {"id": "المشاعر", "type": "source"}],
        [{"source": "الشاعر", "relation": "agent_of", "target": "ينظم"}, {"source": "المشاعر", "relation": "expressed_in", "target": "القصيدة"}],
        {"role": "artistic_expression", "domain": "arts", "certainty": "certain"},
        "certain_knowledge", "easy", ["graph_vector_composition", "arts"]
    ),
    (
        "البيانات غير الكاملة تؤدي إلى استنتاجات خاطئة.",
        [{"id": "البيانات_الناقصة", "type": "cause"}, {"id": "الاستنتاجات_الخاطئة", "type": "effect"}],
        [{"source": "البيانات_الناقصة", "relation": "causes", "target": "الاستنتاجات_الخاطئة"}],
        {"role": "data_quality_risk", "domain": "epistemology", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "evidence_certainty"]
    ),
    (
        "المحكمة الدولية تحاكم الأفراد على جرائم الحرب.",
        [{"id": "المحكمة_الدولية", "type": "agent"}, {"id": "الأفراد", "type": "patient"}, {"id": "جرائم_الحرب", "type": "charge"}],
        [{"source": "المحكمة_الدولية", "relation": "prosecutes", "target": "الأفراد"}, {"source": "جرائم_الحرب", "relation": "charged_for", "target": "المحاكمة"}],
        {"role": "international_law_frame", "domain": "law_politics", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "law", "politics"]
    ),
    (
        "الأم تربي أطفالها بالحب والانضباط.",
        [{"id": "الأم", "type": "agent"}, {"id": "الأطفال", "type": "patient"}, {"id": "الحب", "type": "instrument"}, {"id": "الانضباط", "type": "instrument"}],
        [{"source": "الأم", "relation": "raises", "target": "الأطفال"}, {"source": "الحب", "relation": "instrument_of", "target": "التربية"}],
        {"role": "parenting_frame", "domain": "social", "certainty": "probable"},
        "probable_knowledge", "easy", ["graph_vector_composition", "social"]
    ),
    (
        "المهندس يصمم الجسر مراعياً قوانين الفيزياء والحمولة.",
        [{"id": "المهندس", "type": "agent"}, {"id": "الجسر", "type": "patient"}, {"id": "قوانين_الفيزياء", "type": "constraint"}, {"id": "الحمولة", "type": "constraint"}],
        [{"source": "المهندس", "relation": "designs", "target": "الجسر"}, {"source": "قوانين_الفيزياء", "relation": "constrains", "target": "التصميم"}],
        {"role": "engineering_design", "domain": "science_technology", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "science", "technology"]
    ),
    (
        "الدواء يعالج المرض لكن قد يسبب آثاراً جانبية.",
        [{"id": "الدواء", "type": "instrument"}, {"id": "المرض", "type": "target"}, {"id": "الآثار_الجانبية", "type": "risk"}],
        [{"source": "الدواء", "relation": "treats", "target": "المرض"}, {"source": "الدواء", "relation": "may_cause", "target": "الآثار_الجانبية"}],
        {"role": "medical_tradeoff", "domain": "medicine", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "medicine"]
    ),
    (
        "الصحفي ينشر الخبر الموثوق ويتجنب الإشاعات.",
        [{"id": "الصحفي", "type": "agent"}, {"id": "الخبر_الموثوق", "type": "patient"}, {"id": "الإشاعات", "type": "forbidden"}],
        [{"source": "الصحفي", "relation": "publishes", "target": "الخبر_الموثوق"}, {"source": "الصحفي", "relation": "avoids", "target": "الإشاعات"}],
        {"role": "journalism_ethics", "domain": "media_ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "ethics", "media"]
    ),
    (
        "البيئة الملوثة تسبب أمراضاً تكلف الاقتصاد.",
        [{"id": "البيئة_الملوثة", "type": "cause"}, {"id": "الأمراض", "type": "intermediate"}, {"id": "تكلفة_الاقتصاد", "type": "final_effect"}],
        [{"source": "البيئة_الملوثة", "relation": "causes", "target": "الأمراض"}, {"source": "الأمراض", "relation": "costs", "target": "الاقتصاد"}],
        {"role": "environment_economics_chain", "domain": "environment_economics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "environment", "economics"]
    ),
    (
        "الحكمة تقتضي التثبت قبل الحكم.",
        [{"id": "الحكمة", "type": "concept"}, {"id": "التثبت", "type": "action"}, {"id": "الحكم", "type": "action"}],
        [{"source": "الحكمة", "relation": "requires", "target": "التثبت"}, {"source": "التثبت", "relation": "precedes", "target": "الحكم"}],
        {"role": "epistemic_principle", "domain": "epistemology_ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "ethics", "evidence_certainty"]
    ),
    (
        "الصلاة تنهى عن الفحشاء والمنكر.",
        [{"id": "الصلاة", "type": "action"}, {"id": "الفحشاء", "type": "forbidden"}, {"id": "المنكر", "type": "forbidden"}],
        [{"source": "الصلاة", "relation": "prevents", "target": "الفحشاء"}, {"source": "الصلاة", "relation": "prevents", "target": "المنكر"}],
        {"role": "religious_ethical_function", "domain": "religion_ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "shari", "ethics"]
    ),
    (
        "الخوارزمية تعالج المدخلات وتنتج مخرجات محددة.",
        [{"id": "الخوارزمية", "type": "agent"}, {"id": "المدخلات", "type": "patient"}, {"id": "المخرجات", "type": "output"}],
        [{"source": "الخوارزمية", "relation": "processes", "target": "المدخلات"}, {"source": "المعالجة", "relation": "produces", "target": "المخرجات"}],
        {"role": "algorithmic_process", "domain": "technology", "certainty": "certain"},
        "certain_knowledge", "easy", ["graph_vector_composition", "technology"]
    ),
    (
        "التعليم العالي يرفع الإنتاجية ويقلل البطالة.",
        [{"id": "التعليم_العالي", "type": "cause"}, {"id": "الإنتاجية", "type": "positive_effect"}, {"id": "البطالة", "type": "reduced_effect"}],
        [{"source": "التعليم_العالي", "relation": "increases", "target": "الإنتاجية"}, {"source": "التعليم_العالي", "relation": "reduces", "target": "البطالة"}],
        {"role": "education_economics_link", "domain": "education_economics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "education", "economics"]
    ),
    (
        "الحكم الفقهي يختلف باختلاف المذهب والسياق.",
        [{"id": "الحكم_الفقهي", "type": "concept"}, {"id": "المذهب", "type": "variable"}, {"id": "السياق", "type": "variable"}],
        [{"source": "الحكم_الفقهي", "relation": "varies_by", "target": "المذهب"}, {"source": "الحكم_الفقهي", "relation": "varies_by", "target": "السياق"}],
        {"role": "fiqh_variability", "domain": "religion_fiqh", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "fiqh"]
    ),
    (
        "المؤسسة تعتمد على كفاءة موظفيها لتحقيق أهدافها.",
        [{"id": "المؤسسة", "type": "agent"}, {"id": "كفاءة_الموظفين", "type": "instrument"}, {"id": "الأهداف", "type": "goal"}],
        [{"source": "المؤسسة", "relation": "depends_on", "target": "كفاءة_الموظفين"}, {"source": "الكفاءة", "relation": "achieves", "target": "الأهداف"}],
        {"role": "institutional_dependency", "domain": "management", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "management"]
    ),
    (
        "الغذاء الحلال يمتثل لأحكام الفقه الإسلامي.",
        [{"id": "الغذاء_الحلال", "type": "concept"}, {"id": "أحكام_الفقه", "type": "constraint"}, {"id": "الامتثال", "type": "relation"}],
        [{"source": "الغذاء_الحلال", "relation": "complies_with", "target": "أحكام_الفقه"}],
        {"role": "halal_compliance", "domain": "religion_fiqh", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "shari"]
    ),
    (
        "الناخب يختار ممثله الذي يسن القانون لصالحه.",
        [{"id": "الناخب", "type": "agent"}, {"id": "الممثل", "type": "intermediary"}, {"id": "القانون", "type": "patient"}, {"id": "المصلحة", "type": "goal"}],
        [{"source": "الناخب", "relation": "elects", "target": "الممثل"}, {"source": "الممثل", "relation": "enacts", "target": "القانون"}, {"source": "القانون", "relation": "serves", "target": "المصلحة"}],
        {"role": "democratic_chain", "domain": "politics_law", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "politics", "law"]
    ),
    (
        "الطاقة الشمسية تقلل الانبعاثات وتوفر التكاليف.",
        [{"id": "الطاقة_الشمسية", "type": "instrument"}, {"id": "الانبعاثات", "type": "reduced_effect"}, {"id": "التكاليف", "type": "reduced_effect"}],
        [{"source": "الطاقة_الشمسية", "relation": "reduces", "target": "الانبعاثات"}, {"source": "الطاقة_الشمسية", "relation": "saves", "target": "التكاليف"}],
        {"role": "renewable_benefits", "domain": "environment_economics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "environment", "economics"]
    ),
    (
        "النص القرآني قطعي الثبوت قد يكون ظني الدلالة.",
        [{"id": "النص_القرآني", "type": "source"}, {"id": "قطعية_الثبوت", "type": "property"}, {"id": "ظنية_الدلالة", "type": "property"}],
        [{"source": "النص_القرآني", "relation": "has", "target": "قطعية_الثبوت"}, {"source": "النص_القرآني", "relation": "may_have", "target": "ظنية_الدلالة"}],
        {"role": "usul_fiqh_analysis", "domain": "religion_fiqh", "certainty": "certain"},
        "certain_knowledge", "adversarial", ["graph_vector_composition", "shari", "usul_fiqh"]
    ),
    (
        "البيانات الضخمة تكشف الأنماط الخفية في السلوك البشري.",
        [{"id": "البيانات_الضخمة", "type": "instrument"}, {"id": "الأنماط", "type": "output"}, {"id": "السلوك_البشري", "type": "domain"}],
        [{"source": "البيانات_الضخمة", "relation": "reveals", "target": "الأنماط"}, {"source": "الأنماط", "relation": "in", "target": "السلوك_البشري"}],
        {"role": "data_pattern_discovery", "domain": "technology_social", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "technology", "social"]
    ),
    (
        "الأسرة هي اللبنة الأولى في بناء المجتمع.",
        [{"id": "الأسرة", "type": "concept"}, {"id": "المجتمع", "type": "whole"}, {"id": "اللبنة_الأولى", "type": "role"}],
        [{"source": "الأسرة", "relation": "is_base_of", "target": "المجتمع"}],
        {"role": "social_structure", "domain": "social_ethics", "certainty": "probable"},
        "probable_knowledge", "easy", ["graph_vector_composition", "social"]
    ),
    (
        "القياس بلا علة مشتركة خطأ أصولي.",
        [{"id": "القياس", "type": "action"}, {"id": "العلة_المشتركة", "type": "requirement"}, {"id": "الخطأ_الأصولي", "type": "consequence"}],
        [{"source": "القياس", "relation": "requires", "target": "العلة_المشتركة"}, {"source": "غياب_العلة", "relation": "causes", "target": "الخطأ_الأصولي"}],
        {"role": "usul_error_detection", "domain": "fiqh_epistemology", "certainty": "certain"},
        "certain_knowledge", "adversarial", ["graph_vector_composition", "shari", "adversarial"]
    ),
    (
        "التقنية تتطور بسرعة فتسبق التشريع.",
        [{"id": "التقنية", "type": "agent"}, {"id": "التشريع", "type": "concept"}, {"id": "التقدم", "type": "process"}],
        [{"source": "التقنية", "relation": "evolves_faster_than", "target": "التشريع"}],
        {"role": "technology_law_gap", "domain": "technology_law", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "technology", "law"]
    ),
    (
        "الحوار الحضاري يقلص الصراعات ويعزز التفاهم.",
        [{"id": "الحوار_الحضاري", "type": "action"}, {"id": "الصراعات", "type": "reduced"}, {"id": "التفاهم", "type": "increased"}],
        [{"source": "الحوار_الحضاري", "relation": "reduces", "target": "الصراعات"}, {"source": "الحوار_الحضاري", "relation": "enhances", "target": "التفاهم"}],
        {"role": "intercultural_dialogue", "domain": "culture_ethics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "culture", "ethics"]
    ),
    (
        "العالِم يطرح الفرضية ثم يختبرها ثم ينشرها ثم يراجعها.",
        [{"id": "العالِم", "type": "agent"}, {"id": "الفرضية", "type": "concept"}, {"id": "الاختبار", "type": "process"}, {"id": "النشر", "type": "process"}, {"id": "المراجعة", "type": "process"}],
        [{"source": "العالِم", "relation": "proposes", "target": "الفرضية"}, {"source": "الفرضية", "relation": "goes_through", "target": "الاختبار"}, {"source": "الاختبار", "relation": "leads_to", "target": "النشر"}, {"source": "النشر", "relation": "leads_to", "target": "المراجعة"}],
        {"role": "scientific_process_chain", "domain": "science", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "science"]
    ),
    (
        "المتهم بريء حتى تثبت إدانته بالأدلة.",
        [{"id": "المتهم", "type": "concept"}, {"id": "البراءة", "type": "default_state"}, {"id": "الأدلة", "type": "required"}, {"id": "الإدانة", "type": "conclusion"}],
        [{"source": "المتهم", "relation": "presumed", "target": "بريء"}, {"source": "الأدلة", "relation": "required_for", "target": "الإدانة"}],
        {"role": "presumption_of_innocence", "domain": "law", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "law"]
    ),
    (
        "الثقافة والهوية يتشكلان عبر الزمن والتفاعل.",
        [{"id": "الثقافة", "type": "concept"}, {"id": "الهوية", "type": "concept"}, {"id": "الزمن", "type": "factor"}, {"id": "التفاعل", "type": "factor"}],
        [{"source": "الزمن", "relation": "shapes", "target": "الثقافة"}, {"source": "التفاعل", "relation": "shapes", "target": "الهوية"}],
        {"role": "cultural_identity_formation", "domain": "culture_social", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "culture", "social"]
    ),
    (
        "المقيم الأجنبي يخضع لقانون البلد المضيف.",
        [{"id": "المقيم_الأجنبي", "type": "agent"}, {"id": "قانون_البلد_المضيف", "type": "constraint"}],
        [{"source": "المقيم_الأجنبي", "relation": "subject_to", "target": "قانون_البلد_المضيف"}],
        {"role": "jurisdictional_constraint", "domain": "law", "certainty": "certain"},
        "certain_knowledge", "easy", ["graph_vector_composition", "law"]
    ),
    (
        "التربية الإسلامية تجمع العلم والأخلاق.",
        [{"id": "التربية_الإسلامية", "type": "concept"}, {"id": "العلم", "type": "component"}, {"id": "الأخلاق", "type": "component"}],
        [{"source": "التربية_الإسلامية", "relation": "integrates", "target": "العلم"}, {"source": "التربية_الإسلامية", "relation": "integrates", "target": "الأخلاق"}],
        {"role": "islamic_education_synthesis", "domain": "religion_education", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "shari", "education"]
    ),
    (
        "المنافسة الاقتصادية تحفز الابتكار وتخفض الأسعار.",
        [{"id": "المنافسة", "type": "cause"}, {"id": "الابتكار", "type": "positive_effect"}, {"id": "انخفاض_الأسعار", "type": "positive_effect"}],
        [{"source": "المنافسة", "relation": "stimulates", "target": "الابتكار"}, {"source": "المنافسة", "relation": "reduces", "target": "الأسعار"}],
        {"role": "market_competition_effects", "domain": "economics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "economics"]
    ),
    (
        "الرياضة تجمع بين اللياقة والمتعة والمنافسة.",
        [{"id": "الرياضة", "type": "concept"}, {"id": "اللياقة", "type": "benefit"}, {"id": "المتعة", "type": "benefit"}, {"id": "المنافسة", "type": "component"}],
        [{"source": "الرياضة", "relation": "provides", "target": "اللياقة"}, {"source": "الرياضة", "relation": "provides", "target": "المتعة"}, {"source": "الرياضة", "relation": "includes", "target": "المنافسة"}],
        {"role": "multi_benefit_concept", "domain": "sports_social", "certainty": "certain"},
        "certain_knowledge", "easy", ["graph_vector_composition", "sports"]
    ),
    (
        "النظرية الاقتصادية لها قيود تطبيقية في الواقع.",
        [{"id": "النظرية_الاقتصادية", "type": "concept"}, {"id": "القيود_التطبيقية", "type": "limitation"}, {"id": "الواقع", "type": "context"}],
        [{"source": "النظرية", "relation": "has", "target": "قيود"}, {"source": "القيود", "relation": "in", "target": "الواقع"}],
        {"role": "theory_practice_gap", "domain": "economics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "economics"]
    ),
    (
        "المسؤولية الاجتماعية للشركات تجمع الأرباح والأخلاق.",
        [{"id": "المسؤولية_الاجتماعية", "type": "concept"}, {"id": "الأرباح", "type": "goal"}, {"id": "الأخلاق", "type": "constraint"}],
        [{"source": "المسؤولية_الاجتماعية", "relation": "balances", "target": "الأرباح"}, {"source": "المسؤولية_الاجتماعية", "relation": "requires", "target": "الأخلاق"}],
        {"role": "csr_balance", "domain": "economics_ethics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "economics", "ethics"]
    ),
    (
        "التقييم يعتمد على معيار موضوعي لا على الرأي الشخصي.",
        [{"id": "التقييم", "type": "process"}, {"id": "المعيار_الموضوعي", "type": "basis"}, {"id": "الرأي_الشخصي", "type": "excluded"}],
        [{"source": "التقييم", "relation": "based_on", "target": "المعيار_الموضوعي"}, {"source": "التقييم", "relation": "excludes", "target": "الرأي_الشخصي"}],
        {"role": "objective_evaluation", "domain": "epistemology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "evidence_certainty"]
    ),
    (
        "الحد الشرعي يتطلب شروطاً دقيقة للتطبيق.",
        [{"id": "الحد_الشرعي", "type": "concept"}, {"id": "الشروط", "type": "requirement"}, {"id": "التطبيق", "type": "action"}],
        [{"source": "الحد_الشرعي", "relation": "requires", "target": "الشروط"}, {"source": "الشروط", "relation": "enables", "target": "التطبيق"}],
        {"role": "hudud_conditions", "domain": "religion_fiqh_law", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "law"]
    ),
    (
        "الأزمة المالية تبدأ بفقاعة ثم انهيار ثم ركود.",
        [{"id": "الأزمة_المالية", "type": "concept"}, {"id": "الفقاعة", "type": "stage1"}, {"id": "الانهيار", "type": "stage2"}, {"id": "الركود", "type": "stage3"}],
        [{"source": "الفقاعة", "relation": "leads_to", "target": "الانهيار"}, {"source": "الانهيار", "relation": "leads_to", "target": "الركود"}],
        {"role": "financial_crisis_stages", "domain": "economics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "economics"]
    ),
    (
        "الحكومة الديمقراطية تستمد شرعيتها من الشعب.",
        [{"id": "الحكومة_الديمقراطية", "type": "agent"}, {"id": "الشعب", "type": "source"}, {"id": "الشرعية", "type": "property"}],
        [{"source": "الحكومة_الديمقراطية", "relation": "derives_legitimacy_from", "target": "الشعب"}],
        {"role": "democratic_legitimacy", "domain": "politics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "politics"]
    ),
    (
        "الذاكرة تحتاج مراجعة منتظمة للتثبيت.",
        [{"id": "الذاكرة", "type": "concept"}, {"id": "المراجعة_المنتظمة", "type": "action"}, {"id": "التثبيت", "type": "goal"}],
        [{"source": "الذاكرة", "relation": "requires", "target": "المراجعة"}, {"source": "المراجعة", "relation": "achieves", "target": "التثبيت"}],
        {"role": "memory_consolidation", "domain": "science_education", "certainty": "probable"},
        "probable_knowledge", "easy", ["graph_vector_composition", "science", "education"]
    ),
    (
        "التفكير النقدي يكشف الأخطاء المنطقية في الحجج.",
        [{"id": "التفكير_النقدي", "type": "skill"}, {"id": "الأخطاء_المنطقية", "type": "target"}, {"id": "الحجج", "type": "context"}],
        [{"source": "التفكير_النقدي", "relation": "detects", "target": "الأخطاء_المنطقية"}, {"source": "الأخطاء", "relation": "in", "target": "الحجج"}],
        {"role": "critical_thinking", "domain": "epistemology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "epistemology"]
    ),
    (
        "الإجماع الفقهي حجة قاطعة في أصول الفقه.",
        [{"id": "الإجماع_الفقهي", "type": "concept"}, {"id": "الحجة_القاطعة", "type": "status"}, {"id": "أصول_الفقه", "type": "domain"}],
        [{"source": "الإجماع_الفقهي", "relation": "is_a", "target": "حجة_قاطعة"}, {"source": "الحجة", "relation": "in", "target": "أصول_الفقه"}],
        {"role": "ijmaa_authority", "domain": "fiqh_usul", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "usul_fiqh"]
    ),
    (
        "المعرفة التراكمية تبنى على إضافات الأجيال السابقة.",
        [{"id": "المعرفة_التراكمية", "type": "concept"}, {"id": "إضافات_الأجيال", "type": "source"}],
        [{"source": "المعرفة_التراكمية", "relation": "built_on", "target": "إضافات_الأجيال"}],
        {"role": "cumulative_knowledge", "domain": "epistemology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "epistemology"]
    ),
    (
        "الشك المنهجي ينبغي أن يسبق اليقين.",
        [{"id": "الشك_المنهجي", "type": "action"}, {"id": "اليقين", "type": "goal"}],
        [{"source": "الشك_المنهجي", "relation": "precedes", "target": "اليقين"}],
        {"role": "methodological_doubt", "domain": "philosophy_epistemology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "philosophy", "evidence_certainty"]
    ),
    (
        "الطاقة النووية مصدر كثيف لكنها تحمل مخاطر.",
        [{"id": "الطاقة_النووية", "type": "concept"}, {"id": "الكثافة", "type": "benefit"}, {"id": "المخاطر", "type": "risk"}],
        [{"source": "الطاقة_النووية", "relation": "provides", "target": "الكثافة"}, {"source": "الطاقة_النووية", "relation": "carries", "target": "المخاطر"}],
        {"role": "technology_tradeoff", "domain": "science_ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "science", "ethics"]
    ),
    (
        "الربط بين البحث والسياسة يحسن القرارات العامة.",
        [{"id": "البحث_العلمي", "type": "source"}, {"id": "السياسة", "type": "context"}, {"id": "القرارات_العامة", "type": "output"}],
        [{"source": "البحث_العلمي", "relation": "informs", "target": "السياسة"}, {"source": "السياسة", "relation": "produces", "target": "القرارات_العامة"}],
        {"role": "evidence_policy_link", "domain": "science_politics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "science", "politics"]
    ),
    (
        "التعاون الدولي ضروري للتصدي لتغير المناخ.",
        [{"id": "التعاون_الدولي", "type": "action"}, {"id": "تغير_المناخ", "type": "challenge"}],
        [{"source": "التعاون_الدولي", "relation": "required_for", "target": "مواجهة_تغير_المناخ"}],
        {"role": "global_cooperation", "domain": "environment_politics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "environment", "politics"]
    ),
    (
        "الرعاية الصحية الشاملة حق اجتماعي في دول كثيرة.",
        [{"id": "الرعاية_الصحية", "type": "concept"}, {"id": "الحق_الاجتماعي", "type": "status"}],
        [{"source": "الرعاية_الصحية", "relation": "recognized_as", "target": "حق_اجتماعي"}],
        {"role": "healthcare_rights", "domain": "law_social", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "law", "social"]
    ),
    (
        "المنطق الرياضي لا يثبت القضايا الأخلاقية.",
        [{"id": "المنطق_الرياضي", "type": "tool"}, {"id": "القضايا_الأخلاقية", "type": "domain"}],
        [{"source": "المنطق_الرياضي", "relation": "cannot_prove", "target": "القضايا_الأخلاقية"}],
        {"role": "domain_limitation", "domain": "philosophy_math", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "philosophy", "ethics"]
    ),
    (
        "التعليم المبكر يرسم مسار التنمية الفردية.",
        [{"id": "التعليم_المبكر", "type": "cause"}, {"id": "مسار_التنمية_الفردية", "type": "effect"}],
        [{"source": "التعليم_المبكر", "relation": "shapes", "target": "مسار_التنمية"}],
        {"role": "early_education_impact", "domain": "education_social", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "education"]
    ),
    (
        "الحرية والمسؤولية وجهان لعملة واحدة.",
        [{"id": "الحرية", "type": "concept"}, {"id": "المسؤولية", "type": "concept"}, {"id": "الترابط", "type": "relation"}],
        [{"source": "الحرية", "relation": "entails", "target": "المسؤولية"}],
        {"role": "freedom_responsibility_link", "domain": "ethics_philosophy", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "ethics", "philosophy"]
    ),
    (
        "الثقة في المؤسسات تبنى بالشفافية والمساءلة.",
        [{"id": "الثقة", "type": "goal"}, {"id": "المؤسسات", "type": "agent"}, {"id": "الشفافية", "type": "instrument"}, {"id": "المساءلة", "type": "instrument"}],
        [{"source": "الشفافية", "relation": "builds", "target": "الثقة"}, {"source": "المساءلة", "relation": "builds", "target": "الثقة"}],
        {"role": "institutional_trust", "domain": "politics_ethics", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "politics", "ethics"]
    ),
    (
        "حكم الرضاع يترتب عليه تحريم المصاهرة.",
        [{"id": "حكم_الرضاع", "type": "cause"}, {"id": "تحريم_المصاهرة", "type": "effect"}],
        [{"source": "حكم_الرضاع", "relation": "causes", "target": "تحريم_المصاهرة"}],
        {"role": "fiqh_causal_ruling", "domain": "fiqh", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "fiqh"]
    ),
    (
        "الحضارات تتواصل عبر التجارة والمعرفة والحرب.",
        [{"id": "الحضارات", "type": "agent"}, {"id": "التجارة", "type": "channel"}, {"id": "المعرفة", "type": "channel"}, {"id": "الحرب", "type": "channel"}],
        [{"source": "الحضارات", "relation": "interact_through", "target": "التجارة"}, {"source": "الحضارات", "relation": "interact_through", "target": "المعرفة"}, {"source": "الحضارات", "relation": "interact_through", "target": "الحرب"}],
        {"role": "civilization_interaction", "domain": "history_culture", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "culture", "history"]
    ),
    (
        "القانون الجنائي يوازن بين العدل والردع.",
        [{"id": "القانون_الجنائي", "type": "concept"}, {"id": "العدل", "type": "goal"}, {"id": "الردع", "type": "goal"}],
        [{"source": "القانون_الجنائي", "relation": "balances", "target": "العدل"}, {"source": "القانون_الجنائي", "relation": "serves", "target": "الردع"}],
        {"role": "criminal_law_balance", "domain": "law", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "law"]
    ),
    (
        "الاعتراف بالخطأ شرط للتصحيح والتعلم.",
        [{"id": "الاعتراف_بالخطأ", "type": "action"}, {"id": "التصحيح", "type": "goal"}, {"id": "التعلم", "type": "goal"}],
        [{"source": "الاعتراف_بالخطأ", "relation": "enables", "target": "التصحيح"}, {"source": "التصحيح", "relation": "leads_to", "target": "التعلم"}],
        {"role": "error_correction_chain", "domain": "ethics_education", "certainty": "probable"},
        "probable_knowledge", "easy", ["graph_vector_composition", "ethics"]
    ),
    (
        "المستشار الأمين يقدم النصح حتى لو خالف مصلحته.",
        [{"id": "المستشار_الأمين", "type": "agent"}, {"id": "النصح_الصادق", "type": "action"}, {"id": "مصلحته", "type": "overridden"}],
        [{"source": "المستشار_الأمين", "relation": "provides", "target": "النصح_الصادق"}, {"source": "النصح", "relation": "prioritized_over", "target": "المصلحة_الشخصية"}],
        {"role": "advisor_ethics", "domain": "ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "ethics"]
    ),
    (
        "الشبكات الاجتماعية تشكل الرأي العام وتؤثر في السياسة.",
        [{"id": "الشبكات_الاجتماعية", "type": "agent"}, {"id": "الرأي_العام", "type": "patient"}, {"id": "السياسة", "type": "affected"}],
        [{"source": "الشبكات_الاجتماعية", "relation": "shapes", "target": "الرأي_العام"}, {"source": "الرأي_العام", "relation": "influences", "target": "السياسة"}],
        {"role": "social_media_politics_chain", "domain": "technology_politics", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "technology", "politics"]
    ),
    (
        "الوقف الخيري يجمع بين البر الديني والنفع الاجتماعي.",
        [{"id": "الوقف_الخيري", "type": "concept"}, {"id": "البر_الديني", "type": "component"}, {"id": "النفع_الاجتماعي", "type": "component"}],
        [{"source": "الوقف_الخيري", "relation": "combines", "target": "البر_الديني"}, {"source": "الوقف_الخيري", "relation": "provides", "target": "النفع_الاجتماعي"}],
        {"role": "waqf_dual_benefit", "domain": "religion_social", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "shari", "social"]
    ),
    (
        "الشهادة الواحدة غير الكافية تستوجب الإيقاف عن الحكم.",
        [{"id": "الشهادة_الواحدة", "type": "evidence"}, {"id": "الكفاية", "type": "threshold"}, {"id": "الإيقاف_عن_الحكم", "type": "action"}],
        [{"source": "الشهادة_الواحدة", "relation": "below", "target": "الكفاية"}, {"source": "نقص_الكفاية", "relation": "requires", "target": "الإيقاف"}],
        {"role": "evidence_threshold", "domain": "law_epistemology", "certainty": "certain"},
        "certain_knowledge", "adversarial", ["graph_vector_composition", "law", "evidence_certainty"]
    ),
    (
        "الدين والعلم يتقاطعان ولا يتناقضان ضرورةً.",
        [{"id": "الدين", "type": "domain"}, {"id": "العلم", "type": "domain"}, {"id": "التقاطع", "type": "relation"}],
        [{"source": "الدين", "relation": "intersects_with", "target": "العلم"}, {"source": "التناقض", "relation": "not_necessary", "target": "بين_الدين_والعلم"}],
        {"role": "religion_science_relation", "domain": "philosophy_religion", "certainty": "probable"},
        "probable_knowledge", "adversarial", ["graph_vector_composition", "philosophy", "religion", "science"]
    ),
    (
        "التعليم الإلكتروني يتيح الوصول ويقلل التكلفة.",
        [{"id": "التعليم_الإلكتروني", "type": "concept"}, {"id": "الوصول", "type": "benefit"}, {"id": "التكلفة", "type": "reduced_factor"}],
        [{"source": "التعليم_الإلكتروني", "relation": "increases", "target": "الوصول"}, {"source": "التعليم_الإلكتروني", "relation": "reduces", "target": "التكلفة"}],
        {"role": "elearning_benefits", "domain": "education_technology", "certainty": "probable"},
        "probable_knowledge", "medium", ["graph_vector_composition", "education", "technology"]
    ),
    (
        "الإفتاء بلا علم جهالة ومسؤولية دينية.",
        [{"id": "الإفتاء_بلا_علم", "type": "action"}, {"id": "الجهالة", "type": "property"}, {"id": "المسؤولية_الدينية", "type": "consequence"}],
        [{"source": "الإفتاء_بلا_علم", "relation": "is", "target": "جهالة"}, {"source": "الجهالة", "relation": "entails", "target": "المسؤولية_الدينية"}],
        {"role": "fatwa_responsibility", "domain": "religion_fiqh_ethics", "certainty": "certain"},
        "certain_knowledge", "adversarial", ["graph_vector_composition", "shari", "ethics"]
    ),
    (
        "المشاعر الإنسانية تؤثر في اتخاذ القرارات الاقتصادية.",
        [{"id": "المشاعر_الإنسانية", "type": "cause"}, {"id": "القرارات_الاقتصادية", "type": "affected"}],
        [{"source": "المشاعر_الإنسانية", "relation": "influences", "target": "القرارات_الاقتصادية"}],
        {"role": "behavioral_economics", "domain": "economics_psychology", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "economics", "science"]
    ),
    (
        "الحقوق المدنية تستوجب ضمانات دستورية.",
        [{"id": "الحقوق_المدنية", "type": "concept"}, {"id": "الضمانات_الدستورية", "type": "requirement"}],
        [{"source": "الحقوق_المدنية", "relation": "requires", "target": "الضمانات_الدستورية"}],
        {"role": "constitutional_rights", "domain": "law_politics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "law", "politics"]
    ),
    (
        "العقل والنقل مصدران للمعرفة الإسلامية.",
        [{"id": "العقل", "type": "source"}, {"id": "النقل", "type": "source"}, {"id": "المعرفة_الإسلامية", "type": "output"}],
        [{"source": "العقل", "relation": "contributes_to", "target": "المعرفة_الإسلامية"}, {"source": "النقل", "relation": "contributes_to", "target": "المعرفة_الإسلامية"}],
        {"role": "islamic_epistemology", "domain": "religion_philosophy", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "shari", "philosophy"]
    ),
    (
        "الصحة العامة تتطلب تنسيقاً بين الطب والسياسة والاقتصاد.",
        [{"id": "الصحة_العامة", "type": "concept"}, {"id": "الطب", "type": "domain"}, {"id": "السياسة", "type": "domain"}, {"id": "الاقتصاد", "type": "domain"}],
        [{"source": "الصحة_العامة", "relation": "requires_coordination_between", "target": "الطب"}, {"source": "الصحة_العامة", "relation": "requires_coordination_between", "target": "السياسة"}],
        {"role": "public_health_multi_domain", "domain": "medicine_politics_economics", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "medicine", "politics"]
    ),
    (
        "الفلسفة السياسية تسعى للإجابة عن شرعية السلطة.",
        [{"id": "الفلسفة_السياسية", "type": "domain"}, {"id": "شرعية_السلطة", "type": "question"}],
        [{"source": "الفلسفة_السياسية", "relation": "addresses", "target": "شرعية_السلطة"}],
        {"role": "political_philosophy_question", "domain": "philosophy_politics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "philosophy", "politics"]
    ),
    (
        "الجينوم البشري يحمل المعلومات الوراثية لكائن حي.",
        [{"id": "الجينوم_البشري", "type": "concept"}, {"id": "المعلومات_الوراثية", "type": "content"}, {"id": "الكائن_الحي", "type": "owner"}],
        [{"source": "الجينوم_البشري", "relation": "contains", "target": "المعلومات_الوراثية"}, {"source": "المعلومات", "relation": "defines", "target": "الكائن_الحي"}],
        {"role": "genetic_information", "domain": "science_biology", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "science"]
    ),
    (
        "المفسر يستخلص المعنى من السياق والنص والتاريخ.",
        [{"id": "المفسر", "type": "agent"}, {"id": "المعنى", "type": "output"}, {"id": "السياق", "type": "source"}, {"id": "النص", "type": "source"}, {"id": "التاريخ", "type": "source"}],
        [{"source": "المفسر", "relation": "extracts", "target": "المعنى"}, {"source": "السياق", "relation": "informs", "target": "التفسير"}],
        {"role": "hermeneutic_frame", "domain": "linguistics_religion", "certainty": "probable"},
        "probable_knowledge", "hard", ["graph_vector_composition", "linguistics", "religion"]
    ),
    (
        "الاتفاقيات الدولية تُلزم الدول الموقّعة بالتطبيق.",
        [{"id": "الاتفاقيات_الدولية", "type": "instrument"}, {"id": "الدول_الموقّعة", "type": "obligated"}],
        [{"source": "الاتفاقيات_الدولية", "relation": "obligates", "target": "الدول_الموقّعة"}],
        {"role": "international_treaty", "domain": "law_politics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "law", "politics"]
    ),
    (
        "الأمانة في العلم تقتضي الإفصاح عن القيود والشكوك.",
        [{"id": "الأمانة_العلمية", "type": "principle"}, {"id": "القيود", "type": "information"}, {"id": "الشكوك", "type": "information"}],
        [{"source": "الأمانة_العلمية", "relation": "requires_disclosure_of", "target": "القيود"}, {"source": "الأمانة_العلمية", "relation": "requires_disclosure_of", "target": "الشكوك"}],
        {"role": "scientific_integrity", "domain": "science_ethics", "certainty": "certain"},
        "certain_knowledge", "medium", ["graph_vector_composition", "science", "ethics"]
    ),
    (
        "حوكمة البيانات تحدد من يملك البيانات ومن يتحكم بها.",
        [{"id": "حوكمة_البيانات", "type": "concept"}, {"id": "الملكية", "type": "question"}, {"id": "التحكم", "type": "question"}],
        [{"source": "حوكمة_البيانات", "relation": "defines", "target": "الملكية"}, {"source": "حوكمة_البيانات", "relation": "defines", "target": "التحكم"}],
        {"role": "data_governance", "domain": "technology_law", "certainty": "certain"},
        "certain_knowledge", "hard", ["graph_vector_composition", "technology", "law"]
    ),
]


def build_l9_unit(idx, text, domains, certainty, difficulty, tags):
    return {
        "unit_id": f"L09-EX-{idx:04d}",
        "input_text": text,
        "level": 9,
        "target_layer": "domain_reasoning",
        "expected_frame": {
            "things": [],
            "properties": [],
            "actions": [],
            "agents": [],
            "patients": [],
            "instruments": [],
            "times": [],
            "places": [],
            "causes": [],
            "effects": [],
            "relations": [],
            "domains": domains,
            "evidence_need": ["domain_classification"],
            "certainty_policy": certainty,
            "warnings": [],
        },
        "expected_warnings": [],
        "forbidden_confusions": ["domain_conflation", "single_domain_bias"],
        "evidence_need": ["domain_classification"],
        "certainty_policy": certainty,
        "difficulty": difficulty,
        "tags": tags,
        "metadata": {"domains": domains},
    }


def build_l10_unit(idx, text, nodes, edges, vector_hint, certainty, difficulty, tags):
    vectors = [
        {"dimension": vector_hint.get("role", "role"), "value": 1.0},
        {"dimension": vector_hint.get("domain", "domain"), "value": 1.0},
        {"dimension": vector_hint.get("certainty", "certainty"), "value": 1.0},
    ]
    return {
        "unit_id": f"L10-EX-{idx:04d}",
        "input_text": text,
        "level": 10,
        "target_layer": "graph_vector_composition",
        "expected_frame": {
            "things": [n["id"] for n in nodes],
            "properties": [],
            "actions": [],
            "agents": [n["id"] for n in nodes if n.get("type") == "agent"],
            "patients": [n["id"] for n in nodes if n.get("type") == "patient"],
            "instruments": [n["id"] for n in nodes if n.get("type") == "instrument"],
            "times": [],
            "places": [],
            "causes": [n["id"] for n in nodes if n.get("type") == "cause"],
            "effects": [n["id"] for n in nodes if n.get("type") in ("effect", "final_effect", "intermediate")],
            "relations": [{"source": e["source"], "relation": e["relation"], "target": e["target"], "qualifier": None} for e in edges],
            "nodes": nodes,
            "edges": edges,
            "vectors": vectors,
            "evidence_need": ["graph_construction", "vector_composition"],
            "certainty_policy": certainty,
            "warnings": [],
        },
        "expected_warnings": [],
        "forbidden_confusions": ["flat_extraction", "missing_relations", "vector_collapse"],
        "evidence_need": ["graph_construction", "vector_composition"],
        "certainty_policy": certainty,
        "difficulty": difficulty,
        "tags": tags,
        "metadata": {"vector_hint": vector_hint},
    }


# Write level 9
l9_path = DATA_DIR / "level_09_domain_reasoning_ar.jsonl"
with open(l9_path, "w", encoding="utf-8") as f:
    for i, item in enumerate(LEVEL_9_EXAMPLES, start=1):
        text, domains, certainty, difficulty, tags = item
        unit = build_l9_unit(i, text, domains, certainty, difficulty, tags)
        f.write(json.dumps(unit, ensure_ascii=False) + "\n")
print(f"Level 9: {l9_path.name} written with {len(LEVEL_9_EXAMPLES)} examples")

# Write level 10
l10_path = DATA_DIR / "level_10_graph_vector_composition_ar.jsonl"
with open(l10_path, "w", encoding="utf-8") as f:
    for i, item in enumerate(LEVEL_10_EXAMPLES, start=1):
        text, nodes, edges, vector_hint, certainty, difficulty, tags = item
        unit = build_l10_unit(i, text, nodes, edges, vector_hint, certainty, difficulty, tags)
        f.write(json.dumps(unit, ensure_ascii=False) + "\n")
print(f"Level 10: {l10_path.name} written with {len(LEVEL_10_EXAMPLES)} examples")
print("Done generating levels 9 and 10!")
