from __future__ import annotations

import asyncio
import logging
import time
import traceback
from concurrent.futures import Executor
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from chik_rs import AugSchemeMPL, SpendBundleConditions

from chik.consensus.block_header_validation import validate_finished_header_block
from chik.consensus.block_record import BlockRecord
from chik.consensus.blockchain_interface import BlocksProtocol
from chik.consensus.constants import ConsensusConstants
from chik.consensus.cost_calculator import NPCResult
from chik.consensus.full_block_to_block_record import block_to_block_record
from chik.consensus.get_block_challenge import get_block_challenge
from chik.consensus.get_block_generator import get_block_generator
from chik.consensus.pot_iterations import calculate_iterations_quality, is_overflow_block
from chik.full_node.mempool_check_conditions import get_name_puzzle_conditions
from chik.types.blockchain_format.coin import Coin
from chik.types.blockchain_format.proof_of_space import verify_and_get_quality_string
from chik.types.blockchain_format.sized_bytes import bytes32
from chik.types.blockchain_format.sub_epoch_summary import SubEpochSummary
from chik.types.full_block import FullBlock
from chik.types.generator_types import BlockGenerator
from chik.types.unfinished_block import UnfinishedBlock
from chik.util.augmented_chain import AugmentedBlockchain
from chik.util.block_cache import BlockCache
from chik.util.condition_tools import pkm_pairs
from chik.util.errors import Err, ValidationError
from chik.util.generator_tools import get_block_header, tx_removals_and_additions
from chik.util.ints import uint16, uint32, uint64
from chik.util.streamable import Streamable, streamable

log = logging.getLogger(__name__)


@streamable
@dataclass(frozen=True)
class PreValidationResult(Streamable):
    error: Optional[uint16]
    required_iters: Optional[uint64]  # Iff error is None
    conds: Optional[SpendBundleConditions]  # Iff error is None and block is a transaction block
    validated_signature: bool
    timing: uint32  # the time (in milliseconds) it took to pre-validate the block


def batch_pre_validate_blocks(
    constants: ConsensusConstants,
    blocks_pickled: Dict[bytes, bytes],
    full_blocks_pickled: List[bytes],
    prev_transaction_generators: List[Optional[List[bytes]]],
    conditions: Dict[uint32, bytes],
    expected_difficulty: List[uint64],
    expected_sub_slot_iters: List[uint64],
    validate_signatures: bool,
    prev_ses_block_bytes: Optional[List[Optional[bytes]]] = None,
) -> List[bytes]:
    blocks: Dict[bytes32, BlockRecord] = {}
    for k, v in blocks_pickled.items():
        blocks[bytes32(k)] = BlockRecord.from_bytes_unchecked(v)
    results: List[PreValidationResult] = []

    # In this case, we are validating full blocks, not headers
    for i in range(len(full_blocks_pickled)):
        try:
            validation_start = time.monotonic()
            block: FullBlock = FullBlock.from_bytes_unchecked(full_blocks_pickled[i])
            tx_additions: List[Coin] = []
            removals: List[bytes32] = []
            conds: Optional[SpendBundleConditions] = None
            if block.height in conditions:
                conds = SpendBundleConditions.from_bytes(conditions[block.height])
                removals, tx_additions = tx_removals_and_additions(conds)
            elif block.transactions_generator is not None:
                # TODO: this function would be simpler if conditions were
                # required to be passed in for all transaction blocks. We would
                # no longer need prev_transaction_generators
                prev_generators = prev_transaction_generators[i]
                assert prev_generators is not None
                assert block.transactions_info is not None
                block_generator = BlockGenerator(block.transactions_generator, prev_generators)
                assert block_generator.program == block.transactions_generator
                npc_result = get_name_puzzle_conditions(
                    block_generator,
                    min(constants.MAX_BLOCK_COST_KLVM, block.transactions_info.cost),
                    mempool_mode=False,
                    height=block.height,
                    constants=constants,
                )
                if npc_result.error is not None:
                    validation_time = time.monotonic() - validation_start
                    results.append(
                        PreValidationResult(
                            uint16(npc_result.error), None, npc_result.conds, False, uint32(validation_time * 1000)
                        )
                    )
                    continue
                assert npc_result.conds is not None
                conds = npc_result.conds
                removals, tx_additions = tx_removals_and_additions(conds)

            header_block = get_block_header(block, tx_additions, removals)
            prev_ses_block = None
            if prev_ses_block_bytes is not None and len(prev_ses_block_bytes) > 0:
                buffer = prev_ses_block_bytes[i]
                if buffer is not None:
                    prev_ses_block = BlockRecord.from_bytes_unchecked(buffer)
            required_iters, error = validate_finished_header_block(
                constants,
                BlockCache(blocks),
                header_block,
                True,  # check_filter
                expected_difficulty[i],
                expected_sub_slot_iters[i],
                prev_ses_block=prev_ses_block,
            )
            error_int: Optional[uint16] = None
            if error is not None:
                error_int = uint16(error.code.value)

            successfully_validated_signatures = False
            # If we failed header block validation, no need to validate
            # signature, the block is already invalid If this is False, it means
            # either we don't have a signature (not a tx block) or we have an
            # invalid signature (which also puts in an error) or we didn't
            # validate the signature because we want to validate it later.
            # add_block will attempt to validate the signature later.
            if error_int is None and validate_signatures and conds is not None:
                assert block.transactions_info is not None
                pairs_pks, pairs_msgs = pkm_pairs(conds, constants.AGG_SIG_ME_ADDITIONAL_DATA)
                if not AugSchemeMPL.aggregate_verify(
                    pairs_pks, pairs_msgs, block.transactions_info.aggregated_signature
                ):
                    error_int = uint16(Err.BAD_AGGREGATE_SIGNATURE.value)
                else:
                    successfully_validated_signatures = True

            validation_time = time.monotonic() - validation_start
            results.append(
                PreValidationResult(
                    error_int,
                    required_iters,
                    conds,
                    successfully_validated_signatures,
                    uint32(validation_time * 1000),
                )
            )
        except Exception:
            error_stack = traceback.format_exc()
            log.error(f"Exception: {error_stack}")
            validation_time = time.monotonic() - validation_start
            results.append(
                PreValidationResult(uint16(Err.UNKNOWN.value), None, None, False, uint32(validation_time * 1000))
            )
    return [bytes(r) for r in results]


