from __future__ import annotations

from typing import NewType

from chik_rs.sized_ints import uint64

"""
KLVM Cost is the cost to run a KLVM program on the KLVM.
It is similar to transaction bytes in the Bitcoin, but some operations
are charged a higher rate, depending on their arguments.
"""

KLVMCost = NewType("KLVMCost", uint64)
