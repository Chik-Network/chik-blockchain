from __future__ import annotations

from typing import Collection, List, Optional, Tuple

from chikbip158 import PyBIP158

from chik.types.blockchain_format.coin import Coin
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.full_block import FullBlock
from chik.types.header_block import HeaderBlock
from chik.types.spend_bundle_conditions import SpendBundleConditions
from chik.util.ints import uint64


def get_block_header(
    block: FullBlock, tx_addition_coins: Collection[Coin], removals_names: Collection[bytes32]
) -> HeaderBlock:
    # Create filter
    byte_array_tx: List[bytearray] = []
    if block.is_transaction_block():
        for coin in tx_addition_coins:
            byte_array_tx.append(bytearray(coin.puzzle_hash))
        for coin in block.get_included_reward_coins():
            byte_array_tx.append(bytearray(coin.puzzle_hash))
        for name in removals_names:
            byte_array_tx.append(bytearray(name))

    bip158: PyBIP158 = PyBIP158(byte_array_tx)
    encoded_filter: bytes = bytes(bip158.GetEncoded())

    return HeaderBlock(
        block.finished_sub_slots,
        block.reward_chain_block,
        block.challenge_chain_sp_proof,
        block.challenge_chain_ip_proof,
        block.reward_chain_sp_proof,
        block.reward_chain_ip_proof,
        block.infused_challenge_chain_ip_proof,
        block.foliage,
        block.foliage_transaction_block,
        encoded_filter,
        block.transactions_info,
    )


def tx_removals_and_additions(results: Optional[SpendBundleConditions]) -> Tuple[List[bytes32], List[Coin]]:
    """
    Doesn't return farmer and pool reward.
    """

    removals: List[bytes32] = []
    additions: List[Coin] = []

    # build removals list
    if results is None:
        return [], []
    for spend in results.spends:
        removals.append(bytes32(spend.coin_id))
        for puzzle_hash, amount, _ in spend.create_coin:
            additions.append(Coin(bytes32(spend.coin_id), bytes32(puzzle_hash), uint64(amount)))

    return removals, additions
