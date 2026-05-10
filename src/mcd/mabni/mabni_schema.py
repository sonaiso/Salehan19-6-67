"""Phase 7.4 — Arabic Mabni Logical-Pragmatic Control Layer: Core Enums."""
from __future__ import annotations

from enum import Enum


class MabniType(str, Enum):
    pronoun = "pronoun"
    demonstrative = "demonstrative"
    relative = "relative"
    particle = "particle"
    preposition = "preposition"
    conditional = "conditional"
    negation = "negation"
    answer = "answer"
    exception = "exception"
    restriction = "restriction"
    emphasis = "emphasis"
    interrogative = "interrogative"
    vocative = "vocative"
    imperative_marker = "imperative_marker"
    prohibition_marker = "prohibition_marker"


class LogicalFunction(str, Enum):
    reference = "reference"
    scope = "scope"
    condition = "condition"
    negation = "negation"
    answer = "answer"
    speech_act = "speech_act"
    emphasis = "emphasis"
    restriction = "restriction"
    exception = "exception"
    qasr = "qasr"
    relation = "relation"
    suspension = "suspension"


class PragmaticFunction(str, Enum):
    question = "question"
    assertion = "assertion"
    command = "command"
    prohibition = "prohibition"
    wish = "wish"
    hope = "hope"
    warning = "warning"
    confirmation = "confirmation"
    denial = "denial"
    response = "response"
    topic_shift = "topic_shift"


class CertaintyEffect(str, Enum):
    none = "none"
    lower = "lower"
    suspend = "suspend"
    scope_limit = "scope_limit"
    emphasis_only = "emphasis_only"
    requires_external_evidence = "requires_external_evidence"
