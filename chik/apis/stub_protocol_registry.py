from __future__ import annotations

from chik.apis.farmer_stub import FarmerApiStub
from chik.apis.full_node_stub import FullNodeApiStub
from chik.apis.harvester_stub import HarvesterApiStub
from chik.apis.introducer_stub import IntroducerApiStub
from chik.apis.solver_stub import SolverApiStub
from chik.apis.timelord_stub import TimelordApiStub
from chik.apis.wallet_stub import WalletNodeApiStub
from chik.protocols.outbound_message import NodeType
from chik.server.api_protocol import ApiMetadata

StubMetadataRegistry: dict[NodeType, ApiMetadata] = {
    NodeType.FULL_NODE: FullNodeApiStub.metadata,
    NodeType.WALLET: WalletNodeApiStub.metadata,
    NodeType.INTRODUCER: IntroducerApiStub.metadata,
    NodeType.TIMELORD: TimelordApiStub.metadata,
    NodeType.FARMER: FarmerApiStub.metadata,
    NodeType.HARVESTER: HarvesterApiStub.metadata,
    NodeType.SOLVER: SolverApiStub.metadata,
}
