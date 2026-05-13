/-!
Standalone minimal theorem file for PR #74.
No external imports required so this can be checked file-by-file.
-/

inductive PublicJudgment where
  | zero
  | hypothesis
  | certificate
  deriving DecidableEq, Repr

structure GovernanceState where
  recognizedInput : Bool
  hasProofObject : Bool
  governanceGatePassed : Bool
  reverseTraceComplete : Bool
  evidenceMatchesClaim : Bool
  forbiddenTransition : Bool
  residualErasure : Bool
  deriving Repr

def certificateAllowed (s : GovernanceState) : Bool :=
  s.hasProofObject && s.governanceGatePassed && s.reverseTraceComplete && s.evidenceMatchesClaim &&
    (!s.forbiddenTransition) && (!s.residualErasure)

def publicJudgment (s : GovernanceState) : PublicJudgment :=
  if !s.recognizedInput then
    PublicJudgment.zero
  else if certificateAllowed s then
    PublicJudgment.certificate
  else
    PublicJudgment.hypothesis

theorem triad_closure (s : GovernanceState) :
    publicJudgment s = PublicJudgment.zero ∨
      publicJudgment s = PublicJudgment.hypothesis ∨
        publicJudgment s = PublicJudgment.certificate := by
  unfold publicJudgment
  by_cases hRecognized : !s.recognizedInput
  · simp [hRecognized]
  · by_cases hAllowed : certificateAllowed s
    · simp [hRecognized, hAllowed]
    · simp [hRecognized, hAllowed]

theorem triad_type_closure (s : GovernanceState) :
    ∃ j : PublicJudgment, publicJudgment s = j := by
  exact ⟨publicJudgment s, rfl⟩

