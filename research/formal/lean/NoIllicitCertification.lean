import research.formal.lean.CoreJudgment

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
