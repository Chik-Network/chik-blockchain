from __future__ import annotations

import pkg_resources
from klvm.casts import int_from_bytes

from chik.types.condition_opcodes import ConditionOpcode


def test_condition_codes_is_complete() -> None:
    with open(pkg_resources.resource_filename("chik.wallet.puzzles", "condition_codes.clib")) as f:
        contents: str = f.read()
        for name, value in ConditionOpcode.__members__.items():
            assert f"(defconstant {name} {int_from_bytes(value)})" in contents
