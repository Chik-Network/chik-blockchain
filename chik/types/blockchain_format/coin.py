from __future__ import annotations

from typing import Union

from chik_rs import Coin

from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.hash import std_hash
from chik.util.ints import uint64

__all__ = ["Coin", "coin_as_list", "hash_coin_ids"]


def coin_as_list(c: Coin) -> list[Union[bytes32, uint64]]:
    return [c.parent_coin_info, c.puzzle_hash, uint64(c.amount)]


def hash_coin_ids(coin_ids: list[bytes32]) -> bytes32:
    if len(coin_ids) == 1:
        return std_hash(coin_ids[0])

    coin_ids.sort(reverse=True)
    buffer = bytearray()

    for name in coin_ids:
        buffer.extend(name)

    return std_hash(buffer, skip_bytes_conversion=True)
