from __future__ import annotations

from chik.full_node.full_node_rpc_api import FullNodeRpcApi
from chik.introducer.introducer import Introducer
from chik.introducer.introducer_api import IntroducerAPI
from chik.server.start_service import Service

IntroducerService = Service[Introducer, IntroducerAPI, FullNodeRpcApi]
