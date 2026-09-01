from __future__ import annotations

from chik.harvester.harvester import Harvester
from chik.harvester.harvester_api import HarvesterAPI
from chik.harvester.harvester_rpc_api import HarvesterRpcApi
from chik.server.start_service import Service

HarvesterService = Service[Harvester, HarvesterAPI, HarvesterRpcApi]
