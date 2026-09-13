from __future__ import annotations

from dataclasses import dataclass

from chik.types.condition_opcodes import ConditionOpcode


@dataclass(frozen=True)
class ConditionWithArgs:
    """
    This structure is used to store parsed CLVK conditions
    Conditions in CLVK have either format of (opcode, var1) or (opcode, var1, var2)
    """

    opcode: ConditionOpcode
    vars: list[bytes]
