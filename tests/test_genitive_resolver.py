"""Tests for GenitiveResolver."""
import pytest
from mcd.murab.genitive_resolver import GenitiveResolver


def test_genitive_preposition():
    resolver = GenitiveResolver()
    result = resolver.resolve("المدرسةِ", ["ذهبتُ", "إلى", "المدرسةِ"], 2)
    assert result == "object_of_preposition"


def test_genitive_mudaf_ilayh():
    resolver = GenitiveResolver()
    result = resolver.resolve("الطالبِ", ["كتابُ", "الطالبِ"], 1)
    assert result == "mudaf_ilayh"


def test_genitive_idafa_not_always_ownership():
    """Idafa can express specification not just ownership."""
    resolver = GenitiveResolver()
    result = resolver.resolve("العلمِ", ["كتابُ", "العلمِ"], 1)
    # The result is mudaf_ilayh regardless of semantic relation
    assert result == "mudaf_ilayh"


def test_genitive_preposition_min():
    resolver = GenitiveResolver()
    result = resolver.resolve("المغربِ", ["أقبلَ", "من", "المغربِ"], 2)
    assert result == "object_of_preposition"


def test_genitive_to_dict():
    resolver = GenitiveResolver()
    result = resolver.resolve("البيتِ", ["في", "البيتِ"], 1)
    assert isinstance(result, str)
    assert result in ("object_of_preposition", "mudaf_ilayh")
