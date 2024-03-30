from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from chik.consensus.cost_calculator import NPCResult
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.mempool_item import BundleCoinSpend
from chik.types.spend_bundle import SpendBundle
from chik.util.ints import uint32


@dataclass
class InternalMempoolItem:
    spend_bundle: SpendBundle
    npc_result: NPCResult
    height_added_to_mempool: uint32
    # Map of coin ID to coin spend data between the bundle and its NPCResult
    bundle_coin_spends: Dict[bytes32, BundleCoinSpend]
