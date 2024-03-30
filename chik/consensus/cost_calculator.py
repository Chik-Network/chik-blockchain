from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chik.types.spend_bundle_conditions import SpendBundleConditions
from chik.util.ints import uint16
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class NPCResult(Streamable):
    error: Optional[uint16]
    conds: Optional[SpendBundleConditions]
