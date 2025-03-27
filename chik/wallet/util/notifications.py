from __future__ import annotations

from chik_puzzles_py.programs import NOTIFICATION
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint64

from chik.types.blockchain_format.program import Program

NOTIFICATION_MOD = Program.from_bytes(NOTIFICATION)


def construct_notification(target: bytes32, amount: uint64) -> Program:
    return NOTIFICATION_MOD.curry(target, amount)
