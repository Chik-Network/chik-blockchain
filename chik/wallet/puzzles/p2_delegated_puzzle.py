"""
Pay to delegated puzzle

In this puzzle program, the solution must be a signed delegated puzzle, along with
its (unsigned) solution. The delegated puzzle is executed, passing in the solution.
This obviously could be done recursively, arbitrarily deep (as long as the maximum
cost is not exceeded).

If you want to specify the conditions directly (thus terminating the potential recursion),
you can use p2_conditions.

This roughly corresponds to bitcoin's graftroot.
"""

from __future__ import annotations

from chik_puzzles_py.programs import P2_DELEGATED_PUZZLE

from chik.types.blockchain_format.program import Program
from chik.wallet.puzzles import p2_conditions

MOD = Program.from_bytes(P2_DELEGATED_PUZZLE)


def puzzle_for_pk(public_key: bytes) -> Program:
    return MOD.curry(public_key)


def solution_for_conditions(conditions) -> Program:
    delegated_puzzle = p2_conditions.puzzle_for_conditions(conditions)
    return solution_for_delegated_puzzle(delegated_puzzle, Program.to(0))


def solution_for_delegated_puzzle(delegated_puzzle: Program, delegated_solution: Program) -> Program:
    return delegated_puzzle.to([delegated_puzzle, delegated_solution])
