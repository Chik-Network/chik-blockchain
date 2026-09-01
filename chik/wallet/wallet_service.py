from __future__ import annotations

from chik.server.start_service import Service
from chik.wallet.wallet_node import WalletNode
from chik.wallet.wallet_node_api import WalletNodeAPI
from chik.wallet.wallet_rpc_api import WalletRpcApi

WalletService = Service[WalletNode, WalletNodeAPI, WalletRpcApi]
