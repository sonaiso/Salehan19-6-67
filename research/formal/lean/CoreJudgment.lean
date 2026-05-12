/-!
PR #74 minimal machine-checkable core.

Scope:
- Public judgment triad
- Certificate gating model
- No full-project proof claim
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
