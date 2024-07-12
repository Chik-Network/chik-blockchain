from __future__ import annotations

from chik.data_layer.data_layer import DataLayer
from chik.data_layer.data_layer_api import DataLayerAPI
from chik.farmer.farmer import Farmer
from chik.farmer.farmer_api import FarmerAPI
from chik.full_node.full_node import FullNode
from chik.full_node.full_node_api import FullNodeAPI
from chik.harvester.harvester import Harvester
from chik.harvester.harvester_api import HarvesterAPI
from chik.introducer.introducer import Introducer
from chik.introducer.introducer_api import IntroducerAPI
from chik.rpc.crawler_rpc_api import CrawlerRpcApi
from chik.rpc.data_layer_rpc_api import DataLayerRpcApi
from chik.rpc.farmer_rpc_api import FarmerRpcApi
from chik.rpc.full_node_rpc_api import FullNodeRpcApi
from chik.rpc.harvester_rpc_api import HarvesterRpcApi
from chik.rpc.timelord_rpc_api import TimelordRpcApi
from chik.rpc.wallet_rpc_api import WalletRpcApi
from chik.seeder.crawler import Crawler
from chik.seeder.crawler_api import CrawlerAPI
from chik.server.start_service import Service
from chik.timelord.timelord import Timelord
from chik.timelord.timelord_api import TimelordAPI
from chik.wallet.wallet_node import WalletNode
from chik.wallet.wallet_node_api import WalletNodeAPI

CrawlerService = Service[Crawler, CrawlerAPI, CrawlerRpcApi]
DataLayerService = Service[DataLayer, DataLayerAPI, DataLayerRpcApi]
FarmerService = Service[Farmer, FarmerAPI, FarmerRpcApi]
FullNodeService = Service[FullNode, FullNodeAPI, FullNodeRpcApi]
HarvesterService = Service[Harvester, HarvesterAPI, HarvesterRpcApi]
IntroducerService = Service[Introducer, IntroducerAPI, FullNodeRpcApi]
TimelordService = Service[Timelord, TimelordAPI, TimelordRpcApi]
WalletService = Service[WalletNode, WalletNodeAPI, WalletRpcApi]
