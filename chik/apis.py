from __future__ import annotations

from chik.farmer.farmer_api import FarmerAPI
from chik.full_node.full_node_api import FullNodeAPI
from chik.harvester.harvester_api import HarvesterAPI
from chik.introducer.introducer_api import IntroducerAPI
from chik.server.api_protocol import ApiProtocol
from chik.server.outbound_message import NodeType
from chik.timelord.timelord_api import TimelordAPI
from chik.wallet.wallet_node_api import WalletNodeAPI

ApiProtocolRegistry: dict[NodeType, type[ApiProtocol]] = {
    NodeType.FULL_NODE: FullNodeAPI,
    NodeType.WALLET: WalletNodeAPI,
    NodeType.INTRODUCER: IntroducerAPI,
    NodeType.TIMELORD: TimelordAPI,
    NodeType.FARMER: FarmerAPI,
    NodeType.HARVESTER: HarvesterAPI,
}
