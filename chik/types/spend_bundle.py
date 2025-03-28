from __future__ import annotations

from typing import TypeVar

import chik_rs

from chik.consensus.default_constants import DEFAULT_CONSTANTS
from chik.types.coin_spend import compute_additions_with_cost
from chik.util.errors import Err, ValidationError

SpendBundle = chik_rs.SpendBundle
T_SpendBundle = TypeVar("T_SpendBundle", bound="SpendBundle")


# This function executes all the puzzles to compute the difference between
# additions and removals
def estimate_fees(spend_bundle: SpendBundle) -> int:
    """Unsafe to use for fees validation!!!"""
    removed_amount = 0
    added_amount = 0
    max_cost = int(DEFAULT_CONSTANTS.MAX_BLOCK_COST_KLVM)
    for cs in spend_bundle.coin_spends:
        removed_amount += cs.coin.amount
        coins, cost = compute_additions_with_cost(cs, max_cost=max_cost)
        max_cost -= cost
        if max_cost < 0:
            raise ValidationError(Err.BLOCK_COST_EXCEEDS_MAX, "estimate_fees() for SpendBundle")
        for c in coins:
            added_amount += c.amount
    return removed_amount - added_amount
