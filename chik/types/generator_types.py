from __future__ import annotations

from dataclasses import dataclass
from typing import List

from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class BlockGenerator(Streamable):
    program: SerializedProgram
    generator_refs: List[bytes]
