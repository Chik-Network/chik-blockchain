from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chik.types.blockchain_format.coin import Coin
from chik.types.blockchain_format.program import Program
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.ints import uint64
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class LockedCoinInfo(Streamable):
    coin: Coin
    inner_puzzle: Program  # This is the lockup puzzle, not the lockup_puzzle's inner_puzzle
    active_votes: list[Optional[bytes32]]


@streamable
@dataclass(frozen=True)
class DAOCATInfo(Streamable):
    dao_wallet_id: uint64
    free_cat_wallet_id: uint64
    limitations_program_hash: bytes32
    my_tail: Optional[Program]  # this is the program
    locked_coins: list[LockedCoinInfo]
