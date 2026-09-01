from __future__ import annotations

from dataclasses import dataclass

from chik_rs import PartialProof
from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint8

from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class SolverInfo(Streamable):
    partial_proof: PartialProof
    plot_id: bytes32
    strength: uint8
    size: uint8  # k-size


@streamable
@dataclass(frozen=True)
class SolverResponse(Streamable):
    partial_proof: PartialProof
    proof: bytes
