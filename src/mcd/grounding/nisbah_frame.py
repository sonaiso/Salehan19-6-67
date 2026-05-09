"""NisbahFrame — relational semantic frames derived from RoleFrames."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from mcd.grounding.role_frame import RoleFrame


class NisbahType(str, Enum):
    ISNAD = "isnad"
    TAQYID = "taqyid"
    TADAMMUN = "tadammun"
    SABABIYYAH = "sababiyyah"
    MUSABBABIYYAH = "musabbabiyyah"
    FAILIYYAH = "fa'iliyyah"
    MAFULIYYAH = "maf'uliyyah"
    GHAYAH = "ghayah"
    SHARTIYYAH = "shartiyyah"
    ADATIYYAH = "adatiyyah"
    AGENT_OF = "agent_of"
    PATIENT_OF = "patient_of"
    INSTRUMENT_OF = "instrument_of"
    PLACE_OF = "place_of"
    TIME_OF = "time_of"
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    RESTRICTS = "restricts"
    ENTAILS = "entails"
    INCLUDES = "includes"
    PREDICATES = "predicates"
    QUALIFIES = "qualifies"
    CONDITIONS = "conditions"
    AIMS_AT = "aims_at"


@dataclass
class NisbahFrame:
    nisbah_id: str
    source: str
    relation_type: NisbahType
    target: str
    qualifier: str = ""
    evidence: list = field(default_factory=list)
    certainty: float = 0.5


class NisbahFrameBuilder:
    """Extract NisbahFrames from a RoleFrame."""

    def build(self, role_frame: RoleFrame) -> list[NisbahFrame]:
        frames: list[NisbahFrame] = []
        action = role_frame.action or role_frame.event or "فعل"

        def _make(source: str, rel: NisbahType, target: str) -> NisbahFrame:
            return NisbahFrame(
                nisbah_id=str(uuid.uuid4())[:8],
                source=source,
                relation_type=rel,
                target=target,
                certainty=role_frame.certainty,
            )

        if role_frame.agent:
            frames.append(_make(role_frame.agent, NisbahType.AGENT_OF, action))

        if role_frame.patient:
            frames.append(_make(role_frame.patient, NisbahType.PATIENT_OF, action))

        if role_frame.instrument:
            frames.append(_make(role_frame.instrument, NisbahType.INSTRUMENT_OF, action))

        if role_frame.place:
            frames.append(_make(role_frame.place, NisbahType.PLACE_OF, action))

        if role_frame.time:
            frames.append(_make(role_frame.time, NisbahType.TIME_OF, action))

        if role_frame.cause:
            frames.append(_make(role_frame.cause, NisbahType.CAUSES, action))

        if role_frame.purpose:
            frames.append(_make(action, NisbahType.AIMS_AT, role_frame.purpose))

        return frames
