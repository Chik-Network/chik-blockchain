from __future__ import annotations

from typing import NewType

from chik_rs.sized_ints import uint64

"""
CLVK Cost is the cost to run a CLVK program on the CLVK.
It is similar to transaction bytes in the Bitcoin, but some operations
are charged a higher rate, depending on their arguments.
"""

CLVKCost = NewType("CLVKCost", uint64)

# For block overhead cost calculation
QUOTE_BYTES = 2
QUOTE_EXECUTION_COST = 20
