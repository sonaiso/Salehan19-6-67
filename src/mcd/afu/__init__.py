"""Arabic Fractal Understanding (AFU) layer.

Architectural law for this package:

* Theory is *carried* from day one as a Gate Registry + theory index,
  not executed as runtime modules. PR 1 contains contracts only — no
  registry, no stages, no runner, no API.
* Runtime, when later added, is a minimal seven-stage spine:

    PromptReality
      → PriorInformationFilter
      → Linker
      → UnderstandingJudgment
      → ObligationPlanner
      → AnswerPlan
      → ResponseAudit
      → LicensedResponse

* CERTIFICATE is allowed only for narrow, directly-tested claims.
  A global pipeline CERTIFICATE is forbidden by construction.

This module exposes only contract dataclasses. It must not import any
Layer-T theory module (mantuq/mafhum/qiyas/naskh/illah/manat/dal/…).
"""
from __future__ import annotations

AFU_SCHEMA_VERSION = "1.0.0"
AFU_CONTRACT_VERSION = "1.0.0"

__all__ = [
    "AFU_SCHEMA_VERSION",
    "AFU_CONTRACT_VERSION",
]