async def pre_validate_blocks_multiprocessing(
    constants: ConsensusConstants,
    block_records: BlocksProtocol,
    blocks: Sequence[FullBlock],
    pool: Executor,
    block_height_conds_map: Dict[uint32, SpendBundleConditions],
    *,
    sub_slot_iters: uint64,
    difficulty: uint64,
    prev_ses_block: Optional[BlockRecord],
    wp_summaries: Optional[List[SubEpochSummary]] = None,
    validate_signatures: bool = True,
) -> List[PreValidationResult]:
    """
    This method must be called under the blockchain lock
    If all the full blocks pass pre-validation, (only validates header), returns the list of required iters.
    if any validation issue occurs, returns False.

    Args:
        constants:
        pool:
        constants:
        block_records:
        blocks: list of full blocks to validate (must be connected to current chain)
        npc_results
    """
    prev_b: Optional[BlockRecord] = None

    # Collects all the recent blocks (up to the previous sub-epoch)
    recent_blocks: Dict[bytes32, BlockRecord] = {}
    num_sub_slots_found = 0
    num_blocks_seen = 0

    if blocks[0].height > 0:
        curr = block_records.try_block_record(blocks[0].prev_header_hash)
        if curr is None:
            return [PreValidationResult(uint16(Err.INVALID_PREV_BLOCK_HASH.value), None, None, False, uint32(0))]
        prev_b = curr
        num_sub_slots_to_look_for = 3 if curr.overflow else 2
        header_hash = curr.header_hash
        while (
            curr.sub_epoch_summary_included is None
            or num_blocks_seen < constants.NUMBER_OF_TIMESTAMPS
            or num_sub_slots_found < num_sub_slots_to_look_for
        ) and curr.height > 0:
            if curr.first_in_sub_slot:
                assert curr.finished_challenge_slot_hashes is not None
                num_sub_slots_found += len(curr.finished_challenge_slot_hashes)
            recent_blocks[header_hash] = curr
            if curr.is_transaction_block:
                num_blocks_seen += 1
            header_hash = curr.prev_hash
            curr = block_records.block_record(curr.prev_hash)
            assert curr is not None
        recent_blocks[header_hash] = curr

    # the agumented blockchain object will let us add temporary block records
    # they won't actually be added to the underlying blockchain object
    blockchain = AugmentedBlockchain(block_records)

    diff_ssis: List[Tuple[uint64, uint64]] = []
    prev_ses_block_list: List[Optional[BlockRecord]] = []

    for block in blocks:
        if len(block.finished_sub_slots) > 0:
            if block.finished_sub_slots[0].challenge_chain.new_difficulty is not None:
                difficulty = block.finished_sub_slots[0].challenge_chain.new_difficulty
            if block.finished_sub_slots[0].challenge_chain.new_sub_slot_iters is not None:
                sub_slot_iters = block.finished_sub_slots[0].challenge_chain.new_sub_slot_iters
        overflow = is_overflow_block(constants, block.reward_chain_block.signage_point_index)
        challenge = get_block_challenge(constants, block, BlockCache(recent_blocks), prev_b is None, overflow, False)
        if block.reward_chain_block.challenge_chain_sp_vdf is None:
            cc_sp_hash: bytes32 = challenge
        else:
            cc_sp_hash = block.reward_chain_block.challenge_chain_sp_vdf.output.get_hash()
        q_str: Optional[bytes32] = verify_and_get_quality_string(
            block.reward_chain_block.proof_of_space, constants, challenge, cc_sp_hash, height=block.height
        )
        if q_str is None:
            return [PreValidationResult(uint16(Err.INVALID_POSPACE.value), None, None, False, uint32(0))]

        required_iters: uint64 = calculate_iterations_quality(
            constants.DIFFICULTY_CONSTANT_FACTOR,
            q_str,
            block.reward_chain_block.proof_of_space.size,
            difficulty,
            cc_sp_hash,
        )

        try:
            block_rec = block_to_block_record(
                constants,
                blockchain,
                required_iters,
                block,
                sub_slot_iters=sub_slot_iters,
                prev_ses_block=prev_ses_block,
            )
        except ValueError:
            return [PreValidationResult(uint16(Err.INVALID_SUB_EPOCH_SUMMARY.value), None, None, False, uint32(0))]

        if block_rec.sub_epoch_summary_included is not None and wp_summaries is not None:
            next_ses = wp_summaries[int(block.height / constants.SUB_EPOCH_BLOCKS) - 1]
            if not block_rec.sub_epoch_summary_included.get_hash() == next_ses.get_hash():
                log.error("sub_epoch_summary does not match wp sub_epoch_summary list")
                return [PreValidationResult(uint16(Err.INVALID_SUB_EPOCH_SUMMARY.value), None, None, False, uint32(0))]

        recent_blocks[block_rec.header_hash] = block_rec
        blockchain.add_extra_block(block, block_rec)  # Temporarily add block to chain
        prev_b = block_rec
        diff_ssis.append((difficulty, sub_slot_iters))
        prev_ses_block_list.append(prev_ses_block)
        if block_rec.sub_epoch_summary_included is not None:
            prev_ses_block = block_rec

    conditions_pickled = {}
    for k, v in block_height_conds_map.items():
        conditions_pickled[k] = bytes(v)
    futures = []
    # Pool of workers to validate blocks concurrently
    recent_blocks_bytes = {bytes(k): bytes(v) for k, v in recent_blocks.items()}  # convert to bytes

    batch_size = 4
    for i in range(0, len(blocks), batch_size):
        end_i = min(i + batch_size, len(blocks))
        blocks_to_validate = blocks[i:end_i]
        b_pickled: List[bytes] = []
        previous_generators: List[Optional[List[bytes]]] = []
        for block in blocks_to_validate:
            assert isinstance(block, FullBlock)
            b_pickled.append(bytes(block))
            try:
                block_generator: Optional[BlockGenerator] = await get_block_generator(
                    blockchain.lookup_block_generators, block
                )
            except ValueError:
                return [
                    PreValidationResult(
                        uint16(Err.FAILED_GETTING_GENERATOR_MULTIPROCESSING.value), None, None, False, uint32(0)
                    )
                ]
            if block_generator is not None:
                previous_generators.append(block_generator.generator_refs)
            else:
                previous_generators.append(None)

        ses_blocks_bytes_list: List[Optional[bytes]] = []
        for j in range(i, end_i):
            ses_block_rec = prev_ses_block_list[j]
            if ses_block_rec is None:
                ses_blocks_bytes_list.append(None)
            else:
                ses_blocks_bytes_list.append(bytes(ses_block_rec))

        futures.append(
            asyncio.get_running_loop().run_in_executor(
                pool,
                batch_pre_validate_blocks,
                constants,
                recent_blocks_bytes,
                b_pickled,
                previous_generators,
                conditions_pickled,
                [diff_ssis[j][0] for j in range(i, end_i)],
                [diff_ssis[j][1] for j in range(i, end_i)],
                validate_signatures,
                ses_blocks_bytes_list,
            )
        )
    # Collect all results into one flat list
    return [
        PreValidationResult.from_bytes(result)
        for batch_result in (await asyncio.gather(*futures))
        for result in batch_result
    ]


def _run_generator(
    constants: ConsensusConstants,
    unfinished_block_bytes: bytes,
    block_generator_bytes: bytes,
    height: uint32,
) -> Optional[bytes]:
    """
    Runs the KLVM generator from bytes inputs. This is meant to be called under a ProcessPoolExecutor, in order to
    validate the heavy parts of a block (klvm program) in a different process.
    """
    try:
        unfinished_block: UnfinishedBlock = UnfinishedBlock.from_bytes(unfinished_block_bytes)
        assert unfinished_block.transactions_info is not None
        block_generator: BlockGenerator = BlockGenerator.from_bytes(block_generator_bytes)
        assert block_generator.program == unfinished_block.transactions_generator
        npc_result: NPCResult = get_name_puzzle_conditions(
            block_generator,
            min(constants.MAX_BLOCK_COST_KLVM, unfinished_block.transactions_info.cost),
            mempool_mode=False,
            height=height,
            constants=constants,
        )
        return bytes(npc_result)
    except ValidationError as e:
        return bytes(NPCResult(uint16(e.code.value), None))
    except Exception:
        return bytes(NPCResult(uint16(Err.UNKNOWN.value), None))
