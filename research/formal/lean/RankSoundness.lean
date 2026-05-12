/-!
PR #75 rank soundness extension over the PR #74 certificate-gating core.
Scope: minimal machine-checkable formal extension only.
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

structure GovernanceState where
  recognizedInput : Bool
  hasProofObject : Bool
  governanceGatePassed : Bool
  reverseTraceComplete : Bool
  evidenceMatchesClaim : Bool
  forbiddenTransition : Bool
  residualErasure : Bool
  evidenceRank : EpistemicRank
  deriving Repr

def certificateRequiredRank : EpistemicRank :=
  requiredRank PublicJudgment.certificate

def certificateAllowed (s : GovernanceState) : Bool :=
  rankLeq certificateRequiredRank s.evidenceRank &&
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

theorem rank_soundness (s : GovernanceState) :
    publicJudgment s = PublicJudgment.certificate →
      rankLeq (requiredRank PublicJudgment.certificate) s.evidenceRank = true := by
  intro hCert
  have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
  unfold certificateAllowed at hAllowed
  simp [certificateRequiredRank] at hAllowed
  exact hAllowed.1

theorem rank_order_chain :
    rankLeq EpistemicRank.zero EpistemicRank.hypothesis = true ∧
      rankLeq EpistemicRank.hypothesis EpistemicRank.evidence = true ∧
      rankLeq EpistemicRank.evidence EpistemicRank.certified = true := by
  simp [rankLeq, rankValue]

theorem insufficient_rank_blocks_certificate
    (s : GovernanceState)
    (hInsufficient : rankLeq certificateRequiredRank s.evidenceRank = false) :
    publicJudgment s ≠ PublicJudgment.certificate := by
  intro hCert
  have hRank : rankLeq certificateRequiredRank s.evidenceRank = true := by
    have hAllowed : certificateAllowed s = true := no_illicit_certification s hCert
    unfold certificateAllowed at hAllowed
    simp at hAllowed
    exact hAllowed.1
  rw [hInsufficient] at hRank
  simp at hRank
