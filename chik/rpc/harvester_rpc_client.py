from __future__ import annotations

from typing import Any, cast

from chik.rpc.rpc_client import RpcClient


class HarvesterRpcClient(RpcClient):
    """
    Client to Chik RPC, connects to a local harvester. Uses HTTP/JSON, and converts back from
    JSON into native python objects before returning. All api calls use POST requests.
    Note that this is not the same as the peer protocol, or wallet protocol (which run Chik's
    protocol on top of TCP), it's a separate protocol on top of HTTP that provides easy access
    to the full node.
    """

    async def get_plots(self) -> dict[str, Any]:
        return await self.fetch("get_plots", {})

    async def refresh_plots(self) -> None:
        await self.fetch("refresh_plots", {})

    async def delete_plot(self, filename: str) -> bool:
        response = await self.fetch("delete_plot", {"filename": filename})
        # TODO: casting due to lack of type checked deserialization
        result = cast(bool, response["success"])
        return result

    async def add_plot_directory(self, dirname: str) -> bool:
        response = await self.fetch("add_plot_directory", {"dirname": dirname})
        # TODO: casting due to lack of type checked deserialization
        result = cast(bool, response["success"])
        return result

    async def get_plot_directories(self) -> list[str]:
        response = await self.fetch("get_plot_directories", {})
        # TODO: casting due to lack of type checked deserialization
        result = cast(list[str], response["directories"])
        return result

    async def remove_plot_directory(self, dirname: str) -> bool:
        response = await self.fetch("remove_plot_directory", {"dirname": dirname})
        # TODO: casting due to lack of type checked deserialization
        result = cast(bool, response["success"])
        return result

    async def get_harvester_config(self) -> dict[str, Any]:
        return await self.fetch("get_harvester_config", {})

    async def update_harvester_config(self, config: dict[str, Any]) -> bool:
        response = await self.fetch("update_harvester_config", config)
        # TODO: casting due to lack of type checked deserialization
        result = cast(bool, response["success"])
        return result
