from __future__ import annotations

from typing import Optional

from typing_extensions import Protocol

from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.ints import uint32


class BlockInfo(Protocol):
    @property
    def prev_header_hash(self) -> bytes32: ...

    @property
    def transactions_generator(self) -> Optional[SerializedProgram]: ...

    @property
    def transactions_generator_ref_list(self) -> list[uint32]: ...
