from __future__ import annotations

import asyncio
import contextlib
import signal
import sys
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Optional, cast

import aiohttp.client_exceptions
import pytest
from chik_rs.sized_ints import uint16
from typing_extensions import Protocol

from chik._tests.core.data_layer.util import ChikRoot
from chik._tests.util.misc import closing_chik_root_popen
from chik.daemon.client import DaemonProxy, connect_to_daemon_and_validate
from chik.rpc.data_layer_rpc_client import DataLayerRpcClient
from chik.rpc.farmer_rpc_client import FarmerRpcClient
from chik.rpc.full_node_rpc_client import FullNodeRpcClient
from chik.rpc.harvester_rpc_client import HarvesterRpcClient
from chik.rpc.rpc_client import RpcClient
from chik.rpc.wallet_rpc_client import WalletRpcClient
from chik.simulator.socket import find_available_listen_port
from chik.util.config import lock_and_load_config, save_config
from chik.util.timing import adjusted_timeout

if sys.platform == "win32" or sys.platform == "cygwin":
    termination_signals = [signal.SIGBREAK, signal.SIGINT, signal.SIGTERM]
    sendable_termination_signals = [signal.SIGTERM]
else:
    termination_signals = [signal.SIGINT, signal.SIGTERM]
    sendable_termination_signals = termination_signals


class CreateServiceProtocol(Protocol):
    @contextlib.asynccontextmanager
    async def __call__(
        self,
        self_hostname: str,
        port: uint16,
        root_path: Path,
        net_config: dict[str, Any],
    ) -> AsyncIterator[RpcClient]:
        yield cast(RpcClient, None)  # pragma: no cover


async def wait_for_daemon_connection(root_path: Path, config: dict[str, Any], timeout: float = 15) -> DaemonProxy:
    timeout = adjusted_timeout(timeout=timeout)

    start = time.monotonic()
    while time.monotonic() - start < timeout:
        client = await connect_to_daemon_and_validate(root_path=root_path, config=config, quiet=True)
        if client is not None:
            break
        await asyncio.sleep(0.1)
    else:
        raise Exception(f"unable to connect within {timeout} seconds")
    return client


@pytest.mark.parametrize(argnames="signal_number", argvalues=sendable_termination_signals)
@pytest.mark.anyio
async def test_daemon_terminates(signal_number: signal.Signals, chik_root: ChikRoot) -> None:
    port = find_available_listen_port()
    with lock_and_load_config(root_path=chik_root.path, filename="config.yaml") as config:
        config["daemon_port"] = port
        save_config(root_path=chik_root.path, filename="config.yaml", config_data=config)

    with closing_chik_root_popen(chik_root=chik_root, args=[sys.executable, "-m", "chik.daemon.server"]) as process:
        client = await wait_for_daemon_connection(root_path=chik_root.path, config=config)

        try:
            return_code = process.poll()
            assert return_code is None

            process.send_signal(signal_number)
            process.communicate(timeout=adjusted_timeout(timeout=10))
        finally:
            await client.close()


@pytest.mark.parametrize(argnames="signal_number", argvalues=sendable_termination_signals)
@pytest.mark.parametrize(
    argnames=["create_service", "module_path", "service_config_name"],
    argvalues=[
        [DataLayerRpcClient.create_as_context, "chik.server.start_data_layer", "data_layer"],
        [FarmerRpcClient.create_as_context, "chik.server.start_farmer", "farmer"],
        [FullNodeRpcClient.create_as_context, "chik.server.start_full_node", "full_node"],
        [HarvesterRpcClient.create_as_context, "chik.server.start_harvester", "harvester"],
        [WalletRpcClient.create_as_context, "chik.server.start_wallet", "wallet"],
        [None, "chik.server.start_introducer", "introducer"],
        # TODO: fails...  make it not do that
        # [None, "chik.seeder.start_crawler", "crawler"],
        [None, "chik.server.start_timelord", "timelord"],
        pytest.param(
            None,
            "chik.timelord.timelord_launcher",
            "timelord_launcher",
            marks=pytest.mark.skipif(
                sys.platform in {"win32", "cygwin"},
                reason="windows is not supported by the timelord launcher",
            ),
        ),
        # TODO: fails...  starts creating plots etc
        # [None, "chik.simulator.start_simulator", "simulator"],
        # TODO: fails...  make it not do that
        # [None, "chik.data_layer.data_layer_server", "data_layer"],
    ],
)
@pytest.mark.anyio
async def test_services_terminate(
    signal_number: signal.Signals,
    chik_root: ChikRoot,
    create_service: Optional[CreateServiceProtocol],
    module_path: str,
    service_config_name: str,
) -> None:
    with lock_and_load_config(root_path=chik_root.path, filename="config.yaml") as config:
        config["daemon_port"] = find_available_listen_port(name="daemon")
        service_config = config[service_config_name]
        api_port_group = service_config
        if service_config_name == "timelord":
            api_port_group = api_port_group["vdf_server"]
        if "port" in api_port_group:
            api_port_group["port"] = 0
        rpc_port = find_available_listen_port(name="rpc")
        service_config["rpc_port"] = rpc_port
        save_config(root_path=chik_root.path, filename="config.yaml", config_data=config)

    # TODO: make the wallet start up regardless so this isn't needed
    with closing_chik_root_popen(
        chik_root=chik_root,
        args=[sys.executable, "-m", "chik.daemon.server"],
    ):
        # Make sure the daemon is running and responsive before starting other services.
        # This probably shouldn't be required.  For now, it helps at least with the
        # farmer.
        daemon_client = await wait_for_daemon_connection(root_path=chik_root.path, config=config)
        await daemon_client.close()

        async with contextlib.AsyncExitStack() as exit_stack:
            process = exit_stack.enter_context(
                closing_chik_root_popen(
                    chik_root=chik_root,
                    args=[sys.executable, "-m", module_path],
                )
            )

            if create_service is None:
                await asyncio.sleep(5)
            else:
                client = await exit_stack.enter_async_context(
                    create_service(
                        self_hostname=config["self_hostname"],
                        port=uint16(rpc_port),
                        root_path=chik_root.path,
                        net_config=config,
                    )
                )

                start = time.monotonic()
                while time.monotonic() - start < 50:
                    return_code = process.poll()
                    assert return_code is None

                    try:
                        result = await client.healthz()
                    except (
                        aiohttp.client_exceptions.ClientConnectorError,
                        aiohttp.client_exceptions.ClientResponseError,
                    ):
                        pass
                    else:
                        if result.get("success", False):
                            break

                    await asyncio.sleep(0.1)
                else:
                    raise Exception("unable to connect")

            return_code = process.poll()
            assert return_code is None

            process.send_signal(signal_number)
            process.communicate(timeout=adjusted_timeout(timeout=30))
