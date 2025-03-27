from __future__ import annotations

import os
import pathlib
import sys
from typing import Any, Optional

from chik_rs import ConsensusConstants

from chik.apis import ApiProtocolRegistry
from chik.consensus.constants import replace_str_to_bytes
from chik.consensus.default_constants import DEFAULT_CONSTANTS, update_testnet_overrides
from chik.farmer.farmer import Farmer
from chik.farmer.farmer_api import FarmerAPI
from chik.rpc.farmer_rpc_api import FarmerRpcApi
from chik.server.outbound_message import NodeType
from chik.server.signal_handlers import SignalHandlers
from chik.server.start_service import RpcInfo, Service, async_run
from chik.types.aliases import FarmerService
from chik.util.chik_logging import initialize_service_logging
from chik.util.config import get_unresolved_peer_infos, load_config, load_config_cli
from chik.util.default_root import resolve_root_path
from chik.util.keychain import Keychain
from chik.util.task_timing import maybe_manage_task_instrumentation

# See: https://bugs.python.org/issue29288
"".encode("idna")

SERVICE_NAME = "farmer"


def create_farmer_service(
    root_path: pathlib.Path,
    config: dict[str, Any],
    config_pool: dict[str, Any],
    consensus_constants: ConsensusConstants,
    keychain: Optional[Keychain] = None,
    connect_to_daemon: bool = True,
) -> FarmerService:
    service_config = config[SERVICE_NAME]

    network_id = service_config["selected_network"]
    overrides = service_config["network_overrides"]["constants"][network_id]
    update_testnet_overrides(network_id, overrides)
    updated_constants = replace_str_to_bytes(consensus_constants, **overrides)

    node = Farmer(
        root_path, service_config, config_pool, consensus_constants=updated_constants, local_keychain=keychain
    )
    peer_api = FarmerAPI(node)

    rpc_info: Optional[RpcInfo[FarmerRpcApi]] = None
    if service_config.get("start_rpc_server", True):
        rpc_info = (FarmerRpcApi, service_config["rpc_port"])

    return Service(
        root_path=root_path,
        config=config,
        node=node,
        peer_api=peer_api,
        node_type=NodeType.FARMER,
        advertised_port=service_config["port"],
        service_name=SERVICE_NAME,
        connect_peers=get_unresolved_peer_infos(service_config, NodeType.FULL_NODE),
        on_connect_callback=node.on_connect,
        network_id=network_id,
        rpc_info=rpc_info,
        connect_to_daemon=connect_to_daemon,
        class_for_type=ApiProtocolRegistry,
    )


async def async_main(root_path: pathlib.Path) -> int:
    # TODO: refactor to avoid the double load
    config = load_config(root_path, "config.yaml")
    service_config = load_config_cli(root_path, "config.yaml", SERVICE_NAME)
    config[SERVICE_NAME] = service_config
    config_pool = load_config_cli(root_path, "config.yaml", "pool")
    config["pool"] = config_pool
    initialize_service_logging(service_name=SERVICE_NAME, config=config, root_path=root_path)

    service = create_farmer_service(root_path, config, config_pool, DEFAULT_CONSTANTS)
    async with SignalHandlers.manage() as signal_handlers:
        await service.setup_process_global_state(signal_handlers=signal_handlers)
        await service.run()

    return 0


def main() -> int:
    root_path = resolve_root_path(override=None)

    with maybe_manage_task_instrumentation(
        enable=os.environ.get(f"CHIK_INSTRUMENT_{SERVICE_NAME.upper()}") is not None
    ):
        return async_run(coro=async_main(root_path=root_path))


if __name__ == "__main__":
    sys.exit(main())
