import json
from pathlib import Path


def test_examples_validate():
    root = Path(__file__).resolve().parents[1] / "examples" / "coding_copilot"
    files = sorted(root.glob("*.json"))
    assert len(files) == 6

    required = {
        "issue",
        "repo_context",
        "code_claims",
        "patch_plan",
        "patch_artifact",
        "evidence",
        "residuals",
        "reverse_trace",
        "final_judgment",
    }

    for file_path in files:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        assert required.issubset(payload.keys()), file_path.name
        assert payload["final_judgment"] in {"zero", "hypothesis", "certificate"}
