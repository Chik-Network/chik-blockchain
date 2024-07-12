from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional, Tuple

from chik_rs import PrivateKey

from chik.consensus.coinbase import create_puzzlehash_for_pk
from chik.daemon.server import WebSocketServer, daemon_launch_lock_path
from chik.simulator.full_node_simulator import FullNodeSimulator
from chik.simulator.socket import find_available_listen_port
from chik.simulator.ssl_certs import (
    SSLTestCACertAndPrivateKey,
    SSLTestCollateralWrapper,
    SSLTestNodeCertsAndKeys,
    get_next_nodes_certs_and_keys,
    get_next_private_ca_cert_and_key,
)
from chik.simulator.start_simulator import async_main as start_simulator_main
from chik.ssl.create_ssl import create_all_ssl
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.util.bech32m import encode_puzzle_hash
from chik.util.config import create_default_chik_config, load_config, save_config
from chik.util.errors import KeychainFingerprintExists
from chik.util.ints import uint32
from chik.util.keychain import Keychain
from chik.util.lock import Lockfile
from chik.util.misc import SignalHandlers
from chik.wallet.derive_keys import master_sk_to_wallet_sk

"""
These functions are used to test the simulator.
"""


def mnemonic_fingerprint(keychain: Keychain) -> Tuple[str, int]:
    mnemonic = (
        "today grape album ticket joy idle supreme sausage "
        "oppose voice angle roast you oven betray exact "
        "memory riot escape high dragon knock food blade"
    )
    # add key to keychain
    try:
        sk = keychain.add_key(mnemonic)
    except KeychainFingerprintExists:
        pass
    fingerprint = sk.get_g1().get_fingerprint()
    return mnemonic, fingerprint


def get_puzzle_hash_from_key(keychain: Keychain, fingerprint: int, key_id: int = 1) -> bytes32:
    priv_key_and_entropy = keychain.get_private_key_by_fingerprint(fingerprint)
    if priv_key_and_entropy is None:
        raise Exception("Fingerprint not found")
    private_key = priv_key_and_entropy[0]
    sk_for_wallet_id: PrivateKey = master_sk_to_wallet_sk(private_key, uint32(key_id))
    puzzle_hash: bytes32 = create_puzzlehash_for_pk(sk_for_wallet_id.get_g1())
    return puzzle_hash


def create_config(
    chik_root: Path,
    fingerprint: int,
    private_ca_crt_and_key: Tuple[bytes, bytes],
    node_certs_and_keys: Dict[str, Dict[str, Dict[str, bytes]]],
    keychain: Keychain,
) -> Dict[str, Any]:
    # create chik directories
    create_default_chik_config(chik_root)
    create_all_ssl(
        chik_root,
        private_ca_crt_and_key=private_ca_crt_and_key,
        node_certs_and_keys=node_certs_and_keys,
    )
    # load config
    config = load_config(chik_root, "config.yaml")
    config["full_node"]["send_uncompact_interval"] = 0
    config["full_node"]["target_uncompact_proofs"] = 30
    config["full_node"]["peer_connect_interval"] = 50
    config["full_node"]["sanitize_weight_proof_only"] = False
    config["full_node"]["introducer_peer"] = None
    config["full_node"]["dns_servers"] = []
    config["logging"]["log_stdout"] = True
    config["selected_network"] = "testnet0"
    for service in [
        "harvester",
        "farmer",
        "full_node",
        "wallet",
        "introducer",
        "timelord",
        "pool",
        "simulator",
    ]:
        config[service]["selected_network"] = "testnet0"
    config["daemon_port"] = find_available_listen_port("BlockTools daemon")
    config["full_node"]["port"] = 0
    config["full_node"]["rpc_port"] = find_available_listen_port("Node RPC")
    # simulator overrides
    config["simulator"]["key_fingerprint"] = fingerprint
    config["simulator"]["farming_address"] = encode_puzzle_hash(get_puzzle_hash_from_key(keychain, fingerprint), "txck")
    config["simulator"]["plot_directory"] = "test-simulator/plots"
    # save config
    save_config(chik_root, "config.yaml", config)
    return config


async def start_simulator(chik_root: Path, automated_testing: bool = False) -> AsyncGenerator[FullNodeSimulator, None]:
    sys.argv = [sys.argv[0]]  # clear sys.argv to avoid issues with config.yaml
    started_simulator = await start_simulator_main(True, automated_testing, root_path=chik_root)
    service = started_simulator.service

    async with service.manage():
        yield service._api


async def get_full_chik_simulator(
    chik_root: Path,
    keychain: Optional[Keychain] = None,
    automated_testing: bool = False,
    config: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[Tuple[FullNodeSimulator, Path, Dict[str, Any], str, int, Keychain], None]:
    """
    A chik root Path is required.
    The chik root Path can be a temporary directory (tempfile.TemporaryDirectory)
    Passing in a Keychain prevents test keys from being added to the default key location
    This test can either be run in automated mode or not, which determines which mode block tools run in.
    This test is fully interdependent and can be used without the rest of the chik test suite.
    Please refer to the documentation for more information.
    """

    if keychain is None:
        keychain = Keychain()

    with Lockfile.create(daemon_launch_lock_path(chik_root)):
        mnemonic, fingerprint = mnemonic_fingerprint(keychain)

        ssl_ca_cert_and_key_wrapper: SSLTestCollateralWrapper[SSLTestCACertAndPrivateKey] = (
            get_next_private_ca_cert_and_key()
        )
        ssl_nodes_certs_and_keys_wrapper: SSLTestCollateralWrapper[SSLTestNodeCertsAndKeys] = (
            get_next_nodes_certs_and_keys()
        )
        if config is None:
            config = create_config(
                chik_root,
                fingerprint,
                ssl_ca_cert_and_key_wrapper.collateral.cert_and_key,
                ssl_nodes_certs_and_keys_wrapper.collateral.certs_and_keys,
                keychain,
            )
        crt_path = chik_root / config["daemon_ssl"]["private_crt"]
        key_path = chik_root / config["daemon_ssl"]["private_key"]
        ca_crt_path = chik_root / config["private_ssl_ca"]["crt"]
        ca_key_path = chik_root / config["private_ssl_ca"]["key"]

        ws_server = WebSocketServer(chik_root, ca_crt_path, ca_key_path, crt_path, key_path)
        async with SignalHandlers.manage() as signal_handlers:
            await ws_server.setup_process_global_state(signal_handlers=signal_handlers)
            async with ws_server.run():
                async for simulator in start_simulator(chik_root, automated_testing):
                    yield simulator, chik_root, config, mnemonic, fingerprint, keychain
