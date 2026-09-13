from __future__ import annotations

from dataclasses import dataclass

import pytest
from chik_rs.sized_ints import uint32

from chik.rpc.util import marshal
from chik.util.streamable import Streamable, streamable
from chik.wallet.util.clvk_streamable import clvk_streamable


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
    qat: list[str]
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


@clvk_streamable
@dataclass(frozen=True)
class ClvkSubObject(Streamable):
    qux: bytes


@streamable
@dataclass(frozen=True)
class TestClvkRequestType(Streamable):
    sub: ClvkSubObject


@streamable
@dataclass(frozen=True)
class TestClvkResponseObject(Streamable):
    sub: ClvkSubObject


@pytest.mark.anyio
async def test_clvk_streamable_marshalling() -> None:
    @marshal
    async def test_rpc_endpoint(self: None, request: TestClvkRequestType) -> TestClvkResponseObject:
        return TestClvkResponseObject(request.sub)

    assert await test_rpc_endpoint(
        None,
        {
            "sub": "ffff83717578818180",
            "CHIP-0029": True,
        },
    ) == {"sub": "ffff83717578818180"}
