from __future__ import annotations

import click

from chik.cmds.gh import gh_group
from chik.cmds.installers import installers_group
from chik.cmds.sim import sim_cmd


@click.group("dev", help="Developer commands and tools")
@click.pass_context
def dev_cmd(ctx: click.Context) -> None:
    pass


dev_cmd.add_command(sim_cmd)
dev_cmd.add_command(installers_group)
dev_cmd.add_command(gh_group)
