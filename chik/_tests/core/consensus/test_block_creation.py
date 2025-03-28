from __future__ import annotations

import pytest
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint32, uint64

from chik._tests.core.make_block_generator import make_block_generator
from chik.consensus.block_creation import compute_block_cost, compute_block_fee
from chik.consensus.condition_costs import ConditionCost
from chik.consensus.default_constants import DEFAULT_CONSTANTS
from chik.types.blockchain_format.coin import Coin


@pytest.mark.parametrize("add_amount", [[0], [1, 2, 3], []])
@pytest.mark.parametrize("rem_amount", [[0], [1, 2, 3], []])
def test_compute_block_fee(add_amount: list[int], rem_amount: list[int]) -> None:
    additions: list[Coin] = [Coin(bytes32.random(), bytes32.random(), uint64(amt)) for amt in add_amount]
    removals: list[Coin] = [Coin(bytes32.random(), bytes32.random(), uint64(amt)) for amt in rem_amount]

    # the fee is the left-overs from the removals (spent) coins after deducting
    # the newly created coins (additions)
    expected = sum(rem_amount) - sum(add_amount)

    if expected < 0:
        with pytest.raises(ValueError, match="does not fit into uint64"):
            compute_block_fee(additions, removals)
    else:
        assert compute_block_fee(additions, removals) == expected


def test_compute_block_cost(softfork_height: uint32) -> None:
    num_coins = 10
    generator = make_block_generator(num_coins)
    cost = int(compute_block_cost(generator, DEFAULT_CONSTANTS, softfork_height))

    coin_cost = ConditionCost.CREATE_COIN.value * num_coins
    agg_sig_cost = ConditionCost.AGG_SIG.value * num_coins

    cost -= coin_cost
    cost -= agg_sig_cost
    cost -= len(bytes(generator.program)) * DEFAULT_CONSTANTS.COST_PER_BYTE

    print(f"{cost=}")

    # the cost is a non-trivial combination of the KLVM cost of running the puzzles
    # and before the hard-fork, combined with the cost of running the generator ROM
    # Consensus requires these costs to be unchanged over time, so this test
    # ensures compatibility
    if softfork_height >= DEFAULT_CONSTANTS.HARD_FORK_HEIGHT:
        expected = 180980
    else:
        expected = 3936699

    assert cost == expected
