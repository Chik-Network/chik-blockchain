from __future__ import annotations

from dataclasses import dataclass

from chik.types.blockchain_format.program import Program, uncurry
from chik.types.blockchain_format.serialized_program import SerializedProgram


@dataclass(frozen=True)
class UncurriedPuzzle:
    mod: Program
    args: Program


def uncurry_puzzle(puzzle: Program | SerializedProgram) -> UncurriedPuzzle:
    return UncurriedPuzzle(*uncurry(puzzle))
