import research.formal.lean.CoreJudgment

theorem triad_closure (s : GovernanceState) :
    publicJudgment s = PublicJudgment.zero ∨
      publicJudgment s = PublicJudgment.hypothesis ∨
        publicJudgment s = PublicJudgment.certificate := by
  unfold publicJudgment
  by_cases hAllowed : certificateAllowed s
  · simp [hAllowed]
  · simp [hAllowed]

theorem triad_type_closure (s : GovernanceState) :
    ∃ j : PublicJudgment, publicJudgment s = j := by
  exact ⟨publicJudgment s, rfl⟩
