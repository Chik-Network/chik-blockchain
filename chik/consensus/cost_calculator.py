from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chik_rs import SpendBundleConditions
from chik_rs.sized_ints import uint16

from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class NPCResult(Streamable):
    error: Optional[uint16]
    conds: Optional[SpendBundleConditions]
