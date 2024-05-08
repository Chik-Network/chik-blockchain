from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from chik._tests.util.misc import DataCase, Marks, datacases
from chik.server.outbound_message import NodeType
from chik.types.peer_info import UnresolvedPeerInfo
from chik.util.config import get_unresolved_peer_infos, set_peer_info
from chik.util.ints import uint16


@dataclass
class GetUnresolvedPeerInfosCase(DataCase):
    description: str
    service_config: Dict[str, Any]
    requested_node_type: NodeType
    expected_peer_infos: Set[UnresolvedPeerInfo]
    marks: Marks = ()

    @property
    def id(self) -> str:
        return self.description


@datacases(
    GetUnresolvedPeerInfosCase(
        description="multiple farmer peers",
        service_config={
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        expected_peer_infos={
            UnresolvedPeerInfo(host="127.0.0.1", port=uint16(9681)),
            UnresolvedPeerInfo(host="my.farmer.tld", port=uint16(19681)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="single farmer peer",
        service_config={
            "farmer_peer": {
                "host": "my.farmer.tld",
                "port": 19681,
            },
        },
        requested_node_type=NodeType.FARMER,
        expected_peer_infos={
            UnresolvedPeerInfo(host="my.farmer.tld", port=uint16(19681)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="single farmer peer and multiple farmer peers",
        service_config={
            "farmer_peer": {
                "host": "my.farmer.tld",
                "port": 19681,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.other.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        expected_peer_infos={
            UnresolvedPeerInfo(host="my.farmer.tld", port=uint16(19681)),
            UnresolvedPeerInfo(host="127.0.0.1", port=uint16(9681)),
            UnresolvedPeerInfo(host="my.other.farmer.tld", port=uint16(19681)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="multiple full node peers",
        service_config={
            "full_node_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9678,
                },
                {
                    "host": "my.full-node.tld",
                    "port": 19678,
                },
            ],
        },
        requested_node_type=NodeType.FULL_NODE,
        expected_peer_infos={
            UnresolvedPeerInfo(host="127.0.0.1", port=uint16(9678)),
            UnresolvedPeerInfo(host="my.full-node.tld", port=uint16(19678)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="single full node peer",
        service_config={
            "full_node_peer": {
                "host": "my.full-node.tld",
                "port": 19678,
            },
        },
        requested_node_type=NodeType.FULL_NODE,
        expected_peer_infos={
            UnresolvedPeerInfo(host="my.full-node.tld", port=uint16(19678)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="single full node peer and multiple full node peers",
        service_config={
            "full_node_peer": {
                "host": "my.full-node.tld",
                "port": 19678,
            },
            "full_node_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9678,
                },
                {
                    "host": "my.other.full-node.tld",
                    "port": 19678,
                },
            ],
        },
        requested_node_type=NodeType.FULL_NODE,
        expected_peer_infos={
            UnresolvedPeerInfo(host="my.full-node.tld", port=uint16(19678)),
            UnresolvedPeerInfo(host="127.0.0.1", port=uint16(9678)),
            UnresolvedPeerInfo(host="my.other.full-node.tld", port=uint16(19678)),
        },
    ),
    GetUnresolvedPeerInfosCase(
        description="no peer info in config",
        service_config={},
        requested_node_type=NodeType.FULL_NODE,
        expected_peer_infos=set(),
    ),
)
def test_get_unresolved_peer_infos(case: GetUnresolvedPeerInfosCase) -> None:
    assert get_unresolved_peer_infos(case.service_config, case.requested_node_type) == case.expected_peer_infos


@dataclass
class SetPeerInfoCase(DataCase):
    description: str
    service_config: Dict[str, Any]
    requested_node_type: NodeType
    expected_service_config: Dict[str, Any]
    peer_host: Optional[str] = None
    peer_port: Optional[int] = None
    marks: Marks = ()

    @property
    def id(self) -> str:
        return self.description


@datacases(
    SetPeerInfoCase(
        description="multiple peers, modify first entry, set host and port",
        service_config={
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        peer_port=1337,
        expected_service_config={
            "farmer_peers": [
                {
                    "host": "localhost",
                    "port": 1337,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
    SetPeerInfoCase(
        description="multiple peers, modify first entry, set host",
        service_config={
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        expected_service_config={
            "farmer_peers": [
                {
                    "host": "localhost",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
    SetPeerInfoCase(
        description="multiple peers, modify first entry, set port",
        service_config={
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_port=1337,
        expected_service_config={
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 1337,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
    SetPeerInfoCase(
        description="single peer, set host and port",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 9681,
            },
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        peer_port=1337,
        expected_service_config={
            "farmer_peer": {
                "host": "localhost",
                "port": 1337,
            },
        },
    ),
    SetPeerInfoCase(
        description="single peer, set host",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 9681,
            },
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        expected_service_config={
            "farmer_peer": {
                "host": "localhost",
                "port": 9681,
            },
        },
    ),
    SetPeerInfoCase(
        description="single peer, set port",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 9681,
            },
        },
        requested_node_type=NodeType.FARMER,
        peer_port=1337,
        expected_service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 1337,
            },
        },
    ),
    SetPeerInfoCase(
        description="single and multiple peers, modify single peer, set host and port",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 29681,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        peer_port=1337,
        expected_service_config={
            "farmer_peer": {
                "host": "localhost",
                "port": 1337,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
    SetPeerInfoCase(
        description="single and multiple peers, modify single peer, set host",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 29681,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_host="localhost",
        expected_service_config={
            "farmer_peer": {
                "host": "localhost",
                "port": 29681,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
    SetPeerInfoCase(
        description="single and multiple peers, modify single peer, set port",
        service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 29681,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
        requested_node_type=NodeType.FARMER,
        peer_port=1337,
        expected_service_config={
            "farmer_peer": {
                "host": "127.0.0.1",
                "port": 1337,
            },
            "farmer_peers": [
                {
                    "host": "127.0.0.1",
                    "port": 9681,
                },
                {
                    "host": "my.farmer.tld",
                    "port": 19681,
                },
            ],
        },
    ),
)
def test_set_peer_info(case: SetPeerInfoCase) -> None:
    set_peer_info(case.service_config, case.requested_node_type, peer_host=case.peer_host, peer_port=case.peer_port)

    assert case.service_config == case.expected_service_config
