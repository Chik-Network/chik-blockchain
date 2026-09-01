from __future__ import annotations

from dataclasses import dataclass

from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class RemoteInfo(Streamable):
    pass
