"""Architecture Audit — checks layer separation, independence, and modularity."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class ArchitectureAuditResult:
    layer_separation_score: float
    modularity_score: float
    dependency_risk_score: float
    deterministic_core_score: float
    integration_score: float
    overall_score: float
    findings: list[str]
    risks: list[str]
    recommendations: list[str]

    def maturity_label(self) -> str:
        if self.overall_score >= 0.80:
            return "strong"
        if self.overall_score >= 0.60:
            return "acceptable prototype"
        if self.overall_score >= 0.40:
            return "research prototype"
        return "weak"


class ArchitectureAudit:
    LAYERS = ["core", "engines", "knowledge", "nabhani", "classification", "grounding", "evaluation"]

    def __init__(self, root: str | None = None) -> None:
        if root is None:
            self._root = Path(__file__).resolve().parents[3]
        else:
            self._root = Path(root)
        self._src_mcd = self._root / "src" / "mcd"

    def run(self) -> ArchitectureAuditResult:
        findings: list[str] = []
        risks: list[str] = []
        recommendations: list[str] = []

        # 1. Layer separation: each layer has __init__.py
        present = [l for l in self.LAYERS if (self._src_mcd / l / "__init__.py").exists()]
        layer_separation_score = len(present) / len(self.LAYERS)
        if layer_separation_score < 1.0:
            missing = [l for l in self.LAYERS if l not in present]
            findings.append(f"Missing layer __init__.py: {missing}")

        # 2. Modularity: check each layer has >1 file
        multi_file_layers = 0
        for l in present:
            files = list((self._src_mcd / l).glob("*.py"))
            if len(files) > 2:  # __init__.py + at least 2 modules
                multi_file_layers += 1
        modularity_score = multi_file_layers / max(len(present), 1)

        # 3. Dependency risk: check for circular-like cross-imports
        # Check if core imports from engines/nabhani (bad)
        core_files = list((self._src_mcd / "core").rglob("*.py")) if (self._src_mcd / "core").exists() else []
        bad_core_imports = 0
        for f in core_files:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"from mcd\.(engines|nabhani|classification)", content):
                bad_core_imports += 1
                risks.append(f"Core file {f.name} imports from higher layer")
        dependency_risk_score = max(0.0, 1.0 - (bad_core_imports * 0.3))

        # 4. Deterministic core: check no LLM calls in classifiers
        clf_files = list((self._src_mcd / "classification").rglob("*.py")) if (self._src_mcd / "classification").exists() else []
        llm_in_clf = 0
        for f in clf_files:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"openai|anthropic|huggingface|transformers|torch\.", content, re.IGNORECASE):
                llm_in_clf += 1
                risks.append(f"LLM dependency detected in classifier: {f.name}")
        deterministic_core_score = max(0.0, 1.0 - (llm_in_clf * 0.5))

        # 5. Integration score: CLI exists + multiple layers integrated
        cli_exists = (self._src_mcd / "cli.py").exists()
        integration_score = 0.5 if cli_exists else 0.0
        if len(present) >= 4:
            integration_score += 0.3
        if len(present) >= 6:
            integration_score += 0.2

        scores = [layer_separation_score, modularity_score, dependency_risk_score, deterministic_core_score, integration_score]
        overall_score = sum(scores) / len(scores)

        if modularity_score < 0.7:
            recommendations.append("Increase module count per layer for better modularity")
        if dependency_risk_score < 0.8:
            recommendations.append("Reduce cross-layer imports in core modules")
        if integration_score < 0.7:
            recommendations.append("Add CLI integration for all major layers")

        findings.append(f"Layers present: {present}")
        findings.append(f"Overall architecture score: {overall_score:.2f} ({ArchitectureAuditResult(layer_separation_score, modularity_score, dependency_risk_score, deterministic_core_score, integration_score, overall_score, [], [], []).maturity_label()})")

        return ArchitectureAuditResult(
            layer_separation_score=round(layer_separation_score, 3),
            modularity_score=round(modularity_score, 3),
            dependency_risk_score=round(dependency_risk_score, 3),
            deterministic_core_score=round(deterministic_core_score, 3),
            integration_score=round(integration_score, 3),
            overall_score=round(overall_score, 3),
            findings=findings,
            risks=risks,
            recommendations=recommendations,
        )
