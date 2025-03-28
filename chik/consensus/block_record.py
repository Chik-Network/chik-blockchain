from __future__ import annotations

from typing import Optional

import chik_rs
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint32, uint64
from typing_extensions import Protocol

BlockRecord = chik_rs.BlockRecord


class BlockRecordProtocol(Protocol):
    @property
    def header_hash(self) -> bytes32: ...

    @property
    def height(self) -> uint32: ...

    @property
    def timestamp(self) -> Optional[uint64]: ...

    @property
    def prev_transaction_block_height(self) -> uint32: ...

    @property
    def prev_transaction_block_hash(self) -> Optional[bytes32]: ...

    @property
    def is_transaction_block(self) -> bool: ...
