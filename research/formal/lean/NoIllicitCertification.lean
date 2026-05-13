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

theorem no_illicit_certification (s : GovernanceState) :
    publicJudgment s = PublicJudgment.certificate → certificateAllowed s = true := by
  intro h
  unfold publicJudgment at h
  by_cases hRecognized : !s.recognizedInput
  · simp [hRecognized] at h
  · by_cases hAllowed : certificateAllowed s
    · simpa [hAllowed] using hAllowed
    · simp [hRecognized, hAllowed] at h

theorem missing_gate_blocks_certificate
    (s : GovernanceState)
    (h :
      s.hasProofObject = false ∨
        s.governanceGatePassed = false ∨
          s.reverseTraceComplete = false ∨ s.evidenceMatchesClaim = false) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rcases h with hProof | hRest
  · rw [hProof] at hAllowed
    simp at hAllowed
  · rcases hRest with hGate | hRest2
    · rw [hGate] at hAllowed
      simp at hAllowed
    · rcases hRest2 with hTrace | hEvidence
      · rw [hTrace] at hAllowed
        simp at hAllowed
      · rw [hEvidence] at hAllowed
        simp at hAllowed

theorem forbidden_transition_blocks_certificate
    (s : GovernanceState)
    (hForbidden : s.forbiddenTransition = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hForbidden] at hAllowed
  simp at hAllowed

theorem residual_erasure_blocks_certificate
    (s : GovernanceState)
    (hResidual : s.residualErasure = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hResidual] at hAllowed
  simp at hAllowed

theorem complete_gates_enable_certificate
    (s : GovernanceState)
    (hRecognized : s.recognizedInput = true)
    (hProof : s.hasProofObject = true)
    (hGate : s.governanceGatePassed = true)
    (hTrace : s.reverseTraceComplete = true)
    (hEvidence : s.evidenceMatchesClaim = true)
    (hForbidden : s.forbiddenTransition = false)
    (hResidual : s.residualErasure = false) :
    publicJudgment s = PublicJudgment.certificate := by
  unfold publicJudgment certificateAllowed
  simp [hRecognized, hProof, hGate, hTrace, hEvidence, hForbidden, hResidual]

