from __future__ import annotations

import builtins
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

from chik_rs import SpendBundle
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint8, uint32, uint64

from chik.consensus.coinbase import farmer_parent_id, pool_parent_id
from chik.types.blockchain_format.coin import Coin
from chik.types.mempool_inclusion_status import MempoolInclusionStatus
from chik.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chik.util.errors import Err
from chik.util.streamable import Streamable, streamable
from chik.wallet.conditions import ConditionValidTimes
from chik.wallet.util.transaction_type import TransactionType
from chik.wallet.wallet_spend_bundle import WalletSpendBundle

T = TypeVar("T")
_T_TransactionRecord = TypeVar("_T_TransactionRecord", bound="TransactionRecordOld")

minimum_send_attempts = 6


@dataclass
class ItemAndTransactionRecords(Generic[T]):
    item: T
    transaction_records: list[TransactionRecord]


@streamable
@dataclass(frozen=True)
class TransactionRecordOld(Streamable):
    """
    Used for storing transaction data and status in wallets.
    """

    confirmed_at_height: uint32
    created_at_time: uint64
    to_puzzle_hash: bytes32
    amount: uint64
    fee_amount: uint64
    confirmed: bool
    sent: uint32
    spend_bundle: Optional[WalletSpendBundle]
    additions: list[Coin]
    removals: list[Coin]
    wallet_id: uint32

    # Represents the list of peers that we sent the transaction to, whether each one
    # included it in the mempool, and what the error message (if any) was
    sent_to: list[tuple[str, uint8, Optional[str]]]
    trade_id: Optional[bytes32]
    type: uint32  # TransactionType

    # name is also called bundle_id and tx_id
    name: bytes32
    memos: list[tuple[bytes32, list[bytes]]]

    def is_in_mempool(self) -> bool:
        # If one of the nodes we sent it to responded with success or pending, we return True
        for _, mis, _ in self.sent_to:
            if MempoolInclusionStatus(mis) in {MempoolInclusionStatus.SUCCESS, MempoolInclusionStatus.PENDING}:
                return True
        return False

    def height_farmed(self, genesis_challenge: bytes32) -> Optional[uint32]:
        if not self.confirmed:
            return None
        if self.type in {TransactionType.FEE_REWARD, TransactionType.COINBASE_REWARD}:
            for block_index in range(self.confirmed_at_height, self.confirmed_at_height - 100, -1):
                if block_index < 0:
                    return None
                pool_parent = pool_parent_id(uint32(block_index), genesis_challenge)
                farmer_parent = farmer_parent_id(uint32(block_index), genesis_challenge)
                if pool_parent == self.additions[0].parent_coin_info:
                    return uint32(block_index)
                if farmer_parent == self.additions[0].parent_coin_info:
                    return uint32(block_index)
        return None

    def get_memos(self) -> dict[bytes32, list[bytes]]:
        return {coin_id: ms for coin_id, ms in self.memos}

    @classmethod
    def from_json_dict_convenience(
        cls: builtins.type[_T_TransactionRecord], modified_tx_input: dict
    ) -> _T_TransactionRecord:
        modified_tx = modified_tx_input.copy()
        if "to_address" in modified_tx:
            modified_tx["to_puzzle_hash"] = decode_puzzle_hash(modified_tx["to_address"]).hex()
        if "to_address" in modified_tx:
            del modified_tx["to_address"]
        # Converts memos from a flat dict into a nested list
        memos_dict: dict[str, list[str]] = {}
        memos_list: list = []
        if "memos" in modified_tx:
            for coin_id, memo in modified_tx["memos"].items():
                if coin_id not in memos_dict:
                    memos_dict[coin_id] = []
                memos_dict[coin_id].append(memo)
        for coin_id, memos in memos_dict.items():
            memos_list.append((coin_id, memos))
        modified_tx["memos"] = memos_list
        return cls.from_json_dict(modified_tx)

    @classmethod
    def from_json_dict(cls: builtins.type[_T_TransactionRecord], json_dict: dict[str, Any]) -> _T_TransactionRecord:
        try:
            return super().from_json_dict(json_dict)
        except Exception:
            return cls.from_json_dict_convenience(json_dict)

    def to_json_dict_convenience(self, config: dict) -> dict:
        selected = config["selected_network"]
        prefix = config["network_overrides"]["config"][selected]["address_prefix"]
        formatted = self.to_json_dict()
        formatted["to_address"] = encode_puzzle_hash(self.to_puzzle_hash, prefix)
        formatted["memos"] = {
            coin_id.hex(): memo.hex()
            for coin_id, memos in self.get_memos().items()
            for memo in memos
            if memo is not None
        }
        return formatted

    def is_valid(self) -> bool:
        if len(self.sent_to) < minimum_send_attempts:
            # we haven't tried enough peers yet
            return True
        if any(x[1] == MempoolInclusionStatus.SUCCESS for x in self.sent_to):
            # we managed to push it to mempool at least once
            return True
        if any(x[2] in {Err.INVALID_FEE_LOW_FEE.name, Err.INVALID_FEE_TOO_CLOSE_TO_ZERO.name} for x in self.sent_to):
            # we tried to push it to mempool and got a fee error so it's a temporary error
            return True
        return False

    def hint_dict(self) -> dict[bytes32, bytes32]:
        return {coin_id: bytes32(memos[0]) for coin_id, memos in self.memos if len(memos) > 0 and len(memos[0]) == 32}


@streamable
@dataclass(frozen=True)
class TransactionRecord(TransactionRecordOld):
    valid_times: ConditionValidTimes


@streamable
@dataclass(frozen=True)
class LightTransactionRecord(Streamable):
    name: bytes32
    type: uint32
    additions: list[Coin]
    removals: list[Coin]
    spend_bundle: Optional[SpendBundle]
