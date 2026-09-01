from __future__ import annotations

from chik.data_layer.data_layer import DataLayer
from chik.data_layer.data_layer_api import DataLayerAPI
from chik.data_layer.data_layer_rpc_api import DataLayerRpcApi
from chik.server.start_service import Service

DataLayerService = Service[DataLayer, DataLayerAPI, DataLayerRpcApi]
