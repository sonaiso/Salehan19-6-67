/-!
PR #75 typed residual ontology.
Scope: machine-checkable residual typing foundation only.
-/

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

def resolvedByEvidence (r : Residual) (evidenceSufficient : Bool) : Bool :=
  match r with
  | Residual.missingEvidence => evidenceSufficient
  | Residual.rankGap => evidenceSufficient
  | Residual.semanticDrift => false
  | Residual.reverseTraceGap => evidenceSufficient
  | Residual.governanceFailure => false
  | Residual.unresolvedConflict => false
  | Residual.residualErasure => false

def residualPreserved
    (before after : ResidualSet)
    (evidenceSufficient : Bool) : Prop :=
  ∀ r : Residual, before r = true → after r = true ∨ resolvedByEvidence r evidenceSufficient = true

theorem residual_erasure_never_resolved_by_evidence (evidenceSufficient : Bool) :
    resolvedByEvidence Residual.residualErasure evidenceSufficient = false := by
  simp [resolvedByEvidence]

theorem unresolved_conflict_never_resolved_by_evidence (evidenceSufficient : Bool) :
    resolvedByEvidence Residual.unresolvedConflict evidenceSufficient = false := by
  simp [resolvedByEvidence]

