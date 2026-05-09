"""Benchmark profiles — manages evaluation profiles."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from mcd.evaluation.dataset_schema import BenchmarkExample

DEFAULT_PROFILES_PATH = Path(__file__).parent.parent.parent.parent / "data" / "evaluation" / "benchmark_profiles.json"


@dataclass
class BenchmarkProfile:
    name: str
    description: str
    count: int
    sources: list[str]
    filters: dict

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "count": self.count,
            "sources": self.sources,
            "filters": self.filters,
        }


class BenchmarkProfileManager:
    def __init__(self, profiles_path: Path = DEFAULT_PROFILES_PATH):
        with open(profiles_path, encoding="utf-8") as f:
            data = json.load(f)
        self.profiles: dict[str, BenchmarkProfile] = {
            k: BenchmarkProfile(**v)
            for k, v in data["profiles"].items()
        }

    def get_profile(self, name: str) -> BenchmarkProfile:
        if name not in self.profiles:
            raise KeyError(f"Unknown profile: {name}. Available: {list(self.profiles.keys())}")
        return self.profiles[name]

    def list_profiles(self) -> list[str]:
        return list(self.profiles.keys())

    def get_examples(self, profile_name: str, data_dir: Path | None = None) -> list[BenchmarkExample]:
        from mcd.evaluation.dataset_loader import load_all, DEFAULT_DATA_DIR
        profile = self.get_profile(profile_name)
        if data_dir is None:
            data_dir = DEFAULT_DATA_DIR
        all_examples = load_all(data_dir)
        filtered = [ex for ex in all_examples if ex.source_type in profile.sources]
        if profile.filters.get("tags"):
            filter_tags = set(profile.filters["tags"])
            filtered = [ex for ex in filtered if filter_tags & set(ex.tags)]
        if profile.filters.get("difficulty"):
            filter_difficulties = set(profile.filters["difficulty"])
            filtered = [ex for ex in filtered if ex.difficulty in filter_difficulties]
        return filtered[:profile.count]
