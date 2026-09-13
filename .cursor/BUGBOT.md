# Bugbot Review Guidance

Use the repository context map before reporting issues that depend on
cross-file invariants. Prefer the relevant context document over reasoning from
a narrow diff alone. Start with `.cursor/context/INDEX.md` when unsure.

## Context Routing

Before reviewing a changed file, identify the subsystem and read the matching
context document:

| Changed area                                                   | Read first                             |
| -------------------------------------------------------------- | -------------------------------------- |
| `chik/consensus/**`, block validation, difficulty, SSI, reorgs | `.cursor/context/consensus.md`         |
| `chik/full_node/**`, sync, batch validation, node state        | `.cursor/context/full-node.md`         |
| `chik/full_node/mempool*.py`, fee logic, spend admission       | `.cursor/context/mempool.md`           |
| `chik/server/**`, peer connections, rate limits                | `.cursor/context/server.md`            |
| `chik/protocols/**`, wire messages                             | `.cursor/context/protocols.md`         |
| `chik/apis/**`, API stub metadata                              | `.cursor/context/apis.md`              |
| `chik/types/**`, shared types, serialization boundary          | `.cursor/context/types.md`             |
| `chik/wallet/**`                                               | `.cursor/context/wallet.md`            |
| CLVK, generators, puzzles, conditions                          | `.cursor/context/clvk-execution.md`    |
| `chik/farmer/**`                                               | `.cursor/context/farmer.md`            |
| `chik/harvester/**`                                            | `.cursor/context/harvester.md`         |
| `chik/timelord/**`                                             | `.cursor/context/timelord.md`          |
| `chik/plotting/**`, `chik/plot_sync/**`                        | `.cursor/context/plotting.md`          |
| `chik/pools/**`                                                | `.cursor/context/pools.md`             |
| `chik/daemon/**`                                               | `.cursor/context/daemon.md`            |
| `chik/data_layer/**`                                           | `.cursor/context/data-layer.md`        |
| `chik/rpc/**`                                                  | `.cursor/context/rpc.md`               |
| `chik/ssl/**`                                                  | `.cursor/context/ssl.md`               |
| `chik/simulator/**`                                            | `.cursor/context/simulator.md`         |
| `chik/solver/**`                                               | `.cursor/context/solver.md`            |
| `chik/cmds/**`                                                 | `.cursor/context/cmds.md`              |
| `chik/util/**`                                                 | `.cursor/context/util.md`              |
| Root config, build scripts, workflows, tooling                 | `.cursor/context/repo-tooling.md`      |
| Cross-cutting or security-sensitive changes                    | `.cursor/context/global-invariants.md` |

If multiple areas are touched, read each matching context document and check
the interaction between their invariants. If a suspected issue contradicts the
context, verify the full path before reporting it.
