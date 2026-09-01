# Architecture Overview

> Attach this file when starting unfamiliar work or needing first-time
> orientation on the chik-blockchain codebase.

## Project shape

Python PoST blockchain. **Not a monorepo** — this repository (`chik-blockchain`)
is the Python node implementation. It depends on several external packages from
the Chik-Network GitHub org for Rust-accelerated cryptography, proofs, and
puzzle compilation.

## External Chik dependencies

| Package           | Repo                                                                            | Role                                                                                                                                                        | Used by                                                                    |
| ----------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `chik_rs`         | [Chik-Network/chik_rs](https://github.com/Chik-Network/chik_rs)                 | Core Rust FFI: consensus types, BLS signatures, KLVM execution, serialization, condition validation, spend bundle validation, merkle sets, V2 proof solving | Nearly everything — consensus, mempool, wallet, types, solver              |
| `chikpos`         | [Chik-Network/chikpos](https://github.com/Chik-Network/chikpos)                 | Proof of Space: plot creation, proof verification, quality computation                                                                                      | `chik/plotting/`, `chik/types/blockchain_format/proof_of_space.py`         |
| `chikvdf`         | [Chik-Network/chikvdf](https://github.com/Chik-Network/chikvdf)                 | VDF computation and proof verification                                                                                                                      | `chik/timelord/`, `chik/types/blockchain_format/vdf.py`, `chik/simulator/` |
| `klvm`            | [Chik-Network/klvm](https://github.com/Chik-Network/klvm)                       | Python KLVM interpreter (used in tooling, not consensus-hot path)                                                                                           | `chik/types/blockchain_format/program.py`, wallet puzzle drivers           |
| `klvm_tools`      | [Chik-Network/klvm_tools](https://github.com/Chik-Network/klvm_tools)           | KLVM utilities: currying, `Program.to()`, disassembly                                                                                                       | Wallet puzzle construction, tests, debugging                               |
| `chiklisp`        | [Chik-Network/chiklisp](https://github.com/Chik-Network/chiklisp)               | Rust ChikLisp compiler — compiles `.clsp` puzzle source to KLVM bytecode                                                                                    | `chik/wallet/puzzles/load_klvm.py`, puzzle compilation tooling             |
| `chik-puzzles-py` | [Chik-Network/chik-puzzles-py](https://github.com/Chik-Network/chik-puzzles-py) | Pre-compiled standard puzzle bytecode (singletons, CATs, DIDs, NFTs, etc.)                                                                                  | Wallet puzzle drivers, pool puzzles, data layer                            |
| `chikbip158`      | [Chik-Network/chikbip158](https://github.com/Chik-Network/chikbip158)           | BIP-158 compact block filters for lightweight wallet sync                                                                                                   | Block body validation, mempool manager, wallet sync                        |

**Version pinning**: `chik_rs` is pinned to a minor range (`>=0.37.0, <0.38`).
Other Chik packages use minimum-version pins. See `pyproject.toml` for current values.

## Module map

| Module             | Purpose                                                              | Criticality  |
| ------------------ | -------------------------------------------------------------------- | ------------ |
| `chik/consensus/`  | Block validation, difficulty, fork choice, VDF iters, rewards        | **Critical** |
| `chik/full_node/`  | Full node state, mempool, stores, fee estimation, weight proofs, RPC | **Critical** |
| `chik/server/`     | Networking: WebSocket, rate limiting, peer discovery, TLS            | **Critical** |
| `chik/protocols/`  | Wire protocol message definitions between all node types             | **Critical** |
| `chik/wallet/`     | Wallet state, coin selection, spend construction, sub-wallets        | **High**     |
| `chik/farmer/`     | Farming logic, signage point handling, proof forwarding              | **High**     |
| `chik/harvester/`  | Plot file management, PoS lookups                                    | **Medium**   |
| `chik/timelord/`   | VDF computation, infusion point management                           | **High**     |
| `chik/types/`      | Type definitions: blockchain format, mempool items, generators       | **High**     |
| `chik/util/`       | DB wrapper, streamable, keychain, bech32m, etc.                      | **Medium**   |
| `chik/simulator/`  | Test blockchain simulator                                            | Low          |
| `chik/data_layer/` | DataLayer (data-storage singleton)                                   | Medium       |
| `chik/cmds/`       | CLI command handlers                                                 | Low          |

## `chik_rs` boundary (largest external dependency)

Nearly all core consensus types live in Rust via `chik_rs`:

**Types**: `BlockRecord`, `FullBlock`, `ConsensusConstants`, `SpendBundleConditions`,
`CoinRecord`, `SpendBundle`, `EndOfSubSlotBundle`, `HeaderBlock`, `UnfinishedBlock`,
`SubEpochSummary`, `SubEpochChallengeSegment`, `Coin`, `CoinSpend`, `G1Element`,
`G2Element`, `AugSchemeMPL`, `BLSCache`, `PartialProof`.

**Functions**: `validate_klvm_and_signature`, `run_block_generator`,
`run_block_generator2`, `additions_and_removals`, `check_time_locks`,
`compute_merkle_set_root`, `fast_forward_singleton`, `supports_fast_forward`,
`get_flags_for_height_and_constants`, `solution_generator_backrefs`,
`get_puzzle_and_solution_for_coin2`, `is_canonical_serialization`,
`get_conditions_from_spendbundle`, `get_spends_for_trusted_block`,
`solve_proof` (V2 plot solving).

**Rule of thumb**: Consensus-critical _math_ (VDF iteration calculation, difficulty
adjustment, quality computation) is Python. Signature/KLVM/serialization
validation is Rust. VDF proofs are computed by `chikvdf`, PoS proofs by
`chikpos`. Puzzle bytecode comes pre-compiled from `chik-puzzles-py`.

## Actors

Node roles are defined by `NodeType` in `chik/protocols/outbound_message.py`:
`FULL_NODE`, `HARVESTER`, `FARMER`, `TIMELORD`, `INTRODUCER`, `WALLET`,
`DATA_LAYER`, `SOLVER`.

### Full Node (central)

- **P2P API**: `FullNodeAPI` in `full_node_api.py` (~2080 lines)
- **RPC API**: `FullNodeRpcApi` in `full_node_rpc_api.py` (~1170 lines)
- **State machine**: `FullNode` in `full_node.py` (~3400 lines)

### Farmer

- **API**: `FarmerAPI` in `farmer_api.py` — receives signage points, forwards proofs
- **RPC**: `FarmerRpcApi` — local management

### Harvester

- **API**: `HarvesterAPI` in `harvester_api.py` — receives challenges, checks plots

### Timelord

- **API**: `TimelordAPI` in `timelord_api.py` — receives peaks, produces VDFs
- **State**: `TimelordState` in `timelord_state.py`

### Wallet

- **P2P**: `WalletNodeAPI` in `wallet_node_api.py` — coin state updates
- **RPC**: `WalletRpcApi` in `wallet_rpc_api.py` (~3600 lines) — full wallet surface
- **State**: `WalletStateManager` in `wallet_state_manager.py` (~3300 lines)

### Introducer

- **Service**: `Introducer` in `introducer.py` — bootstrap peer discovery
- **API**: `IntroducerAPI` in `introducer_api.py` — serves vetted peer lists

### Data Layer

- **Service**: `DataLayer` in `data_layer.py` — singleton-based data store service
- **RPC**: `DataLayerRpcApi` in `data_layer_rpc_api.py` — DataLayer control surface

### Solver

- **Service**: `Solver` in `solver.py` — solves V2 plot partial proofs into full proofs of space
- **API**: `SolverAPI` in `solver_api.py` — receives `SolverInfo` (partial proof, plot_id, k-size) from farmer, returns full proof via `SolverResponse`

## Wire protocol overview

109 message types in `ProtocolMessageTypes` enum. Key flows:

- **Full Node ↔ Full Node**: `new_peak`, `new_transaction`, `request_block(s)`,
  `new_signage_point_or_end_of_sub_slot`, `request_compact_vdf`
- **Full Node ↔ Wallet**: `new_peak_wallet`, `send_transaction`,
  `coin_state_update`, `request_puzzle_state`, `mempool_items_added/removed`
- **Farmer ↔ Full Node**: `new_signage_point`, `declare_proof_of_space`,
  `request_signed_values`
- **Farmer ↔ Harvester**: `new_signage_point_harvester`, `new_proof_of_space`,
  `request_signatures`
- **Full Node ↔ Timelord**: `new_peak_timelord`, `new_infusion_point_vdf`,
  `new_signage_point_vdf`

## Key type files

| File                                                 | Contents                                               |
| ---------------------------------------------------- | ------------------------------------------------------ |
| `chik/types/blockchain_format/coin.py`               | `Coin` (parent_id, puzzle_hash, amount)                |
| `chik/types/blockchain_format/vdf.py`                | `VDFInfo`, `VDFProof`                                  |
| `chik/types/blockchain_format/proof_of_space.py`     | PoS verification                                       |
| `chik/types/blockchain_format/program.py`            | KLVM program wrappers                                  |
| `chik/types/blockchain_format/serialized_program.py` | Lazy KLVM deserialization                              |
| `chik/types/mempool_item.py`                         | `MempoolItem`, `BundleCoinSpend`, `UnspentLineageInfo` |
| `chik/types/generator_types.py`                      | `BlockGenerator`, `NewBlockGenerator`                  |
| `chik/types/validation_state.py`                     | `ValidationState`                                      |
| `chik/types/weight_proof.py`                         | `WeightProof`                                          |
| `chik/consensus/block_record.py`                     | Re-export of `BlockRecord` from chik_rs                |
| `chik/consensus/default_constants.py`                | `DEFAULT_CONSTANTS` with all parameter values          |
