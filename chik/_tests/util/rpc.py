from __future__ import annotations

from chik.rpc.rpc_client import RpcClient
from chik.rpc.rpc_server import RpcApiProtocol


async def validate_get_routes(client: RpcClient, api: RpcApiProtocol) -> None:
    routes_client = (await client.fetch("get_routes", {}))["routes"]
    assert len(routes_client) > 0
    routes_api = list(api.get_routes().keys())
    # TODO: avoid duplication of RpcServer.get_routes()
    routes_server = [
        "/get_network_info",
        "/get_connections",
        "/open_connection",
        "/close_connection",
        "/stop_node",
        "/get_routes",
        "/get_version",
        "/healthz",
    ]
    assert len(routes_api) > 0
    assert sorted(routes_client) == sorted(routes_api + routes_server)
