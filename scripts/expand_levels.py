#!/usr/bin/env python3
"""Expand curriculum levels 1-8 from 50 to 100 examples each."""
import json
from pathlib import Path

DATA_DIR = Path("/home/runner/work/Salehan19-6-67/Salehan19-6-67/data/curriculum")

# Additional examples for each level (50 each, appended to existing 50)
EXPANSIONS = {
    1: [  # things
        ("النهر شيء.", "النهر", "thing", "certain_knowledge", ["things"]),
        ("الجبل شيء.", "الجبل", "thing", "certain_knowledge", ["things"]),
        ("الكتاب شيء.", "الكتاب", "thing", "certain_knowledge", ["things"]),
        ("القلم شيء.", "القلم", "thing", "certain_knowledge", ["things"]),
        ("المدرسة شيء.", "المدرسة", "thing", "certain_knowledge", ["things"]),
        ("الطائرة شيء.", "الطائرة", "thing", "certain_knowledge", ["things"]),
        ("الحاسوب شيء.", "الحاسوب", "thing", "certain_knowledge", ["things"]),
        ("البيت شيء.", "البيت", "thing", "certain_knowledge", ["things"]),
        ("الشجرة شيء.", "الشجرة", "thing", "certain_knowledge", ["things"]),
        ("السيارة شيء.", "السيارة", "thing", "certain_knowledge", ["things"]),
        ("المستشفى شيء.", "المستشفى", "thing", "certain_knowledge", ["things"]),
        ("القمر شيء.", "القمر", "thing", "certain_knowledge", ["things"]),
        ("الشمس شيء.", "الشمس", "thing", "certain_knowledge", ["things"]),
        ("الطاولة شيء.", "الطاولة", "thing", "certain_knowledge", ["things"]),
        ("الباب شيء.", "الباب", "thing", "certain_knowledge", ["things"]),
        ("النافذة شيء.", "النافذة", "thing", "certain_knowledge", ["things"]),
        ("الحديقة شيء.", "الحديقة", "thing", "certain_knowledge", ["things"]),
        ("الملعب شيء.", "الملعب", "thing", "certain_knowledge", ["things"]),
        ("السوق شيء.", "السوق", "thing", "certain_knowledge", ["things"]),
        ("المسجد شيء.", "المسجد", "thing", "certain_knowledge", ["things"]),
        ("البحر شيء.", "البحر", "thing", "certain_knowledge", ["things"]),
        ("الصحراء شيء.", "الصحراء", "thing", "certain_knowledge", ["things"]),
        ("المطار شيء.", "المطار", "thing", "certain_knowledge", ["things"]),
        ("الميناء شيء.", "الميناء", "thing", "certain_knowledge", ["things"]),
        ("الجسر شيء.", "الجسر", "thing", "certain_knowledge", ["things"]),
        ("الطريق شيء.", "الطريق", "thing", "certain_knowledge", ["things"]),
        ("اللغة شيء.", "اللغة", "thing", "certain_knowledge", ["things"]),
        ("الرياضيات شيء.", "الرياضيات", "thing", "certain_knowledge", ["things"]),
        ("الفيزياء شيء.", "الفيزياء", "thing", "certain_knowledge", ["things"]),
        ("الكيمياء شيء.", "الكيمياء", "thing", "certain_knowledge", ["things"]),
        ("البيولوجيا شيء.", "البيولوجيا", "thing", "certain_knowledge", ["things"]),
        ("الفلسفة شيء.", "الفلسفة", "thing", "certain_knowledge", ["things"]),
        ("التاريخ شيء.", "التاريخ", "thing", "certain_knowledge", ["things"]),
        ("الجغرافيا شيء.", "الجغرافيا", "thing", "certain_knowledge", ["things"]),
        ("الموسيقى شيء.", "الموسيقى", "thing", "certain_knowledge", ["things"]),
        ("الرسم شيء.", "الرسم", "thing", "certain_knowledge", ["things"]),
        ("الشعر شيء.", "الشعر", "thing", "certain_knowledge", ["things"]),
        ("الرواية شيء.", "الرواية", "thing", "certain_knowledge", ["things"]),
        ("الصورة شيء.", "الصورة", "thing", "certain_knowledge", ["things"]),
        ("الفيديو شيء.", "الفيديو", "thing", "certain_knowledge", ["things"]),
        ("الإنترنت شيء.", "الإنترنت", "thing", "certain_knowledge", ["things"]),
        ("الهاتف شيء.", "الهاتف", "thing", "certain_knowledge", ["things"]),
        ("التلفاز شيء.", "التلفاز", "thing", "certain_knowledge", ["things"]),
        ("الراديو شيء.", "الراديو", "thing", "certain_knowledge", ["things"]),
        ("الصحيفة شيء.", "الصحيفة", "thing", "certain_knowledge", ["things"]),
        ("المجلة شيء.", "المجلة", "thing", "certain_knowledge", ["things"]),
        ("القاموس شيء.", "القاموس", "thing", "certain_knowledge", ["things"]),
        ("الموسوعة شيء.", "الموسوعة", "thing", "certain_knowledge", ["things"]),
        ("الخريطة شيء.", "الخريطة", "thing", "certain_knowledge", ["things"]),
        ("المجهر شيء.", "المجهر", "thing", "certain_knowledge", ["things"]),
    ],
    2: [  # properties
        ("الثلج أبيض.", "الثلج", "أبيض", "certain_knowledge", ["properties"]),
        ("العسل حلو.", "العسل", "حلو", "certain_knowledge", ["properties"]),
        ("الخل حامض.", "الخل", "حامض", "certain_knowledge", ["properties"]),
        ("الصخرة صلبة.", "الصخرة", "صلبة", "certain_knowledge", ["properties"]),
        ("الريشة خفيفة.", "الريشة", "خفيفة", "certain_knowledge", ["properties"]),
        ("الحديد ثقيل.", "الحديد", "ثقيل", "certain_knowledge", ["properties"]),
        ("الغيم ناعم.", "الغيم", "ناعم", "probable_knowledge", ["properties"]),
        ("السكر أبيض.", "السكر", "أبيض", "certain_knowledge", ["properties"]),
        ("الفحم أسود.", "الفحم", "أسود", "certain_knowledge", ["properties"]),
        ("الماء شفاف.", "الماء", "شفاف", "certain_knowledge", ["properties"]),
        ("الليل مظلم.", "الليل", "مظلم", "certain_knowledge", ["properties"]),
        ("النهار مضيء.", "النهار", "مضيء", "certain_knowledge", ["properties"]),
        ("الشتاء بارد.", "الشتاء", "بارد", "probable_knowledge", ["properties"]),
        ("الصيف حار.", "الصيف", "حار", "probable_knowledge", ["properties"]),
        ("البرتقال حامض.", "البرتقال", "حامض", "probable_knowledge", ["properties"]),
        ("الشوكولاتة مرة.", "الشوكولاتة", "مرة", "probable_knowledge", ["properties"]),
        ("القطران لزج.", "القطران", "لزج", "certain_knowledge", ["properties"]),
        ("الزجاج هش.", "الزجاج", "هش", "certain_knowledge", ["properties"]),
        ("الذهب لامع.", "الذهب", "لامع", "certain_knowledge", ["properties"]),
        ("الفضة لامعة.", "الفضة", "لامعة", "certain_knowledge", ["properties"]),
        ("النحاس ناقل.", "النحاس", "ناقل", "certain_knowledge", ["properties"]),
        ("الخشب خام.", "الخشب", "خام", "probable_knowledge", ["properties"]),
        ("البلاستيك مرن.", "البلاستيك", "مرن", "certain_knowledge", ["properties"]),
        ("الحرير ناعم.", "الحرير", "ناعم", "certain_knowledge", ["properties"]),
        ("الصوف دافئ.", "الصوف", "دافئ", "certain_knowledge", ["properties"]),
        ("القطن خفيف.", "القطن", "خفيف", "certain_knowledge", ["properties"]),
        ("الورق رقيق.", "الورق", "رقيق", "certain_knowledge", ["properties"]),
        ("الحجر صلب.", "الحجر", "صلب", "certain_knowledge", ["properties"]),
        ("التربة ناعمة.", "التربة", "ناعمة", "certain_knowledge", ["properties"]),
        ("الرمل ناعم.", "الرمل", "ناعم", "certain_knowledge", ["properties"]),
        ("الطين طري.", "الطين", "طري", "certain_knowledge", ["properties"]),
        ("النار مضيئة.", "النار", "مضيئة", "certain_knowledge", ["properties"]),
        ("الجليد صلب.", "الجليد", "صلب", "certain_knowledge", ["properties"]),
        ("البخار خفيف.", "البخار", "خفيف", "certain_knowledge", ["properties"]),
        ("الدم أحمر.", "الدم", "أحمر", "certain_knowledge", ["properties"]),
        ("النباتات خضراء.", "النباتات", "خضراء", "probable_knowledge", ["properties"]),
        ("السماء زرقاء.", "السماء", "زرقاء", "probable_knowledge", ["properties"]),
        ("الأرض واسعة.", "الأرض", "واسعة", "certain_knowledge", ["properties"]),
        ("الكون لا نهائي.", "الكون", "لا نهائي", "probable_knowledge", ["properties"]),
        ("الإنسان عاقل.", "الإنسان", "عاقل", "certain_knowledge", ["properties"]),
        ("الحيوان حساس.", "الحيوان", "حساس", "certain_knowledge", ["properties"]),
        ("النبات نامٍ.", "النبات", "نامٍ", "certain_knowledge", ["properties"]),
        ("الطفل صغير.", "الطفل", "صغير", "certain_knowledge", ["properties"]),
        ("الشيخ كبير.", "الشيخ", "كبير", "certain_knowledge", ["properties"]),
        ("العالم خبير.", "العالم", "خبير", "probable_knowledge", ["properties"]),
        ("الطالب مجتهد.", "الطالب", "مجتهد", "probable_knowledge", ["properties"]),
        ("الكتاب مفيد.", "الكتاب", "مفيد", "probable_knowledge", ["properties"]),
        ("الأداة مفيدة.", "الأداة", "مفيدة", "probable_knowledge", ["properties"]),
        ("القانون ملزم.", "القانون", "ملزم", "certain_knowledge", ["properties"]),
        ("الحقيقة ثابتة.", "الحقيقة", "ثابتة", "probable_knowledge", ["properties"]),
    ],
    3: [  # actions
        ("زيد يكتب.", "زيد", "يكتب", "certain_knowledge", ["actions"]),
        ("سارة تدرس.", "سارة", "تدرس", "certain_knowledge", ["actions"]),
        ("الولد يلعب.", "الولد", "يلعب", "certain_knowledge", ["actions"]),
        ("البنت تقرأ.", "البنت", "تقرأ", "certain_knowledge", ["actions"]),
        ("المعلم يشرح.", "المعلم", "يشرح", "certain_knowledge", ["actions"]),
        ("الطبيب يعالج.", "الطبيب", "يعالج", "certain_knowledge", ["actions"]),
        ("المهندس يصمم.", "المهندس", "يصمم", "certain_knowledge", ["actions"]),
        ("الطاهي يطبخ.", "الطاهي", "يطبخ", "certain_knowledge", ["actions"]),
        ("السائق يقود.", "السائق", "يقود", "certain_knowledge", ["actions"]),
        ("العمال يبنون.", "العمال", "يبنون", "certain_knowledge", ["actions"]),
        ("الفارس يركب.", "الفارس", "يركب", "certain_knowledge", ["actions"]),
        ("الصياد يصيد.", "الصياد", "يصيد", "certain_knowledge", ["actions"]),
        ("الزارع يزرع.", "الزارع", "يزرع", "certain_knowledge", ["actions"]),
        ("التاجر يبيع.", "التاجر", "يبيع", "certain_knowledge", ["actions"]),
        ("المشتري يشتري.", "المشتري", "يشتري", "certain_knowledge", ["actions"]),
        ("الباحث يبحث.", "الباحث", "يبحث", "certain_knowledge", ["actions"]),
        ("الكاتب يؤلف.", "الكاتب", "يؤلف", "certain_knowledge", ["actions"]),
        ("الفنان يرسم.", "الفنان", "يرسم", "certain_knowledge", ["actions"]),
        ("الموسيقي يعزف.", "الموسيقي", "يعزف", "certain_knowledge", ["actions"]),
        ("المغني يغني.", "المغني", "يغني", "certain_knowledge", ["actions"]),
        ("الرياضي يتدرب.", "الرياضي", "يتدرب", "certain_knowledge", ["actions"]),
        ("الجندي يدافع.", "الجندي", "يدافع", "certain_knowledge", ["actions"]),
        ("الشرطي يحرس.", "الشرطي", "يحرس", "certain_knowledge", ["actions"]),
        ("القاضي يحكم.", "القاضي", "يحكم", "certain_knowledge", ["actions"]),
        ("المحامي يدافع.", "المحامي", "يدافع", "certain_knowledge", ["actions"]),
        ("الصحفي يكتب.", "الصحفي", "يكتب", "certain_knowledge", ["actions"]),
        ("المدير يقرر.", "المدير", "يقرر", "certain_knowledge", ["actions"]),
        ("الرئيس يدير.", "الرئيس", "يدير", "certain_knowledge", ["actions"]),
        ("الأم ترعى.", "الأم", "ترعى", "certain_knowledge", ["actions"]),
        ("الأب يعمل.", "الأب", "يعمل", "certain_knowledge", ["actions"]),
        ("الطفل يلعب.", "الطفل", "يلعب", "certain_knowledge", ["actions"]),
        ("العجوز يمشي.", "العجوز", "يمشي", "certain_knowledge", ["actions"]),
        ("الحيوان يأكل.", "الحيوان", "يأكل", "certain_knowledge", ["actions"]),
        ("الطائر يطير.", "الطائر", "يطير", "certain_knowledge", ["actions"]),
        ("السمكة تسبح.", "السمكة", "تسبح", "certain_knowledge", ["actions"]),
        ("النبات ينمو.", "النبات", "ينمو", "certain_knowledge", ["actions"]),
        ("الشجرة تتنفس.", "الشجرة", "تتنفس", "certain_knowledge", ["actions"]),
        ("الأرض تدور.", "الأرض", "تدور", "certain_knowledge", ["actions"]),
        ("القمر يدور.", "القمر", "يدور", "certain_knowledge", ["actions"]),
        ("الشمس تشرق.", "الشمس", "تشرق", "certain_knowledge", ["actions"]),
        ("الغيوم تتحرك.", "الغيوم", "تتحرك", "certain_knowledge", ["actions"]),
        ("المطر يهطل.", "المطر", "يهطل", "certain_knowledge", ["actions"]),
        ("الريح تهب.", "الريح", "تهب", "certain_knowledge", ["actions"]),
        ("البركان يثور.", "البركان", "يثور", "probable_knowledge", ["actions"]),
        ("النهر يجري.", "النهر", "يجري", "certain_knowledge", ["actions"]),
        ("البحر يموج.", "البحر", "يموج", "certain_knowledge", ["actions"]),
        ("الجليد يذوب.", "الجليد", "يذوب", "certain_knowledge", ["actions"]),
        ("الحجر يسقط.", "الحجر", "يسقط", "certain_knowledge", ["actions"]),
        ("الصوت يصدر.", "الصوت", "يصدر", "certain_knowledge", ["actions"]),
        ("النور ينتشر.", "النور", "ينتشر", "certain_knowledge", ["actions"]),
    ],
    4: [  # relations
        ("الطالب يكتب الواجب بالقلم.", "الطالب", "يكتب", "الواجب", "القلم", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المعلم يشرح الدرس للطلاب.", "المعلم", "يشرح", "الدرس", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الطبيب يعالج المريض بالدواء.", "الطبيب", "يعالج", "المريض", "الدواء", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المهندس يبني الجسر.", "المهندس", "يبني", "الجسر", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الفلاح يزرع القمح.", "الفلاح", "يزرع", "القمح", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الأم ترضع الطفل.", "الأم", "ترضع", "الطفل", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الرياح تحرك الأشجار.", "الرياح", "تحرك", "الأشجار", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("النهر يروي الحقول.", "النهر", "يروي", "الحقول", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الشمس تدفئ الأرض.", "الشمس", "تدفئ", "الأرض", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("المطر يروي النباتات.", "المطر", "يروي", "النباتات", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("العلماء يكتشفون الحقائق.", "العلماء", "يكتشفون", "الحقائق", None, "agent_of|patient_of", "probable_knowledge", ["relations"]),
        ("الباحثون يحللون البيانات.", "الباحثون", "يحللون", "البيانات", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("المبرمج يكتب الكود بالحاسوب.", "المبرمج", "يكتب", "الكود", "الحاسوب", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الشاعر ينظم القصيدة بالقلم.", "الشاعر", "ينظم", "القصيدة", "القلم", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الطاهي يطبخ الطعام بالنار.", "الطاهي", "يطبخ", "الطعام", "النار", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الصانع يصنع المنتج بالآلة.", "الصانع", "يصنع", "المنتج", "الآلة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المزارع يحصد القمح بالمنجل.", "المزارع", "يحصد", "القمح", "المنجل", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الحداد يطرق الحديد بالمطرقة.", "الحداد", "يطرق", "الحديد", "المطرقة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("النجار يقطع الخشب بالمنشار.", "النجار", "يقطع", "الخشب", "المنشار", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("البستاني يسقي الزهور بالخرطوم.", "البستاني", "يسقي", "الزهور", "الخرطوم", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الفنان يرسم اللوحة بالفرشاة.", "الفنان", "يرسم", "اللوحة", "الفرشاة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الكاتب يؤلف الرواية بالقلم.", "الكاتب", "يؤلف", "الرواية", "القلم", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المصور يلتقط الصورة بالكاميرا.", "المصور", "يلتقط", "الصورة", "الكاميرا", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الجراح يجري العملية بالمشرط.", "الجراح", "يجري", "العملية", "المشرط", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الموسيقار يعزف الأغنية بالعود.", "الموسيقار", "يعزف", "الأغنية", "العود", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المعماري يصمم المبنى بالحاسوب.", "المعماري", "يصمم", "المبنى", "الحاسوب", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المحلل يحلل البيانات بالبرنامج.", "المحلل", "يحلل", "البيانات", "البرنامج", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الأستاذ يقيّم الامتحان بالقلم الأحمر.", "الأستاذ", "يقيّم", "الامتحان", "القلم الأحمر", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المتحدث يشرح الفكرة بالأمثلة.", "المتحدث", "يشرح", "الفكرة", "الأمثلة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الصياد يصيد السمك بالشبكة.", "الصياد", "يصيد", "السمك", "الشبكة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الطفل يلعب الكرة بيده.", "الطفل", "يلعب", "الكرة", "يده", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المتعلم يفهم الدرس بالممارسة.", "المتعلم", "يفهم", "الدرس", "الممارسة", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("العالم يثبت الفرضية بالتجربة.", "العالم", "يثبت", "الفرضية", "التجربة", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("القاضي يصدر الحكم بالقانون.", "القاضي", "يصدر", "الحكم", "القانون", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المحقق يكشف الجريمة بالأدلة.", "المحقق", "يكشف", "الجريمة", "الأدلة", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("الرياضي يفوز بالبطولة بالتدريب.", "الرياضي", "يفوز", "البطولة", "التدريب", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("الشركة تنتج المنتج بالآلات.", "الشركة", "تنتج", "المنتج", "الآلات", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المعمل يختبر المادة بالأدوات.", "المعمل", "يختبر", "المادة", "الأدوات", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الفريق يحقق الهدف بالتعاون.", "الفريق", "يحقق", "الهدف", "التعاون", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("المصنع ينتج الكهرباء بالطاقة.", "المصنع", "ينتج", "الكهرباء", "الطاقة", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الحكومة تسن القوانين بالبرلمان.", "الحكومة", "تسن", "القوانين", "البرلمان", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المركز يدرب الموظفين بالبرامج.", "المركز", "يدرب", "الموظفين", "البرامج", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المختبر يطور الدواء بالتجارب.", "المختبر", "يطور", "الدواء", "التجارب", "agent_of|patient_of|instrument_of", "probable_knowledge", ["relations"]),
        ("المعهد يمنح الشهادات بالاختبارات.", "المعهد", "يمنح", "الشهادات", "الاختبارات", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("النظام يعالج البيانات بالخوارزميات.", "النظام", "يعالج", "البيانات", "الخوارزميات", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("المنصة تقدم الخدمات للمستخدمين.", "المنصة", "تقدم", "الخدمات", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("التطبيق يعالج الطلبات بالخوادم.", "التطبيق", "يعالج", "الطلبات", "الخوادم", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("الشبكة تنقل البيانات بالألياف.", "الشبكة", "تنقل", "البيانات", "الألياف", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
        ("القمر الصناعي يبث الإشارة.", "القمر الصناعي", "يبث", "الإشارة", None, "agent_of|patient_of", "certain_knowledge", ["relations"]),
        ("الروبوت يجمع القطع بالذراع.", "الروبوت", "يجمع", "القطع", "الذراع", "agent_of|patient_of|instrument_of", "certain_knowledge", ["relations"]),
    ],
    5: [  # causes_effects
        ("الجفاف يسبب المجاعة.", "الجفاف", "المجاعة", "causes", "certain_knowledge", ["causes_effects"]),
        ("التلوث يسبب الأمراض.", "التلوث", "الأمراض", "causes", "probable_knowledge", ["causes_effects"]),
        ("الحرارة الزائدة تسبب الحرائق.", "الحرارة الزائدة", "الحرائق", "causes", "probable_knowledge", ["causes_effects"]),
        ("الرياضة تسبب اللياقة.", "الرياضة", "اللياقة", "causes", "probable_knowledge", ["causes_effects"]),
        ("الإهمال يسبب الأخطاء.", "الإهمال", "الأخطاء", "causes", "probable_knowledge", ["causes_effects"]),
        ("الدراسة تسبب التعلم.", "الدراسة", "التعلم", "causes", "probable_knowledge", ["causes_effects"]),
        ("العمل الجاد يسبب النجاح.", "العمل الجاد", "النجاح", "causes", "probable_knowledge", ["causes_effects"]),
        ("الكسل يسبب الفشل.", "الكسل", "الفشل", "causes", "probable_knowledge", ["causes_effects"]),
        ("الاحتكاك يسبب الحرارة.", "الاحتكاك", "الحرارة", "causes", "certain_knowledge", ["causes_effects"]),
        ("البرودة تسبب التجمد.", "البرودة", "التجمد", "causes", "certain_knowledge", ["causes_effects"]),
        ("الرطوبة تسبب الصدأ.", "الرطوبة", "الصدأ", "causes", "certain_knowledge", ["causes_effects"]),
        ("الحمض يسبب تآكل المعادن.", "الحمض", "تآكل المعادن", "causes", "certain_knowledge", ["causes_effects"]),
        ("الجاذبية تسبب سقوط الأجسام.", "الجاذبية", "سقوط الأجسام", "causes", "certain_knowledge", ["causes_effects"]),
        ("الأمطار الغزيرة تسبب الفيضانات.", "الأمطار الغزيرة", "الفيضانات", "causes", "probable_knowledge", ["causes_effects"]),
        ("الزلزال يسبب دمار المباني.", "الزلزال", "دمار المباني", "causes", "probable_knowledge", ["causes_effects"]),
        ("السرعة الزائدة تسبب الحوادث.", "السرعة الزائدة", "الحوادث", "causes", "probable_knowledge", ["causes_effects"]),
        ("السهر المتأخر يسبب الإرهاق.", "السهر المتأخر", "الإرهاق", "causes", "probable_knowledge", ["causes_effects"]),
        ("الإجهاد يسبب التوتر.", "الإجهاد", "التوتر", "causes", "probable_knowledge", ["causes_effects"]),
        ("التغذية الجيدة تسبب الصحة.", "التغذية الجيدة", "الصحة", "causes", "probable_knowledge", ["causes_effects"]),
        ("النوم الكافي يسبب النشاط.", "النوم الكافي", "النشاط", "causes", "probable_knowledge", ["causes_effects"]),
        ("شرب الماء يسبب الارتواء.", "شرب الماء", "الارتواء", "causes", "certain_knowledge", ["causes_effects"]),
        ("الجوع يسبب الضعف.", "الجوع", "الضعف", "causes", "certain_knowledge", ["causes_effects"]),
        ("التعلم يسبب المعرفة.", "التعلم", "المعرفة", "causes", "probable_knowledge", ["causes_effects"]),
        ("التفكير يسبب الأفكار.", "التفكير", "الأفكار", "causes", "certain_knowledge", ["causes_effects"]),
        ("الإبداع يسبب الابتكار.", "الإبداع", "الابتكار", "causes", "probable_knowledge", ["causes_effects"]),
        ("التواصل يسبب الفهم.", "التواصل", "الفهم", "causes", "probable_knowledge", ["causes_effects"]),
        ("الثقة تسبب التعاون.", "الثقة", "التعاون", "causes", "probable_knowledge", ["causes_effects"]),
        ("الخداع يسبب فقدان الثقة.", "الخداع", "فقدان الثقة", "causes", "probable_knowledge", ["causes_effects"]),
        ("العدالة تسبب الاستقرار.", "العدالة", "الاستقرار", "causes", "probable_knowledge", ["causes_effects"]),
        ("الظلم يسبب الثورة.", "الظلم", "الثورة", "causes", "probable_knowledge", ["causes_effects"]),
        ("التضخم يسبب ارتفاع الأسعار.", "التضخم", "ارتفاع الأسعار", "causes", "certain_knowledge", ["causes_effects"]),
        ("الركود يسبب البطالة.", "الركود", "البطالة", "causes", "probable_knowledge", ["causes_effects"]),
        ("النمو الاقتصادي يسبب رفع المستوى.", "النمو الاقتصادي", "رفع المستوى", "causes", "probable_knowledge", ["causes_effects"]),
        ("التقنية تسبب التغيير الاجتماعي.", "التقنية", "التغيير الاجتماعي", "causes", "probable_knowledge", ["causes_effects"]),
        ("الإنترنت أسبب ثورة المعلومات.", "الإنترنت", "ثورة المعلومات", "causes", "probable_knowledge", ["causes_effects"]),
        ("الذكاء الاصطناعي يسبب تغيير الوظائف.", "الذكاء الاصطناعي", "تغيير الوظائف", "causes", "probable_knowledge", ["causes_effects"]),
        ("التعليم يسبب التنمية.", "التعليم", "التنمية", "causes", "probable_knowledge", ["causes_effects"]),
        ("الصحة تسبب الإنتاجية.", "الصحة", "الإنتاجية", "causes", "probable_knowledge", ["causes_effects"]),
        ("الفقر يسبب الجريمة.", "الفقر", "الجريمة", "causes", "probable_knowledge", ["causes_effects"]),
        ("التعصب يسبب الصراع.", "التعصب", "الصراع", "causes", "probable_knowledge", ["causes_effects"]),
        ("الحوار يسبب التفاهم.", "الحوار", "التفاهم", "causes", "probable_knowledge", ["causes_effects"]),
        ("الانتخابات تسبب التغيير السياسي.", "الانتخابات", "التغيير السياسي", "causes", "probable_knowledge", ["causes_effects"]),
        ("القوانين تسبب النظام.", "القوانين", "النظام", "causes", "probable_knowledge", ["causes_effects"]),
        ("الفساد يسبب انهيار المؤسسات.", "الفساد", "انهيار المؤسسات", "causes", "probable_knowledge", ["causes_effects"]),
        ("الشفافية تسبب الثقة.", "الشفافية", "الثقة", "causes", "probable_knowledge", ["causes_effects"]),
        ("البحث العلمي يسبب التقدم.", "البحث العلمي", "التقدم", "causes", "probable_knowledge", ["causes_effects"]),
        ("الاستثمار يسبب النمو.", "الاستثمار", "النمو", "causes", "probable_knowledge", ["causes_effects"]),
        ("التخطيط يسبب النجاح.", "التخطيط", "النجاح", "causes", "probable_knowledge", ["causes_effects"]),
        ("الإدارة الجيدة تسبب الكفاءة.", "الإدارة الجيدة", "الكفاءة", "causes", "probable_knowledge", ["causes_effects"]),
        ("التنسيق يسبب الانسجام.", "التنسيق", "الانسجام", "causes", "probable_knowledge", ["causes_effects"]),
    ],
    6: [  # instruments_times_places
        ("كتب أحمد الرسالة بالقلم في المكتب صباحًا.", "أحمد", "كتب", "الرسالة", "القلم", "المكتب", "صباحًا", "certain_knowledge", ["instruments_times_places"]),
        ("طبخت سارة الطعام بالموقد في المطبخ مساءً.", "سارة", "طبخت", "الطعام", "الموقد", "المطبخ", "مساءً", "certain_knowledge", ["instruments_times_places"]),
        ("قطع النجار الخشب بالمنشار في الورشة.", "النجار", "قطع", "الخشب", "المنشار", "الورشة", None, "certain_knowledge", ["instruments_times_places"]),
        ("زرع الفلاح القمح بالمحراث في الحقل ربيعًا.", "الفلاح", "زرع", "القمح", "المحراث", "الحقل", "ربيعًا", "certain_knowledge", ["instruments_times_places"]),
        ("صوّر المصور الطبيعة بالكاميرا في الغابة.", "المصور", "صوّر", "الطبيعة", "الكاميرا", "الغابة", None, "certain_knowledge", ["instruments_times_places"]),
        ("رسم الطالب الخريطة بالمسطرة في الصف.", "الطالب", "رسم", "الخريطة", "المسطرة", "الصف", None, "certain_knowledge", ["instruments_times_places"]),
        ("أصلح الميكانيكي السيارة بالمفتاح في الكراج.", "الميكانيكي", "أصلح", "السيارة", "المفتاح", "الكراج", None, "certain_knowledge", ["instruments_times_places"]),
        ("لعب الأطفال كرة القدم في الملعب بعد الظهر.", "الأطفال", "لعبوا", "كرة القدم", None, "الملعب", "بعد الظهر", "certain_knowledge", ["instruments_times_places"]),
        ("درس الطلاب في المكتبة ليلًا.", "الطلاب", "درسوا", None, None, "المكتبة", "ليلًا", "certain_knowledge", ["instruments_times_places"]),
        ("صلى المسلمون في المسجد فجرًا.", "المسلمون", "صلوا", None, None, "المسجد", "فجرًا", "certain_knowledge", ["instruments_times_places"]),
        ("باع التاجر البضاعة في السوق صباحًا.", "التاجر", "باع", "البضاعة", None, "السوق", "صباحًا", "certain_knowledge", ["instruments_times_places"]),
        ("فحص الطبيب المريض بالأجهزة في المستشفى.", "الطبيب", "فحص", "المريض", "الأجهزة", "المستشفى", None, "certain_knowledge", ["instruments_times_places"]),
        ("شرب المسافر الماء في المطار قبل السفر.", "المسافر", "شرب", "الماء", None, "المطار", "قبل السفر", "certain_knowledge", ["instruments_times_places"]),
        ("ألقى المحاضر الخطبة بالميكروفون في القاعة.", "المحاضر", "ألقى", "الخطبة", "الميكروفون", "القاعة", None, "certain_knowledge", ["instruments_times_places"]),
        ("حفر العمال الأساس بالمعدات في الموقع.", "العمال", "حفروا", "الأساس", "المعدات", "الموقع", None, "certain_knowledge", ["instruments_times_places"]),
        ("طار الطيار بالطائرة في الأجواء ليلًا.", "الطيار", "طار", None, "الطائرة", "الأجواء", "ليلًا", "certain_knowledge", ["instruments_times_places"]),
        ("سبح الرياضي في البحر صباحًا.", "الرياضي", "سبح", None, None, "البحر", "صباحًا", "certain_knowledge", ["instruments_times_places"]),
        ("تسلق المغامر الجبل بالحبال في الشتاء.", "المغامر", "تسلق", "الجبل", "الحبال", "الجبل", "الشتاء", "certain_knowledge", ["instruments_times_places"]),
        ("نشر الصحفي المقال بالإنترنت في المكتب.", "الصحفي", "نشر", "المقال", "الإنترنت", "المكتب", None, "certain_knowledge", ["instruments_times_places"]),
        ("أجرى العالم التجربة بالأدوات في المختبر.", "العالم", "أجرى", "التجربة", "الأدوات", "المختبر", None, "certain_knowledge", ["instruments_times_places"]),
        ("بدأ المصنع الإنتاج بالآلات في الصرح.", "المصنع", "بدأ", "الإنتاج", "الآلات", "الصرح", None, "certain_knowledge", ["instruments_times_places"]),
        ("عزف الموسيقار السيمفونية بالبيانو في قاعة الحفلات.", "الموسيقار", "عزف", "السيمفونية", "البيانو", "قاعة الحفلات", None, "certain_knowledge", ["instruments_times_places"]),
        ("لاحظ عالم الفلك النجوم بالتلسكوب في المرصد.", "عالم الفلك", "لاحظ", "النجوم", "التلسكوب", "المرصد", None, "certain_knowledge", ["instruments_times_places"]),
        ("ختم القاضي الحكم بالختم الرسمي في المحكمة.", "القاضي", "ختم", "الحكم", "الختم الرسمي", "المحكمة", None, "certain_knowledge", ["instruments_times_places"]),
        ("كشف المحقق الجريمة بالأدلة في مسرح الجريمة.", "المحقق", "كشف", "الجريمة", "الأدلة", "مسرح الجريمة", None, "probable_knowledge", ["instruments_times_places"]),
        ("قدّم المتقدم طلبه بالإنترنت في المنزل.", "المتقدم", "قدّم", "طلبه", "الإنترنت", "المنزل", None, "certain_knowledge", ["instruments_times_places"]),
        ("فاز اللاعب بالبطولة في الملعب الكبير صيفًا.", "اللاعب", "فاز", "البطولة", None, "الملعب الكبير", "صيفًا", "certain_knowledge", ["instruments_times_places"]),
        ("جمع الباحث البيانات بالاستبيانات في الجامعة.", "الباحث", "جمع", "البيانات", "الاستبيانات", "الجامعة", None, "certain_knowledge", ["instruments_times_places"]),
        ("أشعل البدوي النار بالزناد في الصحراء.", "البدوي", "أشعل", "النار", "الزناد", "الصحراء", None, "certain_knowledge", ["instruments_times_places"]),
        ("قاد الرائد السفينة بالبوصلة في البحر المفتوح.", "الرائد", "قاد", "السفينة", "البوصلة", "البحر المفتوح", None, "certain_knowledge", ["instruments_times_places"]),
        ("استكشف الغواص الأعماق بالأقنعة في البحر.", "الغواص", "استكشف", "الأعماق", "الأقنعة", "البحر", None, "certain_knowledge", ["instruments_times_places"]),
        ("درّب المدرب الفريق بالتمارين في الصالة.", "المدرب", "درّب", "الفريق", "التمارين", "الصالة", None, "certain_knowledge", ["instruments_times_places"]),
        ("صلّح الكهربائي العطل بالأدوات في المنزل.", "الكهربائي", "صلّح", "العطل", "الأدوات", "المنزل", None, "certain_knowledge", ["instruments_times_places"]),
        ("قدّمت المضيفة الطعام بالصينية في الطائرة.", "المضيفة", "قدّمت", "الطعام", "الصينية", "الطائرة", None, "certain_knowledge", ["instruments_times_places"]),
        ("بنى المعماري الجسر بالإسمنت المسلح على النهر.", "المعماري", "بنى", "الجسر", "الإسمنت المسلح", "النهر", None, "certain_knowledge", ["instruments_times_places"]),
        ("أدار المدير الاجتماع بالمنظومة الإلكترونية في القاعة.", "المدير", "أدار", "الاجتماع", "المنظومة الإلكترونية", "القاعة", None, "certain_knowledge", ["instruments_times_places"]),
        ("نقل العمال البضاعة بالرافعة في المستودع.", "العمال", "نقلوا", "البضاعة", "الرافعة", "المستودع", None, "certain_knowledge", ["instruments_times_places"]),
        ("أجرى الممثل التمرين على المسرح مساءً.", "الممثل", "أجرى", "التمرين", None, "المسرح", "مساءً", "certain_knowledge", ["instruments_times_places"]),
        ("رتّب المكتبي الكتب بالتصنيف في المكتبة.", "المكتبي", "رتّب", "الكتب", "التصنيف", "المكتبة", None, "certain_knowledge", ["instruments_times_places"]),
        ("قيّد المحاسب الأرقام بالبرنامج في المكتب.", "المحاسب", "قيّد", "الأرقام", "البرنامج", "المكتب", None, "certain_knowledge", ["instruments_times_places"]),
        ("لاحق الشرطي المشتبه به في الشارع.", "الشرطي", "لاحق", "المشتبه به", None, "الشارع", None, "certain_knowledge", ["instruments_times_places"]),
        ("صوّت الناخب في صندوق الانتخابات في مركز الاقتراع.", "الناخب", "صوّت", None, "صندوق الانتخابات", "مركز الاقتراع", None, "certain_knowledge", ["instruments_times_places"]),
        ("وقّع المسؤول الاتفاقية بالقلم الرسمي في القصر.", "المسؤول", "وقّع", "الاتفاقية", "القلم الرسمي", "القصر", None, "certain_knowledge", ["instruments_times_places"]),
        ("حضر الوفد المؤتمر في جنيف أمس.", "الوفد", "حضر", "المؤتمر", None, "جنيف", "أمس", "certain_knowledge", ["instruments_times_places"]),
        ("ألّف المؤلف الكتاب في منزله خلال أشهر.", "المؤلف", "ألّف", "الكتاب", None, "منزله", "خلال أشهر", "certain_knowledge", ["instruments_times_places"]),
        ("فتش الجمركي الحقيبة بالأجهزة في المطار.", "الجمركي", "فتش", "الحقيبة", "الأجهزة", "المطار", None, "certain_knowledge", ["instruments_times_places"]),
        ("تحدث المتحدث بالترجمة في المؤتمر الدولي.", "المتحدث", "تحدث", None, "الترجمة", "المؤتمر الدولي", None, "certain_knowledge", ["instruments_times_places"]),
        ("صمم المهندس المنتج بالبرنامج في المختبر.", "المهندس", "صمم", "المنتج", "البرنامج", "المختبر", None, "certain_knowledge", ["instruments_times_places"]),
        ("احتفل الفريق بالفوز في الملعب ليلًا.", "الفريق", "احتفل", "الفوز", None, "الملعب", "ليلًا", "certain_knowledge", ["instruments_times_places"]),
        ("أعلن المتحدث الرسمي القرار في المؤتمر الصحفي.", "المتحدث الرسمي", "أعلن", "القرار", None, "المؤتمر الصحفي", None, "certain_knowledge", ["instruments_times_places"]),
    ],
    7: [  # evidence_certainty
        ("النموذج يدعي أن الجميع يستخدم GraphRAG.", None, "unsupported_generalization|source_required", "suspend_judgment", ["evidence_certainty", "adversarial"]),
        ("المصدر قديم لكنه الأحدث المتاح.", None, "stale_source|source_required", "probable_knowledge", ["evidence_certainty"]),
        ("الدليل يأتي من مصدر تجاري.", None, "source_trust_required|potential_bias", "probable_knowledge", ["evidence_certainty"]),
        ("الوثيقة الرسمية حديثة وموثوقة.", None, "textual_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("التجربة أُجريت مرة واحدة فقط.", None, "insufficient_replication", "hypothesis", ["evidence_certainty"]),
        ("نتائج التجربة قابلة للتكرار.", None, "experimental_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("الخبير يؤكد دون إبداء دليل.", None, "unsupported_claim|source_required", "probable_knowledge", ["evidence_certainty"]),
        ("الشهادات المتعددة تتفق على الواقعة.", None, "multiple_witnesses|convergent_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("المصدران يتعارضان في التفاصيل الجوهرية.", None, "conflicting_sources|suspend_required", "suspend_judgment", ["evidence_certainty"]),
        ("الإحصائية مأخوذة من عينة صغيرة.", None, "insufficient_sample|statistical_weakness", "hypothesis", ["evidence_certainty"]),
        ("التقرير يعترف بمحدودية البيانات.", None, "honest_uncertainty|calibration_present", "probable_knowledge", ["evidence_certainty"]),
        ("النتيجة نُشرت في مجلة محكّمة.", None, "peer_reviewed|textual_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("التقييم مبني على رأي واحد فقط.", None, "single_opinion|insufficient_breadth", "hypothesis", ["evidence_certainty"]),
        ("السؤال ملتبس ويحتمل معنيين.", None, "ambiguity|suspend_required", "suspend_judgment", ["evidence_certainty"]),
        ("المصدر لم يُذكر اسمه في التقرير.", None, "anonymous_source|source_required", "suspend_judgment", ["evidence_certainty"]),
        ("الدليل يدعم الفرضية لكن لا يثبتها.", None, "partial_evidence|hypothesis", "probable_knowledge", ["evidence_certainty"]),
        ("المعلومة منتشرة على نطاق واسع.", None, "popularity_not_evidence|source_required", "probable_knowledge", ["evidence_certainty"]),
        ("التجربة العلمية أثبتت الظاهرة مرات عديدة.", None, "experimental_evidence|replicated", "strong_knowledge", ["evidence_certainty"]),
        ("التفسير يتجاوز ما تقوله البيانات.", None, "over_interpretation|unsupported_generalization", "hypothesis", ["evidence_certainty"]),
        ("كلا المصدرين موثوقان لكن يتعارضان.", None, "conflicting_reliable_sources|suspend_required", "suspend_judgment", ["evidence_certainty"]),
        ("الفرضية مبنية على تشابه سطحي.", None, "false_analogy|insufficient_grounds", "hypothesis", ["evidence_certainty"]),
        ("الادعاء مدعوم بدليل تاريخي موثق.", None, "historical_evidence|textual", "strong_knowledge", ["evidence_certainty"]),
        ("المصدر لديه مصلحة مباشرة في النتيجة.", None, "conflict_of_interest|source_bias", "probable_knowledge", ["evidence_certainty"]),
        ("الملاحظة تكررت في ظروف متعددة.", None, "experimental_evidence|replication", "strong_knowledge", ["evidence_certainty"]),
        ("التقرير يخلط الحقائق بالآراء.", None, "fact_opinion_conflation|calibration_needed", "probable_knowledge", ["evidence_certainty"]),
        ("الدليل يعتمد على شهادة مشبوهة.", None, "suspicious_witness|source_trust_required", "hypothesis", ["evidence_certainty"]),
        ("الدراسة شملت عينة متنوعة وممثلة.", None, "representative_sample|strong_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("البيانات من مصادر مفتوحة قابلة للتحقق.", None, "open_data|verifiable", "strong_knowledge", ["evidence_certainty"]),
        ("المصدر المستشهد به حُذف لاحقًا.", None, "deleted_source|stale_reference", "suspend_judgment", ["evidence_certainty"]),
        ("الادعاء يعتمد على توقعات نموذج AI.", None, "ai_prediction|tool_not_evidence", "hypothesis", ["evidence_certainty"]),
        ("السند الشرعي ثابت بالتواتر.", None, "shari_evidence|textual_mutawatir", "certain_knowledge", ["evidence_certainty", "shari"]),
        ("الرواية منقطعة السند.", None, "broken_chain|insufficient_shari_evidence", "hypothesis", ["evidence_certainty", "shari"]),
        ("الإجماع الفقهي ثابت على المسألة.", None, "scholarly_consensus|strong_evidence", "strong_knowledge", ["evidence_certainty", "shari"]),
        ("القياس الأصولي يفتقر إلى بيان العلة.", None, "missing_illah|analogy_invalid", "suspend_judgment", ["evidence_certainty"]),
        ("الدليل العلمي والنقلي متوافقان.", None, "convergent_evidence|high_certainty", "strong_knowledge", ["evidence_certainty"]),
        ("اكتُشف خطأ في قاعدة البيانات.", None, "contaminated_data|unreliable", "suspend_judgment", ["evidence_certainty"]),
        ("الاختبار يقيس شيئًا مختلفًا عن المطلوب.", None, "construct_invalidity|measurement_error", "hypothesis", ["evidence_certainty"]),
        ("المنهجية موثقة وقابلة للتدقيق.", None, "methodological_transparency|reliable", "strong_knowledge", ["evidence_certainty"]),
        ("التقييم يعتمد على مقياس ذاتي.", None, "subjective_measure|single_assessor", "probable_knowledge", ["evidence_certainty"]),
        ("الوثيقة موثقة من جهة مستقلة.", None, "independent_verification|textual_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("المعلومة من مصدر غير متخصص.", None, "non_expert_source|source_trust_required", "probable_knowledge", ["evidence_certainty"]),
        ("الرقم المستشهد به مأخوذ خارج سياقه.", None, "decontextualization|misleading", "suspend_judgment", ["evidence_certainty"]),
        ("الشاهد حضر الحدث مباشرةً.", None, "direct_witness|sensory_evidence", "strong_knowledge", ["evidence_certainty"]),
        ("لم تجرِ أي تجربة للتحقق من الادعاء.", None, "unverified_claim|experimental_required", "hypothesis", ["evidence_certainty"]),
        ("المعلومة نُقلت بالسلسلة دون توثيق أصلي.", None, "chain_narration|no_primary_source", "suspend_judgment", ["evidence_certainty"]),
        ("المصدر الوحيد هو نموذج اللغة نفسه.", None, "self_reference|circular_evidence|tool_not_evidence", "suspend_judgment", ["evidence_certainty", "adversarial"]),
        ("التقرير صادر من مؤسسة بحثية مستقلة.", None, "institutional_evidence|credible_source", "strong_knowledge", ["evidence_certainty"]),
        ("لا يوجد إجماع علمي على هذه المسألة.", None, "no_consensus|suspend_recommended", "probable_knowledge", ["evidence_certainty"]),
        ("المصدر يفتقر إلى التاريخ والإصدار.", None, "undated_source|stale_possible", "probable_knowledge", ["evidence_certainty"]),
        ("تكررت النتيجة في ثلاث دراسات مستقلة.", None, "replicated_studies|strong_evidence", "strong_knowledge", ["evidence_certainty"]),
    ],
    8: [  # mixed_reasoning
        ("النموذج قال: الذكاء الاصطناعي يحل كل المشكلات. هل هذا صحيح؟", "unsupported_generalization|over_certainty", "suspend_judgment", ["mixed_reasoning", "adversarial"]),
        ("بما أن الدواء A نجح في حالة واحدة، فهو ناجح دائمًا.", "hasty_generalization|insufficient_sample", "suspend_judgment", ["mixed_reasoning"]),
        ("الكذب ضار. الكذب حرام. ما العلاقة؟", "harm_haram_distinction|domain_mixing", "suspend_judgment", ["mixed_reasoning", "harm_haram"]),
        ("الشركة أعلنت أن منتجها آمن. هل نثق بها؟", "source_trust_required|conflict_of_interest", "probable_knowledge", ["mixed_reasoning"]),
        ("هذه الإحصائية من 2015 تُعبّر عن الوضع الحالي.", "stale_source|temporal_invalidity", "suspend_judgment", ["mixed_reasoning"]),
        ("قال مليون شخص إن هذه الفكرة صحيحة.", "popularity_as_evidence|appeal_to_majority", "probable_knowledge", ["mixed_reasoning"]),
        ("المجتمع مريض - ما التشخيص الحرفي؟", "metaphor_as_literal|domain_error", "suspend_judgment", ["mixed_reasoning"]),
        ("الذكاء الاصطناعي قال ذلك - إذن هو حقيقة.", "tool_as_authority|tool_not_evidence", "suspend_judgment", ["mixed_reasoning", "adversarial"]),
        ("الإجابة إما صح أو خطأ لا وسط بينهما.", "false_dichotomy|binary_fallacy", "suspend_judgment", ["mixed_reasoning"]),
        ("هذا مشابه لذاك إذن يأخذ نفس الحكم.", "false_analogy|missing_illah", "suspend_judgment", ["mixed_reasoning"]),
        ("الفتوى صادرة عن عالم معروف.", "scholarly_authority|shari_evidence", "probable_knowledge", ["mixed_reasoning", "shari"]),
        ("القانون ينص صراحةً على ذلك.", "legal_text|formal_source", "strong_knowledge", ["mixed_reasoning"]),
        ("البيانات الحكومية الرسمية تؤكد الرقم.", "official_data|government_source", "strong_knowledge", ["mixed_reasoning"]),
        ("التجربة نُفّذت دون ضابط تجريبي.", "methodological_flaw|control_group_missing", "hypothesis", ["mixed_reasoning"]),
        ("السؤال يتضمن افتراضًا مسبقًا كاذبًا.", "loaded_question|false_premise", "suspend_judgment", ["mixed_reasoning"]),
        ("المصدران متناقضان - أيهما يُقدَّم؟", "source_conflict|requires_tarjih", "suspend_judgment", ["mixed_reasoning"]),
        ("الادعاء غير قابل للدحض.", "unfalsifiable_claim|pseudoscience", "suspend_judgment", ["mixed_reasoning"]),
        ("الأدلة التجريبية والنصية متوافقة.", "convergent_evidence|high_reliability", "strong_knowledge", ["mixed_reasoning"]),
        ("الكلمة تحتمل معنيين متعارضين.", "lexical_ambiguity|need_context", "suspend_judgment", ["mixed_reasoning"]),
        ("البيانات دقيقة لكن التفسير مبالغ فيه.", "data_over_interpretation|inference_gap", "probable_knowledge", ["mixed_reasoning"]),
        ("الوثيقة مختومة لكن محتواها مشكوك فيه.", "formal_vs_content_validity|critical_reading", "probable_knowledge", ["mixed_reasoning"]),
        ("الخبراء اتفقوا على الاستنتاج.", "expert_consensus|strong_evidence", "strong_knowledge", ["mixed_reasoning"]),
        ("التحذير يأتي من شخص له مصلحة في الإنذار.", "conflict_of_interest|motivated_reasoning", "suspend_judgment", ["mixed_reasoning"]),
        ("الحجة تعتمد على الحجة نفسها كدليل.", "circular_reasoning|self_referential", "suspend_judgment", ["mixed_reasoning"]),
        ("الظاهرة لها تفسيرات بديلة متعددة.", "multiple_explanations|underdetermination", "probable_knowledge", ["mixed_reasoning"]),
        ("التشخيص اليقيني تعذّر بغياب الفحص.", "diagnosis_requires_examination|suspend", "suspend_judgment", ["mixed_reasoning"]),
        ("العلم يوافق المبدأ الشرعي في هذه المسألة.", "science_religion_convergence|high_certainty", "strong_knowledge", ["mixed_reasoning"]),
        ("النتيجة معروفة قبل التجربة - هناك تحيز.", "confirmation_bias|methodological_flaw", "suspend_judgment", ["mixed_reasoning"]),
        ("الفرضية نُشرت لكن لم تُفنَّد بعد.", "awaiting_falsification|provisional", "probable_knowledge", ["mixed_reasoning"]),
        ("المصدر يؤكد لكن القاعدة الرياضية تنفي.", "math_overrides_authority|formal_contradiction", "suspend_judgment", ["mixed_reasoning"]),
        ("الاستدلال صحيح لكن المقدمة خاطئة.", "valid_argument_false_premise|invalid_conclusion", "suspend_judgment", ["mixed_reasoning"]),
        ("قيل هذا منذ ألف سنة - إذن هو حق.", "appeal_to_antiquity|genetic_fallacy", "probable_knowledge", ["mixed_reasoning"]),
        ("كل دول المنطقة تطبقه - إذن هو صحيح.", "appeal_to_practice|descriptive_not_normative", "probable_knowledge", ["mixed_reasoning"]),
        ("الدليل المادي يناقض الشهادة الشفهية.", "evidence_conflict|requires_weighing", "suspend_judgment", ["mixed_reasoning"]),
        ("الادعاء استثنائي ويحتاج دليلًا استثنائيًا.", "extraordinary_claim|high_evidence_bar", "suspend_judgment", ["mixed_reasoning"]),
        ("السلطة الرسمية نفت المعلومة دون سبب.", "official_denial_without_reason|uncertain", "suspend_judgment", ["mixed_reasoning"]),
        ("التقرير يستند إلى بيانات مجهولة المصدر.", "anonymous_data|low_trust", "probable_knowledge", ["mixed_reasoning"]),
        ("المعلومة لا تزال قيد التحقق العلمي.", "pending_verification|provisional", "probable_knowledge", ["mixed_reasoning"]),
        ("الفقه يختلف في المسألة بين المذاهب.", "scholarly_disagreement|shari|requires_ijtihad", "suspend_judgment", ["mixed_reasoning", "shari"]),
        ("الحكم القانوني يختلف من دولة لأخرى.", "jurisdictional_variation|context_dependent", "probable_knowledge", ["mixed_reasoning"]),
        ("الأمر يعتمد على نية الفاعل.", "intention_dependent|requires_context", "probable_knowledge", ["mixed_reasoning"]),
        ("البيانات تشير إلى ارتباط لكن ليس سببية.", "correlation_causation|causality_not_established", "probable_knowledge", ["mixed_reasoning"]),
        ("الدراسة ممولة من الشركة المستفيدة.", "funded_research|conflict_of_interest", "probable_knowledge", ["mixed_reasoning"]),
        ("التقنية حديثة ولا تزال تُختبر.", "emerging_technology|provisional_knowledge", "probable_knowledge", ["mixed_reasoning"]),
        ("الادعاء يعتمد على قراءة جزئية للنص.", "cherry_picking|selective_reading", "suspend_judgment", ["mixed_reasoning"]),
        ("الإحصائية الوصفية تُعرض كنتيجة حتمية.", "descriptive_to_prescriptive_fallacy|misleading", "suspend_judgment", ["mixed_reasoning"]),
        ("اللوائح الرسمية تُقر الممارسة.", "regulatory_approval|formal_evidence", "strong_knowledge", ["mixed_reasoning"]),
        ("البحث يفتقر إلى مراجعة بيانية.", "no_peer_review|low_reliability", "hypothesis", ["mixed_reasoning"]),
        ("الحكمة الشعبية توافق الدليل التجريبي.", "folk_wisdom_validated|convergent", "probable_knowledge", ["mixed_reasoning"]),
        ("الأمثلة المختارة لا تمثل الحالة العامة.", "unrepresentative_examples|selection_bias", "suspend_judgment", ["mixed_reasoning"]),
    ],
}


def build_unit_l1_l3(idx, text, main_thing, action_or_prop, layer, certainty, tags, level):
    frame = {
        "things": [], "properties": [], "actions": [], "agents": [], "patients": [],
        "instruments": [], "times": [], "places": [], "causes": [], "effects": [],
        "relations": [], "evidence_need": [], "certainty_policy": certainty, "warnings": []
    }
    if layer == "thing":
        frame["things"] = [main_thing]
    elif layer == "property":
        frame["things"] = [main_thing]
        frame["properties"] = [action_or_prop]
    elif layer == "action":
        frame["agents"] = [main_thing]
        frame["actions"] = [action_or_prop]
    return {
        "unit_id": f"L0{level}-EX-{idx:04d}",
        "input_text": text,
        "level": level,
        "target_layer": layer,
        "expected_frame": frame,
        "expected_warnings": [],
        "forbidden_confusions": [],
        "evidence_need": [],
        "certainty_policy": certainty,
        "difficulty": "medium",
        "tags": tags,
        "metadata": {}
    }


def build_unit_l4(idx, text, agent, action, patient, instrument, relations_str, certainty, tags):
    rel_triples = []
    if agent and action:
        rel_triples.append({"source": agent, "relation": "agent_of", "target": action, "qualifier": None})
    if patient and action:
        rel_triples.append({"source": patient, "relation": "patient_of", "target": action, "qualifier": None})
    if instrument and action:
        rel_triples.append({"source": instrument, "relation": "instrument_of", "target": action, "qualifier": None})
    frame = {
        "things": [x for x in [agent, patient, instrument] if x],
        "properties": [], "actions": [action] if action else [],
        "agents": [agent] if agent else [], "patients": [patient] if patient else [],
        "instruments": [instrument] if instrument else [],
        "times": [], "places": [], "causes": [], "effects": [],
        "relations": rel_triples,
        "evidence_need": [], "certainty_policy": certainty, "warnings": []
    }
    return {
        "unit_id": f"L04-EX-{idx:04d}",
        "input_text": text,
        "level": 4,
        "target_layer": "relation",
        "expected_frame": frame,
        "expected_warnings": [],
        "forbidden_confusions": [],
        "evidence_need": [],
        "certainty_policy": certainty,
        "difficulty": "medium",
        "tags": tags,
        "metadata": {}
    }


def build_unit_l5(idx, text, cause, effect, rel, certainty, tags):
    frame = {
        "things": [cause, effect],
        "properties": [], "actions": [], "agents": [], "patients": [],
        "instruments": [], "times": [], "places": [],
        "causes": [cause], "effects": [effect],
        "relations": [{"source": cause, "relation": rel, "target": effect, "qualifier": None}],
        "evidence_need": [], "certainty_policy": certainty, "warnings": []
    }
    return {
        "unit_id": f"L05-EX-{idx:04d}",
        "input_text": text,
        "level": 5,
        "target_layer": "cause",
        "expected_frame": frame,
        "expected_warnings": [],
        "forbidden_confusions": [],
        "evidence_need": [],
        "certainty_policy": certainty,
        "difficulty": "medium",
        "tags": tags,
        "metadata": {}
    }


def build_unit_l6(idx, text, agent, action, patient, instrument, place, time, certainty, tags):
    frame = {
        "things": [x for x in [agent, patient, instrument] if x],
        "properties": [], "actions": [action] if action else [],
        "agents": [agent] if agent else [], "patients": [patient] if patient else [],
        "instruments": [instrument] if instrument else [],
        "times": [time] if time else [], "places": [place] if place else [],
        "causes": [], "effects": [],
        "relations": [],
        "evidence_need": [], "certainty_policy": certainty, "warnings": []
    }
    return {
        "unit_id": f"L06-EX-{idx:04d}",
        "input_text": text,
        "level": 6,
        "target_layer": "instrument",
        "expected_frame": frame,
        "expected_warnings": [],
        "forbidden_confusions": [],
        "evidence_need": [],
        "certainty_policy": certainty,
        "difficulty": "medium",
        "tags": tags,
        "metadata": {}
    }


def build_unit_l7(idx, text, warnings_str, certainty, tags):
    warnings_list = warnings_str.split("|") if warnings_str else []
    ev_need = ["textual_evidence"] if "textual" in warnings_str else (["experimental_evidence"] if "experimental" in warnings_str else ["source_verification"])
    frame = {
        "things": [], "properties": [], "actions": [], "agents": [], "patients": [],
        "instruments": [], "times": [], "places": [], "causes": [], "effects": [],
        "relations": [],
        "evidence_need": ev_need,
        "certainty_policy": certainty,
        "warnings": warnings_list
    }
    return {
        "unit_id": f"L07-EX-{idx:04d}",
        "input_text": text,
        "level": 7,
        "target_layer": "evidence",
        "expected_frame": frame,
        "expected_warnings": warnings_list,
        "forbidden_confusions": ["certainty_without_evidence"],
        "evidence_need": ev_need,
        "certainty_policy": certainty,
        "difficulty": "hard",
        "tags": tags,
        "metadata": {}
    }


def build_unit_l8(idx, text, warnings_str, certainty, tags):
    warnings_list = warnings_str.split("|") if warnings_str else []
    ev_need = ["source_verification", "critical_thinking"]
    frame = {
        "things": [], "properties": [], "actions": [], "agents": [], "patients": [],
        "instruments": [], "times": [], "places": [], "causes": [], "effects": [],
        "relations": [],
        "evidence_need": ev_need,
        "certainty_policy": certainty,
        "warnings": warnings_list
    }
    return {
        "unit_id": f"L08-EX-{idx:04d}",
        "input_text": text,
        "level": 8,
        "target_layer": "mixed_reasoning",
        "expected_frame": frame,
        "expected_warnings": warnings_list,
        "forbidden_confusions": ["certainty_without_evidence", "tool_as_evidence"],
        "evidence_need": ev_need,
        "certainty_policy": certainty,
        "difficulty": "adversarial",
        "tags": tags,
        "metadata": {}
    }


units_by_level: dict = {}

for item in EXPANSIONS[1]:
    text, thing, layer, certainty, tags = item
    idx = len(units_by_level.get(1, [])) + 51
    units_by_level.setdefault(1, []).append(build_unit_l1_l3(idx, text, thing, None, layer, certainty, tags, 1))

for item in EXPANSIONS[2]:
    text, thing, prop, certainty, tags = item
    idx = len(units_by_level.get(2, [])) + 51
    units_by_level.setdefault(2, []).append(build_unit_l1_l3(idx, text, thing, prop, "property", certainty, tags, 2))

for item in EXPANSIONS[3]:
    text, agent, action, certainty, tags = item
    idx = len(units_by_level.get(3, [])) + 51
    units_by_level.setdefault(3, []).append(build_unit_l1_l3(idx, text, agent, action, "action", certainty, tags, 3))

for item in EXPANSIONS[4]:
    text, agent, action, patient, instrument, rels, certainty, tags = item
    idx = len(units_by_level.get(4, [])) + 51
    units_by_level.setdefault(4, []).append(build_unit_l4(idx, text, agent, action, patient, instrument, rels, certainty, tags))

for item in EXPANSIONS[5]:
    text, cause, effect, rel, certainty, tags = item
    idx = len(units_by_level.get(5, [])) + 51
    units_by_level.setdefault(5, []).append(build_unit_l5(idx, text, cause, effect, rel, certainty, tags))

for item in EXPANSIONS[6]:
    text, agent, action, patient, instrument, place, time, certainty, tags = item
    idx = len(units_by_level.get(6, [])) + 51
    units_by_level.setdefault(6, []).append(build_unit_l6(idx, text, agent, action, patient, instrument, place, time, certainty, tags))

for item in EXPANSIONS[7]:
    text, _, warnings_str, certainty, tags = item
    idx = len(units_by_level.get(7, [])) + 51
    units_by_level.setdefault(7, []).append(build_unit_l7(idx, text, warnings_str, certainty, tags))

for item in EXPANSIONS[8]:
    text, warnings_str, certainty, tags = item
    idx = len(units_by_level.get(8, [])) + 51
    units_by_level.setdefault(8, []).append(build_unit_l8(idx, text, warnings_str, certainty, tags))

LEVEL_FILES = {
    1: "level_01_things_ar.jsonl",
    2: "level_02_properties_ar.jsonl",
    3: "level_03_actions_ar.jsonl",
    4: "level_04_relations_ar.jsonl",
    5: "level_05_causes_effects_ar.jsonl",
    6: "level_06_instruments_times_places_ar.jsonl",
    7: "level_07_evidence_certainty_ar.jsonl",
    8: "level_08_mixed_reasoning_ar.jsonl",
}

for level, units in units_by_level.items():
    fname = LEVEL_FILES[level]
    path = DATA_DIR / fname
    with open(path, "a", encoding="utf-8") as f:
        for u in units:
            f.write(json.dumps(u, ensure_ascii=False) + "\n")
    total = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    print(f"Level {level}: {fname} now has {total} examples")

print("Done expanding levels 1-8!")
