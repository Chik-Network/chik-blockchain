from __future__ import annotations

import asyncio

from chik_rs import G2Element
from klvm_tools import binutils

from chik.consensus.block_rewards import calculate_base_farmer_reward, calculate_pool_reward
from chik.rpc.full_node_rpc_client import FullNodeRpcClient
from chik.types.blockchain_format.program import Program
from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.types.coin_spend import CoinSpend
from chik.types.condition_opcodes import ConditionOpcode
from chik.types.spend_bundle import SpendBundle
from chik.util.bech32m import decode_puzzle_hash
from chik.util.condition_tools import parse_sexp_to_conditions
from chik.util.config import load_config
from chik.util.default_root import DEFAULT_ROOT_PATH
from chik.util.ints import uint16, uint32


def print_conditions(spend_bundle: SpendBundle) -> None:
    print("\nConditions:")
    for coin_spend in spend_bundle.coin_spends:
        result = Program.from_bytes(bytes(coin_spend.puzzle_reveal)).run(Program.from_bytes(bytes(coin_spend.solution)))
        for cvp in parse_sexp_to_conditions(result):
            print(f"{ConditionOpcode(cvp.opcode).name}: {[var.hex() for var in cvp.vars]}")
    print("")


async def main() -> None:
    rpc_port: uint16 = uint16(9789)
    self_hostname = "localhost"
    path = DEFAULT_ROOT_PATH
    config = load_config(path, "config.yaml")
    client = await FullNodeRpcClient.create(self_hostname, rpc_port, path, config)
    try:
        block_record = await client.get_block_record_by_height(1)
        assert block_record is not None
        assert block_record.reward_claims_incorporated is not None
        farmer_prefarm = block_record.reward_claims_incorporated[1]
        pool_prefarm = block_record.reward_claims_incorporated[0]

        pool_amounts = int(calculate_pool_reward(uint32(0)) / 2)
        farmer_amounts = int(calculate_base_farmer_reward(uint32(0)) / 2)
        print(farmer_prefarm.amount, farmer_amounts)
        assert farmer_amounts == farmer_prefarm.amount // 2
        assert pool_amounts == pool_prefarm.amount // 2
        address1 = "xck1rdatypul5c642jkeh4yp933zu3hw8vv8tfup8ta6zfampnyhjnusws3u73"  # Key 1
        address2 = "xck1duvy5ur5eyj7lp5geetfg84cj2d7xgpxt7pya3lr2y6ke3696w9qysy45j"  # Key 2

        ph1 = decode_puzzle_hash(address1)
        ph2 = decode_puzzle_hash(address2)

        p_farmer_2 = SerializedProgram.to(
            binutils.assemble(f"(q . ((51 0x{ph1.hex()} {farmer_amounts}) " f"(51 0x{ph2.hex()} {farmer_amounts})))")
        )
        p_pool_2 = SerializedProgram.to(
            binutils.assemble(f"(q . ((51 0x{ph1.hex()} {pool_amounts}) " f"(51 0x{ph2.hex()} {pool_amounts})))")
        )

        print(f"Ph1: {ph1.hex()}")
        print(f"Ph2: {ph2.hex()}")
        assert ph1.hex() == "1b7ab2079fa635554ad9bd4812c622e46ee3b1875a7813afba127bb0cc9794f9"
        assert ph2.hex() == "6f184a7074c925ef8688ce56941eb8929be320265f824ec7e351356cc745d38a"

        p_solution = SerializedProgram.to(binutils.assemble("()"))

        sb_farmer = SpendBundle([CoinSpend(farmer_prefarm, p_farmer_2, p_solution)], G2Element())
        sb_pool = SpendBundle([CoinSpend(pool_prefarm, p_pool_2, p_solution)], G2Element())

        print("\n\n\nConditions")
        print_conditions(sb_pool)
        print("\n\n\n")
        print("Farmer to spend")
        print(sb_pool)
        print(sb_farmer)
        print("\n\n\n")
        # res = await client.push_tx(sb_farmer)
        # res = await client.push_tx(sb_pool)

        # print(res)
        up = await client.get_coin_records_by_puzzle_hash(farmer_prefarm.puzzle_hash, True)
        uf = await client.get_coin_records_by_puzzle_hash(pool_prefarm.puzzle_hash, True)
        print(up)
        print(uf)
    finally:
        client.close()


asyncio.run(main())
