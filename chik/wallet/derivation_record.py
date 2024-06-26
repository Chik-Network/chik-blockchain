from __future__ import annotations

from dataclasses import dataclass

from chik_rs import G1Element

from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.ints import uint32
from chik.wallet.util.wallet_types import WalletType


@dataclass(frozen=True)
class DerivationRecord:
    """
    These are records representing a puzzle hash, which is generated from a
    public key, derivation index, and wallet type. Stored in the puzzle_store.
    """

    index: uint32
    puzzle_hash: bytes32
    pubkey: G1Element
    wallet_type: WalletType
    wallet_id: uint32
    hardened: bool
