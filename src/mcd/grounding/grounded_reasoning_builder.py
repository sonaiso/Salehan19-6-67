"""GroundedReasoningBuilder — full GLCFL pipeline."""
from __future__ import annotations

from mcd.grounding.grounded_frame import GroundedReasoningFrame
from mcd.grounding.lexical_grounding import LexicalGroundingEngine
from mcd.grounding.role_frame import RoleFrameBuilder
from mcd.grounding.nisbah_frame import NisbahFrameBuilder
from mcd.grounding.usul_semantics import AdvancedArabicUsulSemantics, DalalahType
from mcd.grounding.manat_engine import ManatApplicabilityEngine
from mcd.grounding.usuli_tarjih import UsuliTarjihEngine, ConflictType
from mcd.grounding.value_system import ValueSystemModel
from mcd.grounding.civilization_civility_classifier import CivilizationCivilityDeepClassifier
from mcd.grounding.society_model import SocietyModel
from mcd.grounding.idea_method_pair import IdeaMethodPairModel
from mcd.grounding.system_derivation import SystemDerivationModel
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data

# Value-related keywords
_VALUE_KEYWORDS = {
    "ضار", "نافع", "حرام", "واجب", "مندوب", "مكروه", "مباح", "جائز",
    "صحيح", "خطأ", "جميل", "قبيح", "مقبول", "مرفوض", "محرم",
}

# Civilization / civility keywords
_CIVILITY_KEYWORDS = {
    "الذكاء", "الاصطناعي", "حضارة", "مدنية", "تقنية", "أداة",
    "الديمقراطية", "الحرية", "العدالة",
}

# Society keywords
_SOCIETY_KEYWORDS = {
    "المجتمع", "مجتمع", "الناس", "الجماعة", "شخص", "فرد",
}

# Idea/method keywords
_IDEA_KEYWORDS = {"نظام", "فكرة", "مبدأ", "هدف", "تعليم", "تربية"}
_METHOD_KEYWORDS = {"طريقة", "أسلوب", "منهج", "وسيلة", "أداة"}

# System keywords
_SYSTEM_KEYWORDS = {"نظام", "منظومة"}


# Named constants for certainty thresholds
_GROUNDED_THRESHOLD = 0.7
_PARTIALLY_GROUNDED_THRESHOLD = 0.3


def _words(text: str) -> set[str]:
    return set(text.split())


