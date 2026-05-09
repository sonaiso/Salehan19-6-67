"""Minimal Cognitive Decoder — طبقة معرفية مستدلة.

A cognitive reasoning layer that works above or without LLMs,
implementing evidence-gated, certainty-scored knowledge processing
for Arabic text.
"""
from __future__ import annotations

from mcd.engines.decoder import MinimalCognitiveDecoder
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data

__version__ = "0.1.0"
__all__ = ["MinimalCognitiveDecoder", "PriorKnowledgeStore", "load_seed_data"]
