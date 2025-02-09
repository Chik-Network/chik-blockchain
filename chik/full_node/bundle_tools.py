from __future__ import annotations

from chik_rs import solution_generator, solution_generator_backrefs

from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.types.generator_types import BlockGenerator
from chik.types.spend_bundle import SpendBundle


def simple_solution_generator(bundle: SpendBundle) -> BlockGenerator:
    spends = [(cs.coin, bytes(cs.puzzle_reveal), bytes(cs.solution)) for cs in bundle.coin_spends]
    block_program = solution_generator(spends)
    return BlockGenerator(SerializedProgram.from_bytes(block_program), [])


def simple_solution_generator_backrefs(bundle: SpendBundle) -> BlockGenerator:
    spends = [(cs.coin, bytes(cs.puzzle_reveal), bytes(cs.solution)) for cs in bundle.coin_spends]
    block_program = solution_generator_backrefs(spends)
    return BlockGenerator(SerializedProgram.from_bytes(block_program), [])
