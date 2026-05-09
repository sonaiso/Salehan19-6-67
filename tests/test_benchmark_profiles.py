"""Tests for benchmark_profiles.py"""
import pytest
from mcd.evaluation.benchmark_profiles import BenchmarkProfileManager, BenchmarkProfile
from mcd.evaluation.dataset_schema import BenchmarkExample


@pytest.fixture
def manager():
    return BenchmarkProfileManager()


def test_manager_loads_profiles(manager):
    profiles = manager.list_profiles()
    assert len(profiles) >= 5


def test_expected_profiles_exist(manager):
    expected = {"quick", "standard", "full", "adversarial", "gpt55_simulation"}
    assert expected.issubset(set(manager.list_profiles()))


def test_get_profile(manager):
    profile = manager.get_profile("quick")
    assert isinstance(profile, BenchmarkProfile)
    assert profile.name == "quick"
    assert profile.count == 50


def test_get_unknown_profile_raises(manager):
    with pytest.raises(KeyError):
        manager.get_profile("nonexistent_profile")


def test_profile_to_dict(manager):
    profile = manager.get_profile("standard")
    d = profile.to_dict()
    assert "name" in d
    assert "description" in d
    assert "count" in d
    assert "sources" in d
    assert "filters" in d


def test_get_examples_quick(manager):
    examples = manager.get_examples("quick")
    assert len(examples) > 0
    assert all(isinstance(ex, BenchmarkExample) for ex in examples)
    assert len(examples) <= 50


def test_get_examples_adversarial_profile(manager):
    examples = manager.get_examples("adversarial")
    assert len(examples) > 0
    assert all(ex.source_type == "adversarial" for ex in examples)


def test_gpt55_simulation_profile(manager):
    profile = manager.get_profile("gpt55_simulation")
    assert "static_gold" in profile.sources
    assert "tags" in profile.filters


def test_full_profile_includes_all_sources(manager):
    profile = manager.get_profile("full")
    expected_sources = {"static_gold", "dynamic_generated", "adversarial", "ambiguity", "calibration"}
    assert expected_sources.issubset(set(profile.sources))
