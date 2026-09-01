from __future__ import annotations

from chik.server.start_service import Service
from chik.timelord.timelord import Timelord
from chik.timelord.timelord_api import TimelordAPI
from chik.timelord.timelord_rpc_api import TimelordRpcApi

TimelordService = Service[Timelord, TimelordAPI, TimelordRpcApi]
