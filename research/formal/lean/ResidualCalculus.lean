/-!
PR #75 typed residual calculus and blocking rules.
Scope: minimal machine-checkable extension only.
-/

inductive PublicJudgment where
  | zero
  | hypothesis
  | certificate
  deriving DecidableEq, Repr

inductive EpistemicRank where
  | zero
  | hypothesis
  | evidence
  | certified
  deriving DecidableEq, Repr

def rankValue : EpistemicRank → Nat
  | EpistemicRank.zero => 0
  | EpistemicRank.hypothesis => 1
  | EpistemicRank.evidence => 2
  | EpistemicRank.certified => 3

def rankLeq (a b : EpistemicRank) : Bool :=
  decide (rankValue a ≤ rankValue b)

def requiredRank : PublicJudgment → EpistemicRank
  | PublicJudgment.zero => EpistemicRank.zero
  | PublicJudgment.hypothesis => EpistemicRank.hypothesis
  | PublicJudgment.certificate => EpistemicRank.certified

def certificateRequiredRank : EpistemicRank :=
  requiredRank PublicJudgment.certificate

inductive Residual where
  | missingEvidence
  | rankGap
  | semanticDrift
  | reverseTraceGap
  | governanceFailure
  | unresolvedConflict
  | residualErasure
  deriving DecidableEq, Repr

abbrev ResidualSet := Residual → Bool

structure GovernanceState where
  recognizedInput : Bool
  hasProofObject : Bool
  governanceGatePassed : Bool
  reverseTraceComplete : Bool
  evidenceMatchesClaim : Bool
  forbiddenTransition : Bool
  residualErasure : Bool
  evidenceRank : EpistemicRank
  hasRankGap : Bool
  hasMissingEvidence : Bool
  hasUnresolvedConflict : Bool
  evidenceSufficient : Bool
  deriving Repr

def resolvedByEvidence (r : Residual) (evidenceSufficient : Bool) : Bool :=
  match r with
  | Residual.missingEvidence => evidenceSufficient
  | Residual.rankGap => evidenceSufficient
  | Residual.semanticDrift => false
  | Residual.reverseTraceGap => evidenceSufficient
  | Residual.governanceFailure => false
  | Residual.unresolvedConflict => false
  | Residual.residualErasure => false

def residualsBefore (s : GovernanceState) : ResidualSet :=
  fun r =>
    match r with
    | Residual.missingEvidence => s.hasMissingEvidence
    | Residual.rankGap => s.hasRankGap
    | Residual.semanticDrift => false
    | Residual.reverseTraceGap => !s.reverseTraceComplete
    | Residual.governanceFailure => !s.governanceGatePassed
    | Residual.unresolvedConflict => s.hasUnresolvedConflict
    | Residual.residualErasure => s.residualErasure

def residualsAfter (s : GovernanceState) : ResidualSet :=
  fun r => residualsBefore s r && !(resolvedByEvidence r s.evidenceSufficient)

def residualPreserved
    (before after : ResidualSet)
    (evidenceSufficient : Bool) : Prop :=
  ∀ r : Residual, before r = true → after r = true ∨ resolvedByEvidence r evidenceSufficient = true

theorem residual_persistence
    (before after : ResidualSet)
    (evidenceSufficient : Bool)
    (hPreserved : residualPreserved before after evidenceSufficient) :
    ∀ r : Residual,
      before r = true → after r = true ∨ resolvedByEvidence r evidenceSufficient = true := by
  intro r hBefore
  exact hPreserved r hBefore

theorem state_residual_persistence (s : GovernanceState) :
    residualPreserved (residualsBefore s) (residualsAfter s) s.evidenceSufficient := by
  intro r hBefore
  by_cases hResolved : resolvedByEvidence r s.evidenceSufficient = true
  · right
    exact hResolved
  · left
    unfold residualsAfter
    simp [hBefore, hResolved]

def certificateAllowed (s : GovernanceState) : Bool :=
  rankLeq certificateRequiredRank s.evidenceRank &&
    s.hasProofObject && s.governanceGatePassed && s.reverseTraceComplete && s.evidenceMatchesClaim &&
    (!s.forbiddenTransition) && (!s.residualErasure) && (!s.hasRankGap) && (!s.hasMissingEvidence) &&
    (!s.hasUnresolvedConflict)

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

theorem rank_gap_blocks_certificate
    (s : GovernanceState)
    (hRankGap : s.hasRankGap = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hRankGap] at hAllowed
  simp at hAllowed

theorem residual_erasure_blocks_certificate
    (s : GovernanceState)
    (hResidualErasure : s.residualErasure = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hResidualErasure] at hAllowed
  simp at hAllowed

theorem missing_evidence_blocks_certificate
    (s : GovernanceState)
    (hMissingEvidence : s.hasMissingEvidence = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hMissingEvidence] at hAllowed
  simp at hAllowed

theorem unresolved_conflict_blocks_certificate
    (s : GovernanceState)
    (hConflict : s.hasUnresolvedConflict = true) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  rw [hConflict] at hAllowed
  simp at hAllowed

