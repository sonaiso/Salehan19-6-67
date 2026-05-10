from __future__ import annotations
import json
from typing import Any

from .fractal_unit import CognitiveFractalUnit
from .level_morphism import LevelMorphism
from .vector_space_registry import UnifiedVector, VectorDimension
from .operator_algebra import CognitiveOperator
from .fold_laws import FoldOperation, UnfoldOperation, RefoldCheck
from .conflict_resolver import CrossLayerConflict
from .concept_center_memory import ConceptCenterRecord
from .pattern_memory import FractalPattern
from .proof_object import ProofObject
from .reverse_trace import ReverseTrace
from .jami_mani_metrics import JamiManiReport
from .residual_folding_contract import GPTResidualFoldingContract
from .kernel_validator import KernelValidationReport


def to_json(obj: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    if hasattr(obj, "to_dict"):
        return json.dumps(obj.to_dict(), indent=indent, ensure_ascii=ensure_ascii)
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)
