from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from chik.server.ws_connection import WSChikConnection
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.mempool_inclusion_status import MempoolInclusionStatus
from chik.types.spend_bundle import SpendBundle
from chik.util.errors import Err
from chik.util.misc import ValuedEvent


@dataclass(frozen=True)
class TransactionQueueEntry:
    """
    A transaction received from peer. This is put into a queue, and not yet in the mempool.
    """

    transaction: SpendBundle = field(compare=False)
    transaction_bytes: Optional[bytes] = field(compare=False)
    spend_name: bytes32
    peer: Optional[WSChikConnection] = field(compare=False)
    test: bool = field(compare=False)
    done: ValuedEvent[Tuple[MempoolInclusionStatus, Optional[Err]]] = field(
        default_factory=ValuedEvent,
        compare=False,
    )
