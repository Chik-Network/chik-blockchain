from __future__ import annotations

from typing import Optional

import click

from chik.cmds.cmd_classes import ChikCliContext


@click.command("netspace", help="Estimate total farmed space on the network")
@click.option(
    "-p",
    "--rpc-port",
    help=(
        "Set the port where the Full Node is hosting the RPC interface. "
        "See the rpc_port under full_node in config.yaml. "
        "[default: 9789]"
    ),
    type=int,
    default=None,
)
@click.option(
    "-d",
    "--delta-block-height",
    help=(
        "Compare a block X blocks older to estimate total network space. "
        "Defaults to 4608 blocks (~1 day) and Peak block as the starting block. "
        "Use --start BLOCK_HEIGHT to specify starting block. "
        "Use 192 blocks to estimate over the last hour."
    ),
    type=str,
    default="4608",
)
@click.option(
    "-s",
    "--start",
    help="Newest block used to calculate estimated total network space. Defaults to Peak block.",
    type=str,
    default="",
)
@click.pass_context
def netspace_cmd(ctx: click.Context, rpc_port: Optional[int], delta_block_height: str, start: str) -> None:
    """
    Calculates the estimated space on the network given two block header hashes.
    """
    import asyncio

    from chik.cmds.netspace_funcs import netstorge_async

    asyncio.run(netstorge_async(ChikCliContext.set_default(ctx).root_path, rpc_port, delta_block_height, start))
