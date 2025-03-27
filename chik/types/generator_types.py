from __future__ import annotations

from dataclasses import dataclass, field

from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class BlockGenerator(Streamable):
    program: SerializedProgram = field(default_factory=SerializedProgram.default)
    generator_refs: list[bytes] = field(default_factory=list)
