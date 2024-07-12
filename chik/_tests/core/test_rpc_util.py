from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest

from chik.rpc.util import marshal
from chik.util.ints import uint32
from chik.util.streamable import Streamable, streamable
from chik.wallet.util.klvm_streamable import klvm_streamable


@streamable
@dataclass(frozen=True)
class SubObject(Streamable):
    qux: str


@streamable
@dataclass(frozen=True)
class TestRequestType(Streamable):
    foofoo: str
    barbar: uint32
    bat: bytes
    bam: SubObject


@streamable
@dataclass(frozen=True)
class TestResponseObject(Streamable):
    qat: List[str]
    sub: SubObject


@pytest.mark.anyio
async def test_rpc_marshalling() -> None:
    @marshal
    async def test_rpc_endpoint(self: None, request: TestRequestType) -> TestResponseObject:
        return TestResponseObject(
            [request.foofoo, str(request.barbar), request.bat.hex(), request.bam.qux], request.bam
        )

    assert await test_rpc_endpoint(
        None,
        {
            "foofoo": "foofoo",
            "barbar": 1,
            "bat": b"\xff",
            "bam": {
                "qux": "qux",
            },
        },
    ) == {"qat": ["foofoo", "1", "ff", "qux"], "sub": {"qux": "qux"}}


@klvm_streamable
@dataclass(frozen=True)
class KlvmSubObject(Streamable):
    qux: bytes


@streamable
@dataclass(frozen=True)
class TestKlvmRequestType(Streamable):
    sub: KlvmSubObject


@streamable
@dataclass(frozen=True)
class TestKlvmResponseObject(Streamable):
    sub: KlvmSubObject


@pytest.mark.anyio
async def test_klvm_streamable_marshalling() -> None:
    @marshal
    async def test_rpc_endpoint(self: None, request: TestKlvmRequestType) -> TestKlvmResponseObject:
        return TestKlvmResponseObject(request.sub)

    assert await test_rpc_endpoint(
        None,
        {
            "sub": "ff81ff80",
            "CHIP-0029": True,
        },
    ) == {"sub": "ff81ff80"}
