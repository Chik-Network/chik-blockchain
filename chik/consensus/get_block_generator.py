from __future__ import annotations

from collections.abc import Awaitable, Callable

from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint32

from chik.consensus.block_generator_info import get_transactions_generator_program
from chik.types.block_protocol import BlockInfo
from chik.types.generator_types import BlockGenerator


async def get_block_generator(
    lookup_block_generators: Callable[[bytes32, set[uint32]], Awaitable[dict[uint32, bytes]]],
    block: BlockInfo,
) -> BlockGenerator | None:
    ref_list = block.transactions_generator_ref_list
    program = get_transactions_generator_program(block)
    if program is None:
        assert len(ref_list) == 0
        return None
    if len(ref_list) == 0:
        return BlockGenerator(program, [])

    generator_refs = set(ref_list)
    generators: dict[uint32, bytes] = await lookup_block_generators(block.prev_header_hash, generator_refs)

    result = [generators[height] for height in block.transactions_generator_ref_list]
    return BlockGenerator(program, result)
