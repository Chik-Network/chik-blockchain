from __future__ import annotations

from chik.full_node.full_node import FullNode
from chik.full_node.full_node_api import FullNodeAPI
from chik.full_node.full_node_rpc_api import FullNodeRpcApi
from chik.server.start_service import Service

FullNodeService = Service[FullNode, FullNodeAPI, FullNodeRpcApi]
