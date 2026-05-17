"""Phase 3B-1 — Governed Arabic quantity mention extraction.

This module implements the *first* local quantitative-reasoning operator for
the Phase 3B chain. Its sole responsibility is the typed transition::

    PromptTextSpan / ArabicSpan -> QuantityMention

It MUST NOT compute final answers, feasibility, or any judgment beyond
``JUDGMENT_HYPOTHESIS``. Later phases (3B-2 … 3B-6) will add
``UnitNormalization``, ``RoleBinding``, ``LawSelection``,
``ConstraintEvaluation``, and a ``QuantitativeProofObject``.
"""
from __future__ import annotations

from mcd.quantity_extraction.extractor import (
    QUANTITY_EXTRACTION_CONTRACT_VERSION,
    QUANTITY_EXTRACTION_OPERATOR_ID,
    QUANTITY_EXTRACTION_SCHEMA_VERSION,
    QuantityMention,
    build_quantity_extraction_operator_contract,
    build_quantity_extraction_payload,
    deserialize_quantity_extraction_payload,
    extract_quantity_mentions,
    serialize_quantity_extraction_payload,
    validate_quantity_extraction_payload,
)

__all__ = [
    "QUANTITY_EXTRACTION_CONTRACT_VERSION",
    "QUANTITY_EXTRACTION_OPERATOR_ID",
    "QUANTITY_EXTRACTION_SCHEMA_VERSION",
    "QuantityMention",
    "build_quantity_extraction_operator_contract",
    "build_quantity_extraction_payload",
    "deserialize_quantity_extraction_payload",
    "extract_quantity_mentions",
    "serialize_quantity_extraction_payload",
    "validate_quantity_extraction_payload",
]
