"""
Pay to conditions

In this puzzle program, the solution is ignored. The reveal of the puzzle
returns a fixed list of conditions. This roughly corresponds to OP_SECURETHEBAG
in bitcoin.

This is a pretty useless most of the time. But some (most?) solutions
require a delegated puzzle program, so in those cases, this is just what
the doctor ordered.
"""

from __future__ import annotations

from chik.types.blockchain_format.program import Program
from chik.wallet.puzzles.load_klvm import load_klvm_maybe_recompile

MOD = load_klvm_maybe_recompile("p2_conditions.clsp")


def puzzle_for_conditions(conditions) -> Program:
    return MOD.run([conditions])


def solution_for_conditions(conditions) -> Program:
    return Program.to([puzzle_for_conditions(conditions), 0])
