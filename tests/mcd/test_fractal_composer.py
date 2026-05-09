"""Tests for FractalComposer."""
from __future__ import annotations

import pytest
from mcd.engines.fractal_composer import FractalComposer
from mcd.core.nodes import KnowledgeNode
from mcd.core.certainty import Certainty


@pytest.fixture
def composer():
    return FractalComposer()


def _make_char_node(ch: str) -> KnowledgeNode:
    return KnowledgeNode(
        node_id=f"char_{ch}",
        level="letter",
        surface=ch,
        certainty=Certainty.from_score(0.8),
    )


def _make_word_node(word: str) -> KnowledgeNode:
    return KnowledgeNode(
        node_id=f"word_{word}",
        level="word",
        surface=word,
        certainty=Certainty.from_score(0.75),
    )


def test_compose_chars_produces_word_node(composer):
    chars = [_make_char_node(c) for c in 'كتب']
    word_node = composer.compose_word(chars)
    assert word_node.level == "word"


def test_word_node_surface_matches(composer):
    chars = [_make_char_node(c) for c in 'كتب']
    word_node = composer.compose_word(chars)
    assert word_node.surface == 'كتب'


def test_compose_phrase(composer):
    words = [_make_word_node(w) for w in ['كتب', 'الطالب']]
    phrase = composer.compose_phrase(words)
    assert phrase.level in ("phrase", "sentence")


def test_compose_empty_units(composer):
    node = composer.compose([])
    assert node.level == "concept"


def test_compose_word_nodes_gives_phrase(composer):
    words = [_make_word_node(w) for w in ['النار', 'تحرق']]
    result = composer.compose(words)
    assert result.level in ("phrase", "sentence")
