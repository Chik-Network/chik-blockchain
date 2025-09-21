from __future__ import annotations

from dataclasses import dataclass

from chik_rs import SpendBundle, SpendBundleConditions
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint32

from chik.types.mempool_item import BundleCoinSpend


@dataclass(frozen=True)
class InternalMempoolItem:
    spend_bundle: SpendBundle
    conds: SpendBundleConditions
    height_added_to_mempool: uint32
    # Map of coin ID to coin spend data between the bundle and its NPCResult
    bundle_coin_spends: dict[bytes32, BundleCoinSpend]
