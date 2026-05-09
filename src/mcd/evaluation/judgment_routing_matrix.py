"""Judgment Routing Matrix — فهرس سياسة التوجيه المعرفي.

Defines a structured policy table with 10 dimensions for each judgment task type:

  1.  نوع المهمة            — task_type
  2.  الواقع المقصود         — intended_reality
  3.  الدليل المطلوب         — required_evidence
  4.  درجة اليقين            — certainty_degree
  5.  متى تجيب               — when_to_answer
  6.  متى تعلق               — when_to_suspend
  7.  متى تطلب مصدرًا        — when_to_request_source
  8.  متى تميز بين رأي ودليل — when_to_distinguish_opinion_evidence
  9.  متى تكشف الهلوسة        — when_to_detect_hallucination
  10. متى تفرق بين حكم تقني وحكم قيمي أو شرعي — when_to_separate_technical_from_value_shari
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from mcd.classification.taxonomy import CertaintyPolicy, JudgmentType

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "evaluation"
_MATRIX_FILE = _DATA_DIR / "judgment_routing_matrix.json"


# ---------------------------------------------------------------------------
# Policy entry dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MatrixEntry:
    """A single row in the Judgment Routing Matrix.

    Each entry captures the full 10-dimension policy for one task type.
    """

    # 1. نوع المهمة
    task_type: str
    # 2. الواقع المقصود
    intended_reality: str
    # 3. الدليل المطلوب
    required_evidence: tuple[str, ...]
    # 4. درجة اليقين
    certainty_degree: str
    # 5. متى تجيب
    when_to_answer: str
    # 6. متى تعلق
    when_to_suspend: str
    # 7. متى تطلب مصدرًا
    when_to_request_source: str
    # 8. متى تميز بين رأي ودليل
    when_to_distinguish_opinion_evidence: str
    # 9. متى تكشف الهلوسة
    when_to_detect_hallucination: str
    # 10. متى تفرق بين حكم تقني وحكم قيمي أو شرعي
    when_to_separate_technical_from_value_shari: str

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "intended_reality": self.intended_reality,
            "required_evidence": list(self.required_evidence),
            "certainty_degree": self.certainty_degree,
            "when_to_answer": self.when_to_answer,
            "when_to_suspend": self.when_to_suspend,
            "when_to_request_source": self.when_to_request_source,
            "when_to_distinguish_opinion_evidence": self.when_to_distinguish_opinion_evidence,
            "when_to_detect_hallucination": self.when_to_detect_hallucination,
            "when_to_separate_technical_from_value_shari": self.when_to_separate_technical_from_value_shari,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MatrixEntry":
        return cls(
            task_type=d["task_type"],
            intended_reality=d["intended_reality"],
            required_evidence=tuple(d.get("required_evidence", [])),
            certainty_degree=d["certainty_degree"],
            when_to_answer=d["when_to_answer"],
            when_to_suspend=d["when_to_suspend"],
            when_to_request_source=d["when_to_request_source"],
            when_to_distinguish_opinion_evidence=d["when_to_distinguish_opinion_evidence"],
            when_to_detect_hallucination=d["when_to_detect_hallucination"],
            when_to_separate_technical_from_value_shari=d[
                "when_to_separate_technical_from_value_shari"
            ],
        )


# ---------------------------------------------------------------------------
# Default hard-coded matrix (covers all 10 JudgmentType values + adversarial)
#
# Each entry is a plain dict with exactly these 10 keys:
#   task_type, intended_reality, required_evidence, certainty_degree,
#   when_to_answer, when_to_suspend, when_to_request_source,
#   when_to_distinguish_opinion_evidence, when_to_detect_hallucination,
#   when_to_separate_technical_from_value_shari
#
# task_type MUST equal the .value of the corresponding JudgmentType member
# (e.g. "epistemic", "shari", "usuli_reasoning").
# required_evidence entries must be valid EvidenceNeed values.
# certainty_degree must be a valid CertaintyPolicy value.
# ---------------------------------------------------------------------------

_DEFAULT_ENTRIES: list[dict] = [
    {
        "task_type": JudgmentType.EPISTEMIC.value,
        "intended_reality": "واقع موضوعي: حدث، علاقة سببية، أو خاصية مدركة بالحس أو العقل.",
        "required_evidence": ["sensory", "experimental", "textual"],
        "certainty_degree": CertaintyPolicy.STRONG_KNOWLEDGE.value,
        "when_to_answer": "إذا وجد دليل تجريبي أو حسي أو منطقي قابل للتحقق.",
        "when_to_suspend": "إذا تعارضت الشواهد أو كان الواقع غير قابل للتحقق الحالي.",
        "when_to_request_source": "عند ادعاء معرفة يقينية بلا دليل ملموس؛ اطلب المصدر التجريبي أو المنطقي.",
        "when_to_distinguish_opinion_evidence": "عندما يُقدَّم تفسير ذاتي على أنه حقيقة موضوعية؛ ميّز بين رأي الشخص والواقع المُثبت.",
        "when_to_detect_hallucination": "عندما يُثبَت واقع تفصيلي مجزوم بلا مصدر، أو يُصاغ اليقين في مسائل لا يقين فيها.",
        "when_to_separate_technical_from_value_shari": "الأصل هنا معرفي؛ لا ترفع الحكم لمستوى شرعي أو قيمي ما لم يُطلب صراحةً.",
    },
    {
        "task_type": JudgmentType.TECHNICAL.value,
        "intended_reality": "واقع تقني: نظام، واجهة برمجية، خوارزمية، أو عملية برمجية.",
        "required_evidence": ["technical", "textual"],
        "certainty_degree": CertaintyPolicy.STRONG_KNOWLEDGE.value,
        "when_to_answer": "إذا كانت المسألة تقنية صرفة وتوفرت المتطلبات والأدوات.",
        "when_to_suspend": "إذا كانت المتطلبات غامضة، أو المهمة خارج نطاق التقنية.",
        "when_to_request_source": "عند الاستشهاد بمواصفات أو حزم برمجية بعينها؛ اطلب الإصدار أو الوثيقة.",
        "when_to_distinguish_opinion_evidence": "عندما تُقدَّم ممارسة مهنية على أنها قانون مطلق؛ ميّز بين best practice وحقيقة تقنية.",
        "when_to_detect_hallucination": "عندما تُذكر APIs أو مكتبات بتفاصيل غير موجودة؛ تحقق من الوجود الفعلي.",
        "when_to_separate_technical_from_value_shari": "افصل الحكم التقني (هل يعمل؟) عن الحكم القيمي (هل ينبغي؟) وعن الشرعي (هل يجوز؟).",
    },
    {
        "task_type": JudgmentType.VALUE.value,
        "intended_reality": "واقع قيمي: نفع، ضرر، جودة، أو معيار اجتماعي/أخلاقي.",
        "required_evidence": ["contextual", "textual", "historical"],
        "certainty_degree": CertaintyPolicy.HYPOTHESIS.value,
        "when_to_answer": "إذا وجد سياق قيمي واضح وأدلة على النفع أو الضرر، مع ضبط المجال.",
        "when_to_suspend": "إذا خُلط الحكم القيمي بالحكم الشرعي، أو كان المعيار غير محدد.",
        "when_to_request_source": "عند ادعاء قيمة مطلقة بلا معيار؛ اطلب المعيار أو الإطار المرجعي.",
        "when_to_distinguish_opinion_evidence": "دائمًا؛ الأحكام القيمية غالبًا ممزوجة بالرأي الشخصي.",
        "when_to_detect_hallucination": "عند التأكيد المطلق بأن شيئًا ما 'جيد' أو 'ضار' دون دليل أو سياق.",
        "when_to_separate_technical_from_value_shari": "القيمة ليست حكمًا شرعيًا ولا تقنيًا؛ نفع الشيء لا يجعله واجبًا وضرره لا يجعله حرامًا.",
    },
    {
        "task_type": JudgmentType.SHARI.value,
        "intended_reality": "واقع تكليفي: وجوب، تحريم، إباحة، أو ندب؛ يستلزم دليلًا شرعيًا.",
        "required_evidence": ["shari", "textual"],
        "certainty_degree": CertaintyPolicy.SUSPEND.value,
        "when_to_answer": "فقط إذا وجد دليل شرعي صريح (نص أو إجماع)، مع الإشارة لمصدره.",
        "when_to_suspend": "إذا غاب الدليل الشرعي أو تعارضت الأدلة أو كانت المسألة خلافية.",
        "when_to_request_source": "دائمًا؛ الحكم الشرعي لا يصدر بلا نص أو مصدر معتبر.",
        "when_to_distinguish_opinion_evidence": "دائمًا؛ آراء الفقهاء ليست حكمًا قاطعًا ما لم تستند لنص صريح.",
        "when_to_detect_hallucination": "عندما يُقطع بحكم شرعي دون نص، أو تُنسب أقوال لعلماء بلا توثيق.",
        "when_to_separate_technical_from_value_shari": "الحكم الشرعي منفصل عن الحكم التقني والقيمي؛ الضرر لا يساوي التحريم والنفع لا يساوي الوجوب.",
    },
    {
        "task_type": JudgmentType.PRACTICAL.value,
        "intended_reality": "واقع عملي: خطوات، إجراءات، أدوات، أو خطة تنفيذ.",
        "required_evidence": ["technical", "contextual", "textual"],
        "certainty_degree": CertaintyPolicy.STRONG_KNOWLEDGE.value,
        "when_to_answer": "إذا وجد سياق عملي كافٍ وكانت الخطوات قابلة للتنفيذ.",
        "when_to_suspend": "إذا كانت المتطلبات غائبة أو المسألة تحتاج قرارًا قيميًا/شرعيًا أولًا.",
        "when_to_request_source": "عند الاستناد لممارسة محددة أو حزمة أداء؛ اطلب السياق البيئي.",
        "when_to_distinguish_opinion_evidence": "عندما تُقدَّم طريقة عمل كحقيقة مطلقة بدلًا من خيار عملي.",
        "when_to_detect_hallucination": "عند تفصيل خطوات واقعية بادعاء الضمان بلا بيانات تجريبية.",
        "when_to_separate_technical_from_value_shari": "المسألة العملية قد تتقاطع مع القيمة أو الشرع؛ ميّز الطبقات صراحةً.",
    },
    {
        "task_type": JudgmentType.AMBIGUOUS.value,
        "intended_reality": "واقع ملتبس: اللفظ أو السؤال يحتمل معاني متعددة بلا سياق.",
        "required_evidence": ["linguistic", "contextual"],
        "certainty_degree": CertaintyPolicy.SUSPEND.value,
        "when_to_answer": "بعد رفع الالتباس: تشكيل، سياق، أو جملة استعمال.",
        "when_to_suspend": "دائمًا إذا ظل اللفظ ملتبسًا بلا سياق يحدد المعنى.",
        "when_to_request_source": "اطلب سياقًا أو جملة استعمال قبل أي إجابة.",
        "when_to_distinguish_opinion_evidence": "عندما يُفرض معنى بعينه على لفظ ملتبس؛ ميّز بين التأويل والدلالة اللغوية.",
        "when_to_detect_hallucination": "عند الجزم بمعنى لفظ ملتبس كأنه الوحيد الممكن.",
        "when_to_separate_technical_from_value_shari": "الغموض يمنع الحكم بأي نوع؛ لا حكم تقني ولا قيمي ولا شرعي قبل رفع الالتباس.",
    },
    {
        "task_type": JudgmentType.LINGUISTIC.value,
        "intended_reality": "واقع دلالي: معنى لفظ، علاقة دال ومدلول، أو بنية لغوية.",
        "required_evidence": ["linguistic", "contextual", "textual"],
        "certainty_degree": CertaintyPolicy.STRONG_KNOWLEDGE.value,
        "when_to_answer": "إذا كان السؤال لغويًا بحتًا وتوفر سياق استعمال أو دلالة معجمية.",
        "when_to_suspend": "إذا أدى الجواب اللغوي إلى استنتاج شرعي أو قيمي مباشر.",
        "when_to_request_source": "عند الادعاء بأصل لغوي غير موثق؛ اطلب المعجم أو الشاهد.",
        "when_to_distinguish_opinion_evidence": "عندما يُقدَّم تفسير لغوي واحد كأنه الحقيقة الوحيدة.",
        "when_to_detect_hallucination": "عند اختراع اشتقاقات أو أصول لغوية بلا مرجع.",
        "when_to_separate_technical_from_value_shari": "المعنى اللغوي لا يعني الحكم الشرعي ولا القيمي؛ المطابقة والتضمن والالتزام طبقات دلالية لا تكليفية.",
    },
    {
        "task_type": JudgmentType.ANALOGY.value,
        "intended_reality": "واقع قياسي: تشبيه بين شيئين بادعاء جامعية العلة.",
        "required_evidence": ["contextual", "linguistic", "textual"],
        "certainty_degree": CertaintyPolicy.SUSPEND.value,
        "when_to_answer": "فقط بعد تحقق العلة الجامعة وانتفاء الفارق المؤثر.",
        "when_to_suspend": "إذا غابت العلة أو وُجد فارق مؤثر بين المقيس والمقيس عليه.",
        "when_to_request_source": "اطلب العلة الجامعة والمناط قبل قبول القياس.",
        "when_to_distinguish_opinion_evidence": "التشابه السطحي رأي؛ العلة المشتركة المُثبَتة هي الدليل.",
        "when_to_detect_hallucination": "عند نقل حكم كامل بمجرد التشابه الظاهري دون علة.",
        "when_to_separate_technical_from_value_shari": "القياس التقني (تقييس API مثلًا) يختلف عن القياس الشرعي أو القيمي؛ لا تخلط المجالين.",
    },
    {
        "task_type": JudgmentType.METAPHOR.value,
        "intended_reality": "واقع مجازي: تعبير مجازي أو استعارة لا يدل على حقيقة حرفية.",
        "required_evidence": ["linguistic", "contextual"],
        "certainty_degree": CertaintyPolicy.HYPOTHESIS.value,
        "when_to_answer": "بعد كشف المجاز وبيان المعنى المقصود في سياقه.",
        "when_to_suspend": "إذا كان المجاز يُوهم حكمًا واقعيًا حرفيًا مباشرًا.",
        "when_to_request_source": "اطلب السياق لتحديد ما إذا كانت العبارة مجازًا أم وصفًا واقعيًا.",
        "when_to_distinguish_opinion_evidence": "المجاز يعبر عن موقف أو صورة لا يثبت بها حكم واقعي.",
        "when_to_detect_hallucination": "عند التعامل مع الاستعارة كحقيقة وصفية ثم بناء استنتاجات واقعية عليها.",
        "when_to_separate_technical_from_value_shari": "المجاز لا يُفيد حكمًا شرعيًا ولا تقنيًا مباشرًا؛ نبّه إلى طبيعة العبارة أولًا.",
    },
    {
        # task_type value is "usuli_reasoning" — matching JudgmentType.USULI.value
        "task_type": JudgmentType.USULI.value,
        "intended_reality": "واقع منهجي أصولي: قاعدة استدلالية أو مفهوم أصول الفقه.",
        "required_evidence": ["textual", "linguistic", "contextual"],
        "certainty_degree": CertaintyPolicy.HYPOTHESIS.value,
        "when_to_answer": "إذا وجد تعريف أصولي واضح مع ضبط شروط تطبيقه.",
        "when_to_suspend": "إذا أُطلقت القاعدة بلا ضبط مجالها أو شروطها.",
        "when_to_request_source": "اطلب المصدر الأصولي أو الشاهد الفقهي قبل تطبيق القاعدة.",
        "when_to_distinguish_opinion_evidence": "القاعدة الأصولية قابلة للاستثناء؛ ميّز بين القاعدة الكلية والتطبيق الجزئي.",
        "when_to_detect_hallucination": "عند نسبة قاعدة أصولية بصياغة معينة لمذهب بلا توثيق.",
        "when_to_separate_technical_from_value_shari": "الحكم الأصولي حكم منهجي؛ لا يُساوى بالحكم التقني ولا يُختزل في الحكم القيمي.",
    },
]


# ---------------------------------------------------------------------------
# Matrix class
# ---------------------------------------------------------------------------

class JudgmentRoutingMatrix:
    """Look up the 10-dimension routing policy for a given task type.

    Usage::

        matrix = JudgmentRoutingMatrix()
        entry = matrix.get(JudgmentType.SHARI)
        print(entry.when_to_suspend)
    """

    def __init__(self, entries: list[MatrixEntry] | None = None) -> None:
        if entries is not None:
            self._entries: dict[str, MatrixEntry] = {e.task_type: e for e in entries}
        else:
            self._entries = {
                d["task_type"]: MatrixEntry.from_dict(d) for d in _DEFAULT_ENTRIES
            }

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, task_type: str) -> MatrixEntry | None:
        """Return the MatrixEntry for *task_type*, or None if not found."""
        return self._entries.get(task_type)

    def require(self, task_type: str) -> MatrixEntry:
        """Return the MatrixEntry, raising KeyError if missing."""
        entry = self._entries.get(task_type)
        if entry is None:
            raise KeyError(f"No matrix entry for task_type={task_type!r}")
        return entry

    def all_entries(self) -> list[MatrixEntry]:
        return list(self._entries.values())

    def task_types(self) -> list[str]:
        return list(self._entries.keys())

    def __iter__(self) -> Iterator[MatrixEntry]:
        return iter(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self._entries.values()]

    def save(self, path: Path | None = None) -> None:
        target = path or _MATRIX_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(self.to_list(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path | None = None) -> "JudgmentRoutingMatrix":
        source = path or _MATRIX_FILE
        with open(source, encoding="utf-8") as f:
            data = json.load(f)
        return cls(entries=[MatrixEntry.from_dict(d) for d in data])

    # ------------------------------------------------------------------
    # Policy helpers — query the 10 dimensions directly
    # ------------------------------------------------------------------

    def should_suspend(self, task_type: str, certainty_policy: str | None = None) -> bool:
        """Return True if the routing matrix says this task type should suspend."""
        entry = self._entries.get(task_type)
        if entry is None:
            return False
        if entry.certainty_degree == CertaintyPolicy.SUSPEND:
            return True
        if certainty_policy == CertaintyPolicy.SUSPEND:
            return True
        return False

    def required_evidence(self, task_type: str) -> tuple[str, ...]:
        """Return the required evidence tuple for a task type."""
        entry = self._entries.get(task_type)
        return entry.required_evidence if entry else ()

    def when_to_answer(self, task_type: str) -> str:
        """Return the 'when to answer' policy text for a task type."""
        entry = self._entries.get(task_type)
        return entry.when_to_answer if entry else ""

    def when_to_suspend(self, task_type: str) -> str:
        """Return the 'when to suspend' policy text for a task type."""
        entry = self._entries.get(task_type)
        return entry.when_to_suspend if entry else ""

    def when_to_request_source(self, task_type: str) -> str:
        """Return the 'when to request source' policy text."""
        entry = self._entries.get(task_type)
        return entry.when_to_request_source if entry else ""

    def when_to_distinguish_opinion_evidence(self, task_type: str) -> str:
        """Return the 'opinion vs evidence' policy text."""
        entry = self._entries.get(task_type)
        return entry.when_to_distinguish_opinion_evidence if entry else ""

    def when_to_detect_hallucination(self, task_type: str) -> str:
        """Return the 'detect hallucination' policy text."""
        entry = self._entries.get(task_type)
        return entry.when_to_detect_hallucination if entry else ""

    def when_to_separate_technical_from_value_shari(self, task_type: str) -> str:
        """Return the 'separate technical from value/shari' policy text."""
        entry = self._entries.get(task_type)
        return entry.when_to_separate_technical_from_value_shari if entry else ""

    # ------------------------------------------------------------------
    # Markdown rendering
    # ------------------------------------------------------------------

    def to_markdown(self) -> str:
        """Render the matrix as a Markdown table (Arabic-friendly)."""
        headers = [
            "نوع المهمة",
            "الواقع المقصود",
            "الدليل المطلوب",
            "درجة اليقين",
            "متى تجيب",
            "متى تعلق",
            "متى تطلب مصدرًا",
            "متى تميز بين رأي ودليل",
            "متى تكشف الهلوسة",
            "متى تفرق بين حكم تقني وحكم قيمي أو شرعي",
        ]
        sep = "|".join(["---"] * len(headers))
        lines = [
            "| " + " | ".join(headers) + " |",
            "|" + sep + "|",
        ]
        for entry in self._entries.values():
            row = [
                entry.task_type,
                entry.intended_reality,
                ", ".join(entry.required_evidence),
                entry.certainty_degree,
                entry.when_to_answer,
                entry.when_to_suspend,
                entry.when_to_request_source,
                entry.when_to_distinguish_opinion_evidence,
                entry.when_to_detect_hallucination,
                entry.when_to_separate_technical_from_value_shari,
            ]
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
