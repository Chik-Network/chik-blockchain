from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.ints import uint32
from chik.util.streamable import Streamable, streamable
from chik.wallet.notification_store import Notification


@streamable
@dataclass(frozen=True)
class GetNotifications(Streamable):
    ids: Optional[List[bytes32]] = None
    start: Optional[uint32] = None
    end: Optional[uint32] = None


@streamable
@dataclass(frozen=True)
class GetNotificationsResponse(Streamable):
    notifications: List[Notification]
