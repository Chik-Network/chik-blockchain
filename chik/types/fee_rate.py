from __future__ import annotations

import math
from dataclasses import dataclass

import typing_extensions
from chik_rs.sized_ints import uint64

from chik.types.klvm_cost import KLVMCost
from chik.types.mojos import Mojos
from chik.util.streamable import Streamable, streamable


@typing_extensions.final
@streamable
@dataclass(frozen=True)
class FeeRate(Streamable):
    """
    Represents Fee Rate in mojos divided by KLVM Cost.
    Performs XCK/mojo conversion.
    Similar to 'Fee per cost'.
    """

    mojos_per_klvm_cost: uint64

    @classmethod
    def create(cls, mojos: Mojos, klvm_cost: KLVMCost) -> FeeRate:
        return cls(uint64(math.ceil(mojos / klvm_cost)))


@dataclass(frozen=True)
class FeeRateV2:
    """
    Represents Fee Rate in mojos divided by KLVM Cost.
    Similar to 'Fee per cost'.
    """

    mojos_per_klvm_cost: float
