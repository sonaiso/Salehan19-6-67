from mcd.coding_copilot.patch_artifact import PatchArtifact


def test_unlinked_changed_file_zero():
    artifact = PatchArtifact(
        patch_id="A-1",
        changed_files=["src/a.py"],
        additions=3,
        deletions=1,
        linked_claims={},
    )
    artifact.ensure_consistency()
    assert any(r.residual_type == "unlinked_patch_file" for r in artifact.residuals)
