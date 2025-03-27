from __future__ import annotations

from chik_rs.sized_bytes import bytes32
from chik_rs.sized_ints import uint64

from chik._tests.cmds.test_cmd_framework import check_click_parsing
from chik.cmds.cmd_classes import ChikCliContext
from chik.cmds.cmd_helpers import NeedsWalletRPC
from chik.cmds.param_types import CliAddress
from chik.cmds.plotnft import (
    ChangePayoutInstructionsPlotNFTCMD,
    ClaimPlotNFTCMD,
    CreatePlotNFTCMD,
    GetLoginLinkCMD,
    InspectPlotNFTCMD,
    JoinPlotNFTCMD,
    LeavePlotNFTCMD,
    ShowPlotNFTCMD,
)
from chik.util.bech32m import encode_puzzle_hash
from chik.wallet.util.address_type import AddressType


def test_plotnft_command_default_parsing() -> None:
    launcher_id = bytes32([1] * 32)
    check_click_parsing(
        GetLoginLinkCMD(launcher_id=launcher_id),
        "--launcher_id",
        launcher_id.hex(),
    )

    burn_ph = bytes32.from_hexstr("0x000000000000000000000000000000000000000000000000000000000000dead")
    burn_address = encode_puzzle_hash(burn_ph, "xck")
    check_click_parsing(
        ChangePayoutInstructionsPlotNFTCMD(
            launcher_id=launcher_id, address=CliAddress(burn_ph, burn_address, AddressType.XCK)
        ),
        "--launcher_id",
        launcher_id.hex(),
        "--address",
        burn_address,
        # Needed for AddressParamType to work correctly without config
        context=ChikCliContext(expected_prefix="xck"),
    )

    check_click_parsing(
        ClaimPlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None), fee=uint64(1), id=5
        ),
        "--id",
        "5",
        "--fee",
        "0.000000000001",
    )

    check_click_parsing(
        CreatePlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None),
            pool_url="http://localhost:1234",
            state="pool",
            fee=uint64(0),
            dont_prompt=False,
        ),
        "--state",
        "pool",
        "--pool-url",
        "http://localhost:1234",
        "--fee",
        "0.0",
    )

    check_click_parsing(
        CreatePlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None),
            pool_url=None,
            state="local",
            fee=uint64(0),
            dont_prompt=True,
        ),
        "--state",
        "local",
        "-y",
    )

    check_click_parsing(
        InspectPlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None),
            id=5,
        ),
        "--id",
        "5",
    )

    check_click_parsing(
        JoinPlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None),
            id=5,
            fee=uint64(3),
            pool_url="http://localhost:1234",
            dont_prompt=True,
        ),
        "--id",
        "5",
        "--fee",
        "0.000000000003",
        "--pool-url",
        "http://localhost:1234",
        "-y",
    )

    check_click_parsing(
        LeavePlotNFTCMD(
            rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None),
            id=5,
            fee=uint64(3),
            dont_prompt=True,
        ),
        "--id",
        "5",
        "--fee",
        "0.000000000003",
        "-y",
    )

    check_click_parsing(
        ShowPlotNFTCMD(rpc_info=NeedsWalletRPC(client_info=None, wallet_rpc_port=None, fingerprint=None), id=5),
        "--id",
        "5",
    )
