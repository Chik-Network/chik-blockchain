from __future__ import annotations

from chik.data_layer.data_layer import DataLayer
from chik.data_layer.data_layer_api import DataLayerAPI
from chik.data_layer.data_layer_rpc_api import DataLayerRpcApi
from chik.farmer.farmer import Farmer
from chik.farmer.farmer_api import FarmerAPI
from chik.farmer.farmer_rpc_api import FarmerRpcApi
from chik.full_node.full_node import FullNode
from chik.full_node.full_node_api import FullNodeAPI
from chik.full_node.full_node_rpc_api import FullNodeRpcApi
from chik.harvester.harvester import Harvester
from chik.harvester.harvester_api import HarvesterAPI
from chik.harvester.harvester_rpc_api import HarvesterRpcApi
from chik.introducer.introducer import Introducer
from chik.introducer.introducer_api import IntroducerAPI
from chik.seeder.crawler import Crawler
from chik.seeder.crawler_api import CrawlerAPI
from chik.seeder.crawler_rpc_api import CrawlerRpcApi
from chik.server.start_service import Service
from chik.timelord.timelord import Timelord
from chik.timelord.timelord_api import TimelordAPI
from chik.timelord.timelord_rpc_api import TimelordRpcApi
from chik.wallet.wallet_node import WalletNode
from chik.wallet.wallet_node_api import WalletNodeAPI
from chik.wallet.wallet_rpc_api import WalletRpcApi

CrawlerService = Service[Crawler, CrawlerAPI, CrawlerRpcApi]
DataLayerService = Service[DataLayer, DataLayerAPI, DataLayerRpcApi]
FarmerService = Service[Farmer, FarmerAPI, FarmerRpcApi]
FullNodeService = Service[FullNode, FullNodeAPI, FullNodeRpcApi]
HarvesterService = Service[Harvester, HarvesterAPI, HarvesterRpcApi]
IntroducerService = Service[Introducer, IntroducerAPI, FullNodeRpcApi]
TimelordService = Service[Timelord, TimelordAPI, TimelordRpcApi]
WalletService = Service[WalletNode, WalletNodeAPI, WalletRpcApi]
