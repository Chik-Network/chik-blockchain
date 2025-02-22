from __future__ import annotations

import pytest

from chik.protocols.full_node_protocol import RequestTransaction
from chik.protocols.protocol_message_types import ProtocolMessageTypes
from chik.server.api_protocol import ApiMetadata


def test_api_protocol_raises_for_repeat_request_registration() -> None:
    metadata = ApiMetadata()

    @metadata.request(request_type=ProtocolMessageTypes.handshake)
    async def f(self: object, request: RequestTransaction) -> None: ...

    async def g(self: object, request: RequestTransaction) -> None: ...

    decorator = metadata.request(request_type=ProtocolMessageTypes.handshake)

    with pytest.raises(Exception, match="request type already registered"):
        decorator(g)
