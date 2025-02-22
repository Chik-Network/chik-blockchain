from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from chik.types.blockchain_format.foliage import Foliage, FoliageTransactionBlock
from chik.types.blockchain_format.reward_chain_block import RewardChainBlockUnfinished
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.blockchain_format.vdf import VDFProof
from chik.types.end_of_slot_bundle import EndOfSubSlotBundle
from chik.util.ints import uint128
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class UnfinishedHeaderBlock(Streamable):
    # Same as a FullBlock but without TransactionInfo and Generator, used by light clients
    finished_sub_slots: list[EndOfSubSlotBundle]  # If first sb
    reward_chain_block: RewardChainBlockUnfinished  # Reward chain trunk data
    challenge_chain_sp_proof: Optional[VDFProof]  # If not first sp in sub-slot
    reward_chain_sp_proof: Optional[VDFProof]  # If not first sp in sub-slot
    foliage: Foliage  # Reward chain foliage data
    foliage_transaction_block: Optional[FoliageTransactionBlock]  # Reward chain foliage data (tx block)
    transactions_filter: bytes  # Filter for block transactions

    @property
    def prev_header_hash(self) -> bytes32:
        return self.foliage.prev_block_hash

    @property
    def header_hash(self) -> bytes32:
        return self.foliage.get_hash()

    @property
    def total_iters(self) -> uint128:
        return self.reward_chain_block.total_iters