class GroundedReasoningBuilder:
    """Orchestrates the full GLCFL pipeline."""

    def __init__(self, store: PriorKnowledgeStore | None = None) -> None:
        if store is None:
            store = PriorKnowledgeStore()
            load_seed_data(store)
        self._store = store
        self._lexical = LexicalGroundingEngine(store)
        self._role_builder = RoleFrameBuilder()
        self._nisbah_builder = NisbahFrameBuilder()
        self._usul = AdvancedArabicUsulSemantics()
        self._manat = ManatApplicabilityEngine()
        self._tarjih = UsuliTarjihEngine()
        self._value = ValueSystemModel()
        self._civilization = CivilizationCivilityDeepClassifier()
        self._society = SocietyModel()
        self._idea_method = IdeaMethodPairModel()
        self._system_deriv = SystemDerivationModel()

    def build(self, text: str, include_debug: bool = False) -> GroundedReasoningFrame:
        frame = GroundedReasoningFrame(input_text=text)
        all_warnings: list[str] = []
        words = _words(text)

        # 1. Try FPCL classify
        try:
            from mcd.classification.fractal_prompt_classifier import FractalPromptClassifier
            fpc = FractalPromptClassifier()
            prompt_frame = fpc.classify(text, include_debug=include_debug)
            frame.prompt_frame = {
                "intent": prompt_frame.intent,
                "routing_engine": prompt_frame.routing_engine,
                "certainty_policy": prompt_frame.certainty_policy,
                "warnings": prompt_frame.warnings,
            }
        except Exception as exc:  # noqa: BLE001
            all_warnings.append(f"fpcl_error: {exc}")

        # 2. Try MCD decode
        try:
            from mcd.engines.decoder import MinimalCognitiveDecoder
            decoder = MinimalCognitiveDecoder(store=self._store)
            mcd_result = decoder.decode(text)
            frame.mcd_analysis = {
                "answer": mcd_result.answer,
                "certainty": mcd_result.certainty,
                "claims": mcd_result.claims,
            }
        except Exception as exc:  # noqa: BLE001
            all_warnings.append(f"mcd_error: {exc}")

        # 3. Try NERL nabhani decode
        try:
            from mcd.nabhani.nabhani_decoder import NabhaniDecoder
            nd = NabhaniDecoder()
            nabhani_result = nd.decode(text)
            frame.nabhani_analysis = {
                "epistemic_status": nabhani_result.get("epistemic_status"),
                "final_answer": nabhani_result.get("final_answer"),
                "certainty": nabhani_result.get("certainty", {}).get("score", 0.0),
            }
        except Exception as exc:  # noqa: BLE001
            all_warnings.append(f"nerl_error: {exc}")

        # 4. Ground each lexeme
        tokens = text.strip().split()
        grounded_lexemes = []
        for token in tokens:
            clean = token.replace("؟", "").replace("،", "").replace(".", "").strip()
            if clean:
                lex = self._lexical.ground(clean, context=text)
                grounded_lexemes.append(lex)
        frame.grounded_lexemes = grounded_lexemes

        # 5. Build RoleFrame
        role_frame = self._role_builder.build(text)
        frame.role_frames = [role_frame]

        # 6. Build NisbahFrames
        nisbah_frames = self._nisbah_builder.build(role_frame)
        frame.nisbah_frames = nisbah_frames

        # 7. Build UsulSemanticFrames for key terms
        usul_frames = []
        for lex in grounded_lexemes:
            if lex.madlul:
                usf = self._usul.analyze(dal=lex.surface, madlul=lex.madlul)
                usul_frames.append(usf)
                all_warnings.extend(usf.warnings)
        frame.usul_semantics = usul_frames

        # 8. Run ValueSystem if value terms detected
        if words & _VALUE_KEYWORDS:
            value_frames = self._value.analyze(text)
            frame.value_frames = value_frames
            for vf in value_frames:
                all_warnings.extend(vf.warnings)

        # 9. Run CivilizationCivility if relevant terms
        if words & _CIVILITY_KEYWORDS:
            civ_frames = []
            for word in words & _CIVILITY_KEYWORDS:
                result = self._civilization.classify(word, context=text)
                civ_frames.append(result)
            frame.civilization_frames = civ_frames

        # 10. Run SocietyModel if societal terms
        if words & _SOCIETY_KEYWORDS:
            society_frame = self._society.analyze(text)
            frame.social_frames = [society_frame]
            all_warnings.extend(society_frame.warnings)

        # 11. Run IdeaMethodPair if idea/method keywords
        if (words & _IDEA_KEYWORDS) and (words & _METHOD_KEYWORDS | {"لـ", "لتربية", "لتعليم"}):
            idea_pair = self._idea_method.extract(text)
            if idea_pair:
                frame.system_frames = [idea_pair]

        # 12. Run SystemDerivation if system keywords
        if words & _SYSTEM_KEYWORDS and not frame.system_frames:
            sys_deriv = self._system_deriv.derive(text)
            if sys_deriv:
                frame.system_frames = [sys_deriv]

        # 13. Aggregate warnings and compute certainty summary
        frame.warnings = list(dict.fromkeys(all_warnings))  # deduplicate

        certainty_scores = [lex.certainty for lex in grounded_lexemes if lex.certainty > 0]
        if certainty_scores:
            frame.certainty_summary = sum(certainty_scores) / len(certainty_scores)
        else:
            frame.certainty_summary = 0.0

        # 14. Determine final status
        if frame.certainty_summary >= _GROUNDED_THRESHOLD:
            frame.final_status = "grounded"
        elif frame.certainty_summary >= _PARTIALLY_GROUNDED_THRESHOLD:
            frame.final_status = "partially_grounded"
        else:
            frame.final_status = "ungrounded"

        # 15. Final answer from NERL if available
        if frame.nabhani_analysis:
            frame.final_answer = frame.nabhani_analysis.get("final_answer", "")
        elif frame.mcd_analysis:
            frame.final_answer = frame.mcd_analysis.get("answer", "")

        return frame
