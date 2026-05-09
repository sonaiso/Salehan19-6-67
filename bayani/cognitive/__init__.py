"""Bayani Cognitive Layer — العقل المعرفي المستدل.

This package implements the full fractal cognitive pipeline described in the
Nabhani-grounded epistemological framework:

    Unicode Seed → Atomic Feature Vector → Role Vector
    → Fractal Composition → Relation Graph → Evidence Gate
    → Certainty Score → Learning Update
    = Simulated Cognitive Reasoning Mind

Public API
----------
.. code-block:: python

    from bayani.cognitive import CognitiveReasoningMind

    mind = CognitiveReasoningMind()

    # Knower mode — reason from existing knowledge
    answer, verified = mind.reason("كتب الطالب الدرس")

    # Learner mode — reason AND update memory from new evidence
    answer, verified = mind.reason(
        "شبكة الحاسوب مترابطة",
        external_evidence=["repeated_digital_contexts"],
        allow_learning=True,
    )
"""

from bayani.cognitive.knowledge_node import KnowledgeNode, NodeLevel, CertaintyInfo
from bayani.cognitive.unicode_encoder import UnicodeAtomicEncoder
from bayani.cognitive.role_vectorizer import RoleVectorizer
from bayani.cognitive.arabic_morphology import ArabicMorphologyAnalyzer
from bayani.cognitive.fractal_composer import FractalComposer
from bayani.cognitive.memory import ThreeLayerMemory
from bayani.cognitive.certainty import MultiDimensionalCertaintyScorer
from bayani.cognitive.mind import CognitiveReasoningMind

__all__ = [
    "CognitiveReasoningMind",
    "KnowledgeNode",
    "NodeLevel",
    "CertaintyInfo",
    "UnicodeAtomicEncoder",
    "RoleVectorizer",
    "ArabicMorphologyAnalyzer",
    "FractalComposer",
    "ThreeLayerMemory",
    "MultiDimensionalCertaintyScorer",
]
