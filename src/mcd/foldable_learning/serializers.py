"""Serializers for foldable learning types."""
from __future__ import annotations
from .fold_schema import FoldSignature
from mcd.residual_learning.residual_schema import CognitiveResidual

__all__ = ["serialize_fold_signature", "serialize_residual"]


def serialize_fold_signature(sig: FoldSignature) -> dict:
    return sig.to_dict()


def serialize_residual(r: CognitiveResidual) -> dict:
    return r.to_dict()
