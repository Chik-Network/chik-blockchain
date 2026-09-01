from __future__ import annotations

from chik.farmer.farmer import Farmer
from chik.farmer.farmer_api import FarmerAPI
from chik.farmer.farmer_rpc_api import FarmerRpcApi
from chik.server.start_service import Service

FarmerService = Service[Farmer, FarmerAPI, FarmerRpcApi]
