from __future__ import annotations

from dataclasses import dataclass

from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.mempool_item import BundleCoinSpend
from chik.types.spend_bundle import SpendBundle
from chik.types.spend_bundle_conditions import SpendBundleConditions
from chik.util.ints import uint32


@dataclass(frozen=True)
class InternalMempoolItem:
    spend_bundle: SpendBundle
    conds: SpendBundleConditions
    height_added_to_mempool: uint32
    # Map of coin ID to coin spend data between the bundle and its NPCResult
    bundle_coin_spends: dict[bytes32, BundleCoinSpend]
