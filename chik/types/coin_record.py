from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chik_rs import CoinState
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint32, uint64

from chik.types.blockchain_format.coin import Coin
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class CoinRecord(Streamable):
    """
    These are values that correspond to a CoinName that are used
    in keeping track of the unspent database.
    """

    coin: Coin
    confirmed_block_index: uint32
    spent_block_index: uint32
    coinbase: bool
    timestamp: uint64  # Timestamp of the block at height confirmed_block_index

    @property
    def spent(self) -> bool:
        return self.spent_block_index > 0

    @property
    def name(self) -> bytes32:
        return self.coin.name()

    @property
    def coin_state(self) -> CoinState:
        spent_h = None
        if self.spent:
            spent_h = self.spent_block_index
        confirmed_height: Optional[uint32] = self.confirmed_block_index
        if self.confirmed_block_index == 0 and self.timestamp == 0:
            confirmed_height = None
        return CoinState(self.coin, spent_h, confirmed_height)
